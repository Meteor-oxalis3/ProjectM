import os
import zipfile
import io
from flask import send_file

# 纯中间产物目录（完全不打包）
SKIP_DIRS = {
    '00_raw_data',
    '04_bwa_host', '05_bwa_phix',
    '06_kraken2', '07_kreport2mpa',
    '10_megahit', '11_prodigal', '12_metaquast',
    '14_megahit_merged', '15_megahit_group', '24_prokka',
}

# 允许打包的文件扩展名（大小写不敏感）
ALLOW_EXTS = {'.pdf', '.png', '.html', '.json', '.tsv', '.csv', '.res', '.txt', '.zip', '.gff', '.faa', '.fna'}

def results_dowload(session, jsonify, request):
    data = request.get_json()
    workflow_uuid = data.get("filename")
    user_id = session.get('user_id')

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
        return jsonify({"error": "Output directory not found"}), 404

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(output_path):
            rel_dir = os.path.relpath(root, output_path)
            top_dir = rel_dir.split(os.sep)[0] if rel_dir != '.' else ''
            if top_dir in SKIP_DIRS:
                continue
            for fn in files:
                if not any(fn.lower().endswith(ext) for ext in ALLOW_EXTS):
                    continue
                abs_path = os.path.join(root, fn)
                rel_path = os.path.relpath(abs_path, output_path)
                zf.write(abs_path, rel_path)
    buf.seek(0)

    return send_file(buf, mimetype='application/zip',
                     as_attachment=True,
                     download_name=f"{workflow_uuid}_results.zip")
