# 从log文件获取当前进展，返回给前端
from CleanLog import completed_work

def get_dag_status(log_file):
    result = completed_work(log_file)
    return result