#!/micromamba/envs/ProjectM/bin/python
import pandas as pd
import argparse

# ---------- 解析命令行参数 ----------
parser = argparse.ArgumentParser(description="计算相对丰度矩阵")
parser.add_argument('-i', '--input', required=True, help='输入的绝对丰度矩阵（TSV 格式）')
parser.add_argument('-o', '--output', required=True, help='输出的相对丰度矩阵文件名（TSV 格式）')

args = parser.parse_args()

# ---------- 读取绝对丰度矩阵 ----------
df_absolute = pd.read_csv(args.input, sep='\t', index_col=0)

# ---------- 计算相对丰度 ----------
df_relative = df_absolute.div(df_absolute.sum(axis=0), axis=1)
df_relative = df_relative.round(6)

# ---------- 保存结果 ----------
df_relative.to_csv(args.output, sep='\t')