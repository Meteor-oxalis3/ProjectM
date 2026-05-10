import os

def preview_results(jsonify, request, session):
    data = request.get_json()
    user_id = session.get("user_id")
    workflow_uuid = data.get("workflow_uuid")

    if not user_id or not workflow_uuid:
        return jsonify({"success": False, "message": "Invalid user or workflow UUID"}), 400

    results_path = os.path.join('/ProjectM/users/', str(user_id), 'workflows', str(workflow_uuid), 'output', 'results')

    if not os.path.isdir(results_path):  # 确保是目录
        return jsonify({"success": False, "message": "Results directory not found"}), 404

    try:
        # 列出目录下的有效文件（排除隐藏文件）
        results_files_list = [f for f in os.listdir(results_path) if not f.startswith(".")]

        # 动态获取 `base_url`
        base_url = 'https://preview.drcan.org'

        # 构造完整 URL
        result_files = [
            {"filename": filename, "url": f"{base_url}/{user_id}/workflows/{workflow_uuid}/output/results/{filename}"}
            for filename in results_files_list
        ]

        return jsonify({"success": True, "files": result_files})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
