import os
import time

def user_upload_files(session, User, jsonify):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Please login first."}), 401

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success": False, "message": "User not found."}), 404

    user_dir = os.path.join('/ProjectM/users', str(user.id), 'data')
    if not os.path.exists(user_dir):
        return jsonify({"success": True, "files": []}), 200

    files = []
    for idx, file in enumerate(os.listdir(user_dir)):
        file_path = os.path.join(user_dir, file)
        if os.path.isfile(file_path):
            files.append({
                "id": idx,  # 添加文件 ID
                "name": file,
                "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))  # 格式化时间
            })

    return jsonify({"success": True, "files": files}), 200
