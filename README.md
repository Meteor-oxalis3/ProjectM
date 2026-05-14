# ProjectM — 面向宏基因组与宏转录组的整合分析及可视化平台

## 项目简介

ProjectM 是一个宏基因组与宏转录组整合分析及可视化平台。平台基于 Snakemake 工作流引擎构建双组学自动化分析管道，集成 20+ 主流生物信息学工具，覆盖从原始 FASTQ 数据到统计图表的全流程闭环分析。Web 前端基于 Vue 3 + Flask 实现用户认证、AI 智能编排、实时 DAG 流程监控与多维度结果可视化，大幅降低了非生物信息学专业人员的使用门槛。

## 技术架构

```
用户交互层 (Vue 3 + Vuetify + VueFlow)
    ↕ REST API / WebSocket
服务接口层 (Flask + Socket.IO · micromamba: flask_backend)
    ↕ subprocess / micromamba run
计算引擎层 (Snakemake v9.16 · micromamba: ProjectM)
    ├── 宏基因组管道 (DNA): 25 条规则 · 20+ 工具 · 113 任务节点
    └── 宏转录组管道 (RNA): 23 条规则 · 22+ 工具
    ↕ 文件系统 I/O
数据存储层 (用户隔离 · 共享参考库 · MariaDB)
```

## 目录结构

```
/ProjectM/
├── ProjectM_DNA/                # 宏基因组管道
│   ├── snakemake/
│   │   ├── Snakefile            # 工作流入口
│   │   └── rules/               # 25 条 Snakemake 规则 (*.smk)
│   └── scripts/                 # 分析可视化脚本 (Python/R)
├── ProjectM_RNA/                # 宏转录组管道
│   ├── snakemake/
│   │   ├── Snakefile
│   │   └── rules/               # 23 条规则
│   └── scripts/                 # 含 DESeq2 KO 分析 (R)
├── flask/                       # Flask 后端
│   ├── app.py                   # 主入口, API 路由
│   ├── ReceiveTask.py           # AI 编排 + Snakemake 调度
│   ├── AI2yaml.py               # DeepSeek LLM 样本表生成
│   ├── DagNetWorkX.py           # DAG 状态解析
│   ├── Dag2JSON.py              # Graphviz DOT → JSON
│   └── CleanLog.py              # Snakemake 日志解析
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── pages/               # 路由页面 (upload, query, dashboard...)
│   │   ├── components/          # 组件 (UserFiles, OpenWorkflow, ListResults...)
│   │   └── router/              # Vue Router 配置
│   └── public/                  # 静态资源 (logo, favicon)
├── db/                          # 共享参考数据库
│   ├── kraken2/                 # Kraken2 标准库
│   ├── reference/hg38/          # 宿主参考基因组
│   ├── reference/phiX/          # PhiX 对照
│   ├── eggnog/                  # eggNOG 功能注释库
│   ├── busco_downloads/         # BUSCO 谱系数据
│   └── metaquast/silva/         # SILVA rRNA 参考
├── raw_data/IBD/                # 测试数据集 (IBDMDB)
├── envs/                        # Conda 环境 YAML 配置
│   ├── ProjectM_DNA_main.yml    # 主分析环境 (Python 3.13 + R 4.5)
│   ├── ProjectM_DNA_prokka.yml  # Prokka 环境
│   ├── ProjectM_DNA_lefse.yml   # LEfSe 环境
│   ├── ProjectM_RNA_eggnog.yml  # eggNOG-mapper 环境
│   ├── ProjectM_DNA_busco.yml   # BUSCO 环境
│   └── flask_backend.yml        # Flask 后端环境
└── users/                       # 用户数据隔离目录
    └── {user_uuid}/
        ├── data/                # 上传的原始文件
        └── workflows/           # 分析任务
            └── {workflow_uuid}/
                ├── samples.csv  # 样本信息表
                ├── snakemake.log
                └── output/      # 分析结果
```

## 环境初始化

### 1. 安装 micromamba

```bash
# Linux/macOS
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
```

### 2. 创建 Conda 虚拟环境

```bash
micromamba env create -f envs/ProjectM_DNA_main.yml    # 主分析环境
micromamba env create -f envs/ProjectM_DNA_prokka.yml   # Prokka 注释
micromamba env create -f envs/ProjectM_DNA_lefse.yml    # LEfSe 差异分析
micromamba env create -f envs/ProjectM_RNA_eggnog.yml   # eggNOG 注释
micromamba env create -f envs/ProjectM_DNA_busco.yml    # BUSCO 评估
micromamba env create -f envs/flask_backend.yml         # Flask 后端
micromamba create -n frontend -c conda-forge nodejs=22  # 前端构建
```

### 3. 安装前端依赖

```bash
cd frontend
micromamba run -n frontend npm install -g pnpm
pnpm install
```

### 4. 下载参考数据库

```bash
# Kraken2 标准库 (需自行下载并放置于 db/kraken2/)
# hg38 参考基因组 (需自行下载并放置于 db/reference/hg38/)
# PhiX 参考 (放置于 db/reference/phiX/)
# eggNOG 数据库 (~20 GB)
download_eggnog_data.py --data_dir db/eggnog/
```

### 5. 配置数据库连接

```bash
# MariaDB 连接信息 (默认值, 可通过环境变量覆盖)
export SQLALCHEMY_DATABASE_URI="mysql+pymysql://user:pass@host:3306/dbname"
# DeepSeek API Key
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxx"
# Flask 密钥
export FLASK_SECRET_KEY="your-secret-key"
```

## 快速启动

### 启动后端

```bash
micromamba run -n flask_backend python flask/app.py
# 默认监听 0.0.0.0:5000
```

### 启动前端

```bash
cd frontend
PATH="/micromamba/envs/frontend/bin:$PATH" pnpm dev --host 0.0.0.0
# 默认监听 0.0.0.0:3000
```

### 访问平台

- 前端: `http://localhost:3000`
- 后端 API: `http://localhost:5000`
- 演示账号: `demo` / 密码: `demo123`

## 命令行直接运行 Snakemake

### 宏基因组 (DNA)

```bash
micromamba run -n ProjectM snakemake \
  -s ProjectM_DNA/snakemake/Snakefile \
  --config ref=hg38 uuid=test_run metadata=IBD_samples.csv \
  --cores 30
```

### 宏转录组 (RNA)

```bash
micromamba run -n ProjectM snakemake \
  -s ProjectM_RNA/snakemake/Snakefile \
  --config ref=hg38 uuid=test_run metadata=IBD_samples_RNA.csv \
  eggnog_data_dir=db/eggnog --cores 30
```

### 仅运行特定规则

```bash
# 只看差异物种
micromamba run -n ProjectM snakemake -s ProjectM_DNA/snakemake/Snakefile \
  --config ref=hg38 uuid=test metadata=IBD_samples.csv \
  --cores 1 09_lefse

# 生成 NCBI 物种链接表
micromamba run -n ProjectM snakemake -s ProjectM_DNA/snakemake/Snakefile \
  --config ref=hg38 uuid=test metadata=IBD_samples.csv \
  --cores 1 27_lefse_ncbi_table
```

## 分析管道概览

### 宏基因组管道 (DNA)

```
fastp → FastQC → BWA(hg38) → BWA(PhiX) → Kraken2 → LEfSe
  → MEGAHIT (single) → Prodigal
  → MEGAHIT (co-assembly) → Prokka → Prokka Viz
  → metaQUAST → Krona → Alpha/Beta Diversity → Heatmap → Stacked Bar
  → Boxplot → Rarefaction → LEfSe NCBI Table
```

### 宏转录组管道 (RNA)

```
fastp → FastQC → BWA(hg38) → BWA(PhiX) → SortMeRNA → Kraken2 → LEfSe
  → MEGAHIT → Prodigal → CD-HIT → eggNOG-mapper
  → KO Matrix → DESeq2 (Volcano + Heatmap)
  → Alpha/Beta Diversity → Stacked Bar → Heatmap → Boxplot → Rarefaction
  → LEfSe NCBI Table → KO KEGG Table
```

## Web 平台功能

| 模块 | 功能 | 技术 |
|------|------|------|
| 用户认证 | 注册/登录, bcrypt + Session | Flask + MariaDB |
| 数据上传 | FASTQ 文件上传, 进度反馈 | Vue 3 + Vuetify |
| AI 编排 | 自然语言 → 样本表 CSV → 自动启动 | DeepSeek LLM API |
| 流程监控 | DAG 实时可视化, 节点状态轮询 | VueFlow + Graphviz dot |
| 结果预览 | PDF/PNG/HTML 在线预览 + 搜索 | Flask + iframe |
| 结果下载 | 白名单过滤打包 ZIP | Flask + zipfile |
| 工作流管理 | 创建/查看/删除, 完成状态判定 | Flask + MariaDB |

## 测试数据

来自 NIH iHMP IBDMDB 项目 (PRJNA395569):

- 1 例溃疡性结肠炎 (UC) 患者 M2026: 5 个纵向采样点
- 1 例 non-IBD 对照 H4008: 3 个纵向采样点
- 每个采样点: 宏基因组 (MGX) + 宏转录组 (MTX) 双端 100bp Illumina HiSeq
- 共 16 个 FASTQ 文库

## 软件版本

| 软件 | 版本 |
|------|------|
| Snakemake | 9.16.3 |
| Python | 3.13.12 |
| R | 4.5.3 |
| FastQC | 0.12.1 |
| fastp | 1.0.1 |
| BWA | 0.7.19 |
| SAMtools | 1.23.1 |
| Kraken2 | 2.17.1 |
| LEfSe | 1.1.2 |
| MEGAHIT | 1.2.9 |
| Prodigal | 2.6.3 |
| Prokka | 1.15.6 |
| eggNOG-mapper | 2.1.13 |
| DESeq2 | 1.50.2 |
| Flask | 3.1.0 |
| Vue | 3.x |
