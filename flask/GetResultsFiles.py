import os
import uuid
import time

def user_results(session, User, jsonify, WorkflowAlias, db):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Please login first."}), 401

    user = User.query.filter_by(id=uuid.UUID(user_id)).first()
    if not user:
        return jsonify({"success": False, "message": "User not found."}), 404

    user_dir = os.path.join('/ProjectM/users', str(user.id), 'workflows')
    if not os.path.exists(user_dir):
        return jsonify({"success": True, "folders": []}), 200

    folders = []
    for idx, folder in enumerate(os.listdir(user_dir)):
        folder_path = os.path.join(user_dir, folder)
        result_path = os.path.join(folder_path, 'output', 'results.zip')
        folder_alias =  WorkflowAlias.query.filter_by(uuid=folder).first()
        
        if os.path.isdir(folder_path) and os.path.exists(result_path):
            folders.append({
                "id": idx,
                "name": folder,
                "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(folder_path))),
                "alias": folder_alias.alias if folder_alias else "无"
            })

    return jsonify({"success": True, "folders": folders}), 200
