import json
import os
import subprocess

def dag2vueflow(dag_file: str, workflow_uuid: str, user_id: str):
    """将 DOT 格式的 DAG 转换为 VueFlow 兼容的 JSON 格式。

    参数:
        dag_file (str): DOT 文件路径
        workflow_uuid (str): 工作流的 UUID
        user_id (str): 用户 ID

    返回:
        dict: 解析后的 JSON DAG 数据
    """
    # 定义 dot 可执行路径
    dot_bin = "dot"

    # 目标 JSON 文件路径
    output_dir = f"/ProjectM/users/{user_id}/workflows/{workflow_uuid}"
    os.makedirs(output_dir, exist_ok=True)  # 确保目录存在
    output_json = os.path.join(output_dir, "dag.json")

    # 执行 Graphviz dot 转换
    try:
        subprocess.run(
            [dot_bin, "-Tdot_json", dag_file, "-o", output_json],
            check=True,  # 发生错误时抛出异常
            capture_output=True,  # 处理错误输出
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Graphviz 解析失败: {e.stderr}") from e

    # 读取 JSON 文件
    with open(output_json, "r", encoding="utf-8") as f:
        return json.load(f)
