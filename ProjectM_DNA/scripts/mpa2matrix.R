#!/micromamba/envs/ProjectM/bin/Rscript
# mpa2matrix.R
# 该脚本用于将多个 .mpa 文件合并为一个矩阵文件
# 输入：mpa.json 文件，包含样本组信息和mpa文件路径
# 输出：合并后的矩阵文件，默认名为 merged_mpa_matrix.tsv
library(optparse)
library(data.table)
library(tidyverse)
library(jsonlite)

# ---------- Step 1: 定义命令行参数 ----------
option_list <- list(
  make_option(c("-i", "--input"), type = "character", default = NULL,
              help = "输入的 mpa.json 文件路径", metavar = "character"),
  make_option(c("-o", "--output"), type = "character", default = "merged_mpa_matrix.tsv",
              help = "输出合并后的矩阵文件名 [默认: %default]", metavar = "character")
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

# ---------- Step 2: 检查参数 ----------
if (is.null(opt$input)) {
  print_help(opt_parser)
  stop("必须提供 --input 参数！", call. = FALSE)
}

# ---------- Step 3: 读取 JSON ----------
group_info <- fromJSON(opt$input)
sample_files <- unlist(group_info, use.names = FALSE)
sample_names <- tools::file_path_sans_ext(basename(sample_files))

# ---------- Step 4: 读取每个 .mpa 文件 ----------
data_list <- lapply(seq_along(sample_files), function(i) {
  file <- sample_files[i]
  sample <- sample_names[i]

  df <- fread(file, header = FALSE, sep = "\t", fill = TRUE)
  if (ncol(df) < 2) stop(paste("格式错误：", file))
  df <- df[, .(taxonomy = V1, count = as.numeric(V2))]
  df$sample <- sample
  df
})

# ---------- Step 5: 合并 & 转 wide ----------
merged_long <- rbindlist(data_list)
merged_wide <- dcast(merged_long, taxonomy ~ sample, value.var = "count", fill = 0.0)

# ---------- Step 6: 保存 ----------
fwrite(merged_wide, opt$output, sep = "\t", quote = FALSE)
