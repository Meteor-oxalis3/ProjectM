from DagStatus import get_dag_status
from DagNetWorkX import get_dag_current_and_waiting
from Dag2JSON import dag2vueflow
import os
import glob

# 获取DAG图数据
def workflow_data(jsonify, session, request):
    user_id = session.get('user_id')
    workflow_uuid = request.get_json().get('workflow_uuid')

    dot_file = os.path.join('/ProjectM/users', str(user_id), "workflows", str(workflow_uuid), 'dag.dot')
    with open('/tmp/owd_debug.log', 'a') as dlog:
        dlog.write(f"user_id={user_id} wf={workflow_uuid} dot={dot_file} exists={os.path.exists(dot_file)}\n")
    if not os.path.exists(dot_file):
        return jsonify({"error": "DAG not found", "completed": {}, "ongoing": [], "unfinished": []})

    # 查找 Snakemake 日志（.snakemake/ 在 workflow 根目录，output 在 output/ 子目录）
    workflow_base = os.path.join('/ProjectM/users', str(user_id), 'workflows', str(workflow_uuid))
    log_file = None
    for search_dir in [
        os.path.join(workflow_base, '.snakemake', 'log'),
        os.path.join(workflow_base, 'output', '.snakemake', 'log'),
        os.path.join('/ProjectM/ProjectM_DNA/output', str(workflow_uuid), '.snakemake', 'log'),
        os.path.join('/ProjectM/ProjectM_RNA/output', str(workflow_uuid), '.snakemake', 'log'),
    ]:
        logs = glob.glob(os.path.join(search_dir, '*.snakemake.log'))
        if logs:
            log_file = sorted(logs)[-1]  # 取最新的
            break

    if not log_file:
        return jsonify({"error": "Log not found (pipeline may not have started yet)", "completed": {}, "ongoing": [], "unfinished": []})

    try:
        dot_result = dag2vueflow(dot_file, workflow_uuid, user_id)
        log_result = get_dag_status(log_file)
        ongoing, unfinished = get_dag_current_and_waiting(dot_file, log_file)
        return jsonify({
            "dag": dot_result,
            "completed": log_result,
            "ongoing": ongoing,
            "unfinished": unfinished
        })
    except Exception as e:
        with open('/tmp/owd_debug.log', 'a') as dlog:
            import traceback
            dlog.write(f"DAG processing error: {e}\n{traceback.format_exc()}\n")
        return jsonify({"error": f"Processing error: {str(e)}", "completed": {}, "ongoing": [], "unfinished": []})