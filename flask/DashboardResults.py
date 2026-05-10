from GetResultsFiles import user_results
from GetUserWorkflows import user_workflows
import json

def dashboard_results(session, User, jsonify, WorkflowAlias, db):
    json_user_results, _ = user_results(session, User, jsonify, WorkflowAlias, db)
    json_user_workflows, _ = user_workflows(session, User, jsonify, WorkflowAlias, db)

    json_user_results = json_user_results.get_json()
    json_user_workflows = json_user_workflows.get_json()

    #合并两个json，并集显示布尔值，两个json都有的key值，布尔值显示为True
    # 将 name 作为唯一标识，构建字典
    folders1 = {folder["name"]: folder for folder in json_user_results["folders"]}
    folders2 = {folder["name"]: folder for folder in json_user_workflows["folders"]}

    # 获取所有唯一 name
    all_names = set(folders1.keys()) | set(folders2.keys())

    # 合并数据并添加 in_both 标记
    merged_folders = []
    for name in all_names:
        folder = folders1.get(name, folders2.get(name)).copy()  # 复制数据，避免修改原数据
        folder["completed"] = name in folders1 and name in folders2
        merged_folders.append(folder)

        # 生成合并后的 JSON
        merged_json = {"folders": merged_folders, "success": True}

        # 输出合并结果
        # print(json.dumps(merged_json, indent=2, ensure_ascii=False))

    return jsonify(merged_json), 200