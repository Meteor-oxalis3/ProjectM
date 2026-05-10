import os
import uuid

def delete_user_files(User, session, request, jsonify):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Please login first."}), 401

    user = User.query.filter_by(id=uuid.UUID(user_id)).first()
    if not user:
        return jsonify({"success": False, "message": "User not found."}), 404

    user_dir = os.path.join('/ProjectM/users', str(user_id), 'data')
    if not user_dir or not os.path.exists(user_dir):
        return jsonify({"success": False, "message": "User directory not found."}), 404

    data = request.get_json()
    file_names = data.get("files", [])

    if not file_names:
        return jsonify({"success": False, "message": "No files provided."}), 400

    deleted_files = []
    failed_files = []

    # print(f"Deleting files for user {user_id}:", file_names)
    for file_name in file_names:
        file_path = os.path.join(user_dir, file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_files.append(file_name)
            except Exception as e:
                print(f"Failed to delete file {file_name}: {e}")
                failed_files.append(file_name)
        else:
            print(f"File not found: {file_name}")
            failed_files.append(file_name)
        
    return jsonify({
        "success": bool(deleted_files),  # 只有成功删除文件才返回 True
        "deleted": deleted_files,
        "failed": failed_files
    }), 200
