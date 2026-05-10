import networkx as nx
import re
from DagStatus import get_dag_status

def parse_dot_edges(file_path):
    """
    从 DOT 语言文本中提取边信息。

    参数：
    dot_text (str): DOT 文件的内容。

    返回：
    list[tuple]: 提取的边 (起点, 终点) 列表。
    """
    with open(file_path, "r", encoding="utf-8") as file:
        dot_text = file.read()
    pattern = re.compile(r'(\d+)\s*->\s*(\d+)')
    edges = [(int(a), int(b)) for a, b in pattern.findall(dot_text)]
    return edges

def get_dag_current_and_waiting(dot_file, log_file):
    # 任务依赖关系
    edges = parse_dot_edges(dot_file)

    # 已完成事件
    completed_str = get_dag_status(log_file)
    # print("completed_str: ", completed_str)
    completed = set()
    if completed_str.strip():
        completed = set(map(int, [x for x in completed_str.split(',') if x.strip()]))

    # 构建有向图
    G = nx.DiGraph()
    G.add_edges_from(edges)

    # 找到正在进行的事件（所有前置事件已完成但自身未完成）
    ongoing = [node for node in G.nodes if node not in completed and all(parent in completed for parent in G.predecessors(node))]

    # 找到未完成的事件
    unfinished = [node for node in G.nodes if node not in completed]
    # print("正在进行的事件:", ongoing)
    # print("未完成的事件:", unfinished)

    ongoing = ','.join(map(str, ongoing))
    unfinished = ','.join(map(str, unfinished))

    return ongoing, unfinished