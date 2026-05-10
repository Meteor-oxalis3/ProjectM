from AI2yaml import ai_to_yaml
import uuid
import re
import os
import subprocess

# Snakemake 管道路径映射
PIPELINE_SNAKEFILES = {
    "metagenomics":        "/ProjectM/ProjectM_DNA/snakemake/Snakefile",
    "metatranscriptomics": "/ProjectM/ProjectM_RNA/snakemake/Snakefile",
}
SNK_BIN = "/micromamba/envs/ProjectM/bin/snakemake"


def receive_files(request, jsonify, WorkflowAlias, db):
    data = request.get_json()

    user_id = data.get('user_id')
    workflow_alias = data.get('workflow_alias', 'unnamed').replace(" ", "_")
    pipeline_type = data.get('pipeline_type', 'metagenomics')
    workflow_uuid = str(uuid.uuid4())

    # 调用 AI 生成样本表
    ai_result = ai_to_yaml(
        user_id,
        data.get('files'),
        data.get('input_text'),
        pipeline_type=pipeline_type
    )
    print(ai_result)

    # 存储到数据库
    new_workflow = WorkflowAlias(user_id=user_id, alias=workflow_alias, uuid=workflow_uuid)
    db.session.add(new_workflow)
    db.session.commit()

    # 创建流程工作目录
    workflow_dir = os.path.join('/ProjectM/users', str(user_id), 'workflows', workflow_uuid)
    os.makedirs(workflow_dir, exist_ok=True)

    # 提取 AI 返回的 CSV 样本表 (```csv 代码块或纯 CSV)
    csv_pattern = r"```(?:csv)?\n(.*?)\n```"
    matches = re.findall(csv_pattern, ai_result, re.DOTALL)
    if matches:
        csv_content = matches[0].strip()
    else:
        # 尝试直接作为 CSV 使用 (无代码块包裹)
        csv_content = ai_result.strip()
        if not csv_content.startswith("ID,"):
            # 最后兜底：尝试按老 YAML 格式解析再转换
            yaml_pattern = r"```yaml\n(.*?)\n```"
            yaml_matches = re.findall(yaml_pattern, ai_result, re.DOTALL)
            if yaml_matches:
                import yaml as yaml_lib
                yaml_data = yaml_lib.safe_load(yaml_matches[0])
                # Convert YAML samples to CSV
                lines = ["ID,fastq1,fastq2,group"]
                for group, samples in yaml_data.get("samples", {}).items():
                    for sample_id, paths in samples.items():
                        lines.append(f"{sample_id},{paths['fastq1']},{paths['fastq2']},{group}")
                csv_content = "\n".join(lines)
            else:
                return jsonify(success=False, error="AI did not return valid sample table")

    # 写入样本表 CSV
    metadata_csv = os.path.join(workflow_dir, 'samples.csv')
    with open(metadata_csv, 'w') as f:
        f.write(csv_content)
    print(f"Sample table written: {metadata_csv}")

    if not os.path.exists(metadata_csv) or os.path.getsize(metadata_csv) < 10:
        return jsonify(success=False, error="Sample table empty or not created")

    # 选择管道
    snakefile_path = PIPELINE_SNAKEFILES.get(pipeline_type, PIPELINE_SNAKEFILES["metagenomics"])

    os.chdir(workflow_dir)

    # Snakemake 配置参数
    snk_config = [
        SNK_BIN, "-s", snakefile_path,
        "--config",
        f"ref=hg38",
        f"uuid={workflow_uuid}",
        f"metadata={metadata_csv}",
    ]

    # 生成 DAG
    with open("dag.dot", "w") as dag_file:
        proc = subprocess.Popen(
            [SNK_BIN, "--dag", "-s", snakefile_path, "--quiet"] +
            [f"--config", f"ref=hg38", f"uuid={workflow_uuid}", f"metadata={metadata_csv}"],
            stdout=dag_file
        )
        proc.wait()

    if os.path.getsize("dag.dot") == 0:
        return jsonify(success=False, error="DAG generation failed")

    # 启动 Snakemake
    with open("snakemake.log", "w") as logfile:
        subprocess.Popen(
            snk_config,
            stdout=logfile, stderr=subprocess.STDOUT
        )

    os.chdir("/ProjectM")
    return jsonify(success=True, uuid=workflow_uuid)
