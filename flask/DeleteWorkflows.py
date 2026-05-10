import os
import shutil
import uuid

def delete_user_workflows(User, session, request, jsonify, WorkflowAlias, db):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Please login first."}), 401

    user = User.query.filter_by(id=uuid.UUID(user_id)).first()
    if not user:
        return jsonify({"success": False, "message": "User not found."}), 404

    user_dir = os.path.join('/ProjectM/users', str(user_id), 'workflows')
    if not os.path.exists(user_dir):
        return jsonify({"success": False, "message": "User directory not found."}), 404

    data = request.get_json()
    folder_names = data.get("folders", [])

    if not folder_names:
        return jsonify({"success": False, "message": "No folders provided."}), 400

    deleted_folders = []
    failed_folders = []

    for folder_name in folder_names:
        folder_path = os.path.join(user_dir, folder_name)
        deleted = False
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            try:
                shutil.rmtree(folder_path)
                deleted = True
            except Exception as e:
                print(f"Failed to delete folder {folder_name}: {e}")

        # 同步删除数据库中的 WorkflowAlias 记录
        try:
            alias = WorkflowAlias.query.filter_by(uuid=folder_name).first()
            if alias:
                db.session.delete(alias)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to delete DB record for {folder_name}: {e}")

        if deleted:
            deleted_folders.append(folder_name)
        else:
            failed_folders.append(folder_name)

    return jsonify({
        "success": bool(deleted_folders),
        "deleted": deleted_folders,
        "failed": failed_folders
    }), 200
