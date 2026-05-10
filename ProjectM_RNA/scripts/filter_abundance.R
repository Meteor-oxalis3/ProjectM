library(optparse)
library(data.table)

option_list <- list(
  make_option(c("-i", "--input"), type="character", default=NULL,
              help="输入文件路径，必须指定", metavar="file"),
  make_option(c("-o", "--output"), type="character", default=NULL,
              help="输出文件路径，必须指定", metavar="file")
)

opt_parser <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parser)

if (is.null(opt$input) || is.null(opt$output)) {
  print_help(opt_parser)
  stop("输入输出文件路径必须指定！", call.=FALSE)
}

# 读取文件
df <- fread(opt$input)

# 备份 taxonomy 列
taxonomy_col <- df$taxonomy

# 提取纯数据部分（不含 taxonomy）
data_matrix <- df[, -1, with = FALSE]

# 设置过滤阈值
min_presence_ratio <- 0.1
min_total_abundance <- 0.01
n_samples <- ncol(data_matrix)

# 计算过滤条件
keep_rows <- rowSums(data_matrix > 0) >= (n_samples * min_presence_ratio) &
             rowSums(data_matrix) >= min_total_abundance

# 应用过滤，同时保留原始 taxonomy 列
df_filtered <- cbind(taxonomy = taxonomy_col[keep_rows], data_matrix[keep_rows])

# 写出结果
fwrite(df_filtered, opt$output, sep = "\t")
