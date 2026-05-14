import os
import uuid
import time
os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

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
        output_dir = os.path.join(folder_path, 'output')
        snakemake_log = os.path.join(folder_path, 'snakemake.log')
        folder_alias = WorkflowAlias.query.filter_by(uuid=folder).first()

        # 回退：旧版管道输出路径
        if not os.path.isdir(output_dir) or not os.listdir(output_dir):
            for fallback in [
                f"/ProjectM/ProjectM_DNA/output/{folder}",
                f"/ProjectM/ProjectM_RNA/output/{folder}",
            ]:
                if os.path.isdir(fallback) and os.listdir(fallback):
                    output_dir = fallback
                    break
        if not os.path.isdir(output_dir) or not os.listdir(output_dir):
            continue

        # 判断完成状态
        status = 'running'
        if os.path.exists(snakemake_log):
            with open(snakemake_log, 'r') as f:
                log_content = f.read()
            if 'WorkflowError' in log_content or \
               'At least one job did not complete successfully' in log_content:
                status = 'failed'
            elif 'Complete log' in log_content or \
                 'steps (100%) done' in log_content:
                status = 'completed'
            else:
                status = 'running'  # 有输出但还在跑

        folders.append({
            "id": idx,
            "name": folder,
            "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(folder_path))),
            "alias": folder_alias.alias if folder_alias else "无",
            "status": status
        })

    return jsonify({"success": True, "folders": folders}), 200
