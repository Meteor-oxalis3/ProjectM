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

重要规则:
- 只能使用下面"文件列表"中实际存在的 FASTQ 文件，严禁编造或使用 /ProjectM/raw_data/ 等测试路径
- ID: 样本唯一标识符，从文件名中提取有意义的样本名 (如 SRR5947819 → sample1)
- fastq1/fastq2: 必须使用文件列表中给出的完整路径
- group: 样本分组 (如 UC、nonIBD、case、control)，需根据用户描述或文件名推断
- 严禁出现 /ProjectM/raw_data/ 路径
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
