import os
import time

def user_workflows(session, User, jsonify, WorkflowAlias, db):
    # 获取当前用户的 user_id
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Please login first."}), 401

    # 查询用户是否存在
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success": False, "message": "User not found."}), 404

    # 构建用户的工作流目录路径
    user_dir = os.path.join('/ProjectM/users', str(user.id), 'workflows')
    if not os.path.exists(user_dir):
        return jsonify({"success": True, "folders": []}), 200

    # 获取所有文件夹信息
    folders = []
    for idx, folder in enumerate(os.listdir(user_dir)):
        folder_path = os.path.join(user_dir, folder)
        folder_alias =  WorkflowAlias.query.filter_by(uuid=folder).first()
        if os.path.isdir(folder_path):
            folders.append({
                "id": idx,  # 文件夹 ID
                "name": folder,
                "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(folder_path))),  # 格式化时间
                "alias": folder_alias.alias if folder_alias else "无"
            })

    return jsonify({"success": True, "folders": folders}), 200