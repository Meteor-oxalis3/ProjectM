import os
import glob

SKIP_DIRS = {
    '00_raw_data',
    '04_bwa_host', '05_bwa_phix',
    '06_kraken2', '07_kreport2mpa',
    '10_megahit', '11_prodigal', '12_metaquast',
    '14_megahit_merged', '15_megahit_group', '24_prokka',
}

def preview_results(jsonify, request, session):
    data = request.get_json()
    user_id = session.get("user_id")
    workflow_uuid = data.get("workflow_uuid")

    if not user_id or not workflow_uuid:
        return jsonify({"success": False, "message": "Invalid user or workflow UUID"}), 400

    # 查找 output 目录（用户目录优先，管道默认路径回退）
    output_path = os.path.join('/ProjectM/users', str(user_id), 'workflows', str(workflow_uuid), 'output')
    if not os.path.isdir(output_path):
        for fallback in [
            f"/ProjectM/ProjectM_DNA/output/{workflow_uuid}",
            f"/ProjectM/ProjectM_RNA/output/{workflow_uuid}",
        ]:
            if os.path.isdir(fallback):
                output_path = fallback
                break

    if not os.path.isdir(output_path):
        return jsonify({"success": False, "message": "Output directory not found"}), 404

    try:
        # 扫描所有 PDF / PNG / HTML 结果文件
        patterns = ['**/*.pdf', '**/*.png', '**/*.html']
        result_files = []
        for pat in patterns:
            for f in glob.glob(os.path.join(output_path, pat), recursive=True):
                rel = os.path.relpath(f, output_path)
                top_dir = rel.split(os.sep)[0]
                if top_dir in SKIP_DIRS:
                    continue
                result_files.append({
                    "filename": rel,
                    "url": f"/api/results_file?user_id={user_id}&workflow_uuid={workflow_uuid}&file={rel}",
                    "size": os.path.getsize(f),
                    "mtime": os.path.getmtime(f)
                })

        # 按修改时间降序排列
        result_files.sort(key=lambda x: x['mtime'], reverse=True)

        return jsonify({"success": True, "files": result_files})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
