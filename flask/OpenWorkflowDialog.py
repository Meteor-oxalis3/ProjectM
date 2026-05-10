from DagStatus import get_dag_status
from DagNetWorkX import get_dag_current_and_waiting
from Dag2JSON import dag2vueflow
import os
import glob

# 获取DAG图数据
def workflow_data(jsonify, session, request):
    user_id = session.get('user_id')
    workflow_uuid = request.get_json().get('workflow_uuid')
    # print("workflow_uuid: ", workflow_uuid)
    dot_file = os.path.join('/ProjectM/users', str(user_id), "workflows", str(workflow_uuid), 'dag.dot')
    log_dir = os.path.join('/ProjectM/users', str(user_id), 'workflows', str(workflow_uuid), 'output', '.snakemake', 'log')
    log_file = glob.glob(os.path.join(log_dir, '*.snakemake.log'))[0]
    # print("log_file: ", log_file)

    dot_result = dag2vueflow(dot_file, workflow_uuid, user_id)
    log_result = get_dag_status(log_file)
    # print("log_result: ", log_result)
    ongoing, unfinished = get_dag_current_and_waiting(dot_file, log_file)
    return jsonify({
        "dag": dot_result,
        "completed": log_result,
        "ongoing": ongoing,
        "unfinished": unfinished
    })