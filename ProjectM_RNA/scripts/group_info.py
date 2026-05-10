#!/micromamba/envs/ProjectM/bin/python
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="为相对丰度矩阵添加分组行")
parser.add_argument("-i", "--input", required=True, help="相对丰度矩阵TSV文件路径，样本名为列名")
parser.add_argument("-g", "--group_csv", required=True, help="分组信息CSV文件，必须含列 'ID' 和 'group'")
parser.add_argument("-o", "--output", required=True, help="输出文件路径")

args = parser.parse_args()

# 读取矩阵
df = pd.read_csv(args.input, sep='\t', index_col=0)

# 读取分组信息
group_df = pd.read_csv(args.group_csv)
group_dict = dict(zip(group_df['ID'], group_df['group']))

# 组信息，顺序对应df列
group_row = [group_dict.get(sample, "No_Group") for sample in df.columns]

with open(args.output, "w") as f:
    # 写入组信息行
    f.write("group\t" + "\t".join(group_row) + "\n")
    # 写入原数据（包括列名和索引）
    df.to_csv(f, sep='\t', index=True)