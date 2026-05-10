import os
from flask import send_file

def results_dowload(session, jsonify, request):
    data = request.get_json()
    workflow_uuid = data.get("filename")
    user_id = session.get('user_id')

    results_tar = os.path.join('/ProjectM/users', str(user_id), 'workflows', str(workflow_uuid), 'output', 'results.zip')

    # 确保文件存在
    if not os.path.exists(results_tar):
        return jsonify({"error": "File not found"}), 404

    return send_file(results_tar, as_attachment=True, download_name=f"{workflow_uuid}_results.zip, conditional=True")