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
SNK_BIN = "micromamba"
SNK_ENV = "ProjectM"


def receive_files(request, jsonify, WorkflowAlias, db):
    data = request.get_json()

    user_id = data.get('user_id')
    workflow_alias = data.get('workflow_alias', 'unnamed').replace(" ", "_")
    pipeline_type = data.get('pipeline_type', 'metagenomics')
    workflow_uuid = str(uuid.uuid4())

    # 构建用户已上传文件的完整路径列表
    user_data_dir = os.path.join('/ProjectM/users', str(user_id), 'data')
    user_files = []
    if os.path.isdir(user_data_dir):
        user_files = [os.path.join(user_data_dir, f) for f in os.listdir(user_data_dir)
                      if os.path.isfile(os.path.join(user_data_dir, f))]
    # 同时提取纯文件名列表供 AI 参考
    user_file_names = [os.path.basename(p) for p in user_files]

    # 调用 AI 生成样本表
    try:
        ai_result = ai_to_yaml(
            user_id,
            user_file_names,  # 只传文件名，AI 用标准路径格式拼接
            data.get('input_text'),
            pipeline_type=pipeline_type
        )
    except Exception as e:
        with open('/tmp/receive_debug.log', 'a') as dlog:
            dlog.write(f"AI error: {e}\n")
        return jsonify(success=False, error=f"AI调用失败: {str(e)}"), 500

    with open('/tmp/receive_debug.log', 'a') as dlog:
        dlog.write(f"=== AI RESULT ===\n{ai_result}\n=== END ===\n")

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

    # 用用户实际文件路径修正 AI 可能编造的路径
    name_to_path = {os.path.basename(p): p for p in user_files}
    corrected_lines = []
    for line in csv_content.strip().split('\n'):
        if line.startswith('ID,'):
            corrected_lines.append(line)
            continue
        parts = line.split(',')
        if len(parts) >= 4:
            for i in [1, 2]:  # fastq1, fastq2 columns
                fname = os.path.basename(parts[i])
                if fname in name_to_path:
                    parts[i] = name_to_path[fname]
        corrected_lines.append(','.join(parts))
    csv_content = '\n'.join(corrected_lines)

    # 重新写入修正后的 CSV
    with open(metadata_csv, 'w') as f:
        f.write(csv_content)

    # 校验 CSV 中的 FASTQ 路径是否存在
    import csv as csv_module
    invalid_paths = []
    with open(metadata_csv, 'r') as f:
        reader = csv_module.DictReader(f)
        for row in reader:
            for col in ['fastq1', 'fastq2']:
                p = row.get(col, '')
                if not os.path.exists(p):
                    invalid_paths.append(p)
    if invalid_paths:
        with open('/tmp/receive_debug.log', 'a') as dlog:
            dlog.write(f"Invalid paths: {invalid_paths}\n")
            dlog.write(f"user_files: {user_files}\n")
        return jsonify(success=False,
            error=f"FASTQ files not found: {invalid_paths[:3]}... "
                  f"请确保已在'上传与运行'页面上传所有 FASTQ 文件"), 400

    # 选择管道
    snakefile_path = PIPELINE_SNAKEFILES.get(pipeline_type, PIPELINE_SNAKEFILES["metagenomics"])

    os.chdir(workflow_dir)

    output_dir = os.path.join(workflow_dir, 'output')

    # Snakemake 配置参数 (通过 micromamba run 确保工具在 PATH 中)
    snk_config = [
        SNK_BIN, "run", "-n", SNK_ENV, "snakemake",
        "-s", snakefile_path,
        "--cores", "30",
        "--config",
        f"ref=hg38",
        f"uuid={workflow_uuid}",
        f"metadata={metadata_csv}",
        f"output_dir={output_dir}",
    ]

    # 生成 DAG
    with open("dag.dot", "w") as dag_file:
        proc = subprocess.Popen(
            [SNK_BIN, "run", "-n", SNK_ENV, "snakemake",
             "--dag", "-s", snakefile_path, "--quiet",
             "--cores", "1"] +
            [f"--config", f"ref=hg38", f"uuid={workflow_uuid}", f"metadata={metadata_csv}", f"output_dir={output_dir}"],
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
