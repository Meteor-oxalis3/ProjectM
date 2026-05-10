from openai import OpenAI
import os

def ai_to_yaml(user_id, files, chat_content, pipeline_type="metagenomics"):
    client = OpenAI(
        base_url="https://api.deepseek.com/",
        api_key=os.environ.get('OPENAI_API_KEY')
    )

    pipeline_desc = {
        "metagenomics": "宏基因组 (DNA) — FastQC/fastp质控 → 去宿主/PhiX → Kraken2物种注释 → LEfSe差异分析 → MEGAHIT组装 → Prodigal基因预测 → Prokka功能注释 → 多样性可视化",
        "metatranscriptomics": "宏转录组 (RNA) — FastQC/fastp质控 → 去宿主/PhiX → SortMeRNA去rRNA → Kraken2物种注释 → LEfSe差异分析 → MEGAHIT组装 → Prodigal基因预测 → CD-HIT去冗余 → eggNOG-mapper功能注释 → DESeq2 KO差异分析 → 多样性可视化",
    }

    messages = [
        {
            "role": "system",
            "content": f'''你是一个生物信息学助手，帮助用户生成宏组学分析所需的样本信息表。
选择的管道类型: {pipeline_type} — {pipeline_desc.get(pipeline_type, "")}

请将用户提供的 FASTQ 文件按样本配对，生成以下 CSV 格式（逗号分隔），无需其他内容:
ID,fastq1,fastq2,group

规则:
- ID: 样本唯一标识符 (如 sample1_UC)
- fastq1/fastq2: 双端 FASTQ 文件的完整路径
- group: 样本分组 (如 UC、nonIBD、case、control)，需根据用户描述或文件名推断
- 路径格式: /ProjectM/users/(用户UUID)/data/文件名.fastq.gz

示例输出:
ID,fastq1,fastq2,group
sample1_UC,/ProjectM/users/abc-123/data/SRR001_1.fastq.gz,/ProjectM/users/abc-123/data/SRR001_2.fastq.gz,UC
sample2_Control,/ProjectM/users/abc-123/data/SRR002_1.fastq.gz,/ProjectM/users/abc-123/data/SRR002_2.fastq.gz,Control
            '''
        },
        {
            "role": "user",
            "content": f"用户说:{chat_content}, 文件列表:{files}, 用户UUID:{user_id}, 管道类型:{pipeline_type}"
        }
    ]

    completion = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )

    return completion.choices[0].message.content
