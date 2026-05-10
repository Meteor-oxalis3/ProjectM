#!/usr/bin/env Rscript
#' KO Differential Analysis with DESeq2
#'
#' Reads KO count matrix + metadata, runs DESeq2 for differential KO analysis,
#' generates volcano plot, heatmap of top significant KOs, and results table.
#'
#' Usage:
#'   Rscript ko_deseq2.R -c ko_count_matrix.tsv -m metadata.csv -o outdir

suppressPackageStartupMessages({
  library(optparse)
  library(DESeq2)
  library(ggplot2)
  library(ggrepel)
  library(pheatmap)
  library(RColorBrewer)
  library(data.table)
})

# ── CLI ──────────────────────────────────────────────────────────────────────
option_list <- list(
  make_option(c("-c", "--counts"),   type = "character", help = "KO count matrix TSV (KOs=rows, samples=columns)"),
  make_option(c("-m", "--metadata"), type = "character", help = "Sample metadata CSV (columns: ID, group)"),
  make_option(c("-o", "--outdir"),   type = "character", help = "Output directory"),
  make_option(c("--pval"),           type = "numeric",   default = 0.05,  help = "Adjusted p-value threshold [default: 0.05]"),
  make_option(c("--log2fc"),         type = "numeric",   default = 1.0,   help = "|log2FC| threshold [default: 1.0]"),
  make_option(c("--top_n"),          type = "integer",   default = 30,    help = "Top N KOs for heatmap [default: 30]")
)
opt <- parse_args(OptionParser(option_list = option_list))
dir.create(opt$outdir, recursive = TRUE, showWarnings = FALSE)

# ── Load data ────────────────────────────────────────────────────────────────
counts <- fread(opt$counts, header = TRUE, sep = "\t")
counts_mat <- as.matrix(counts[, -1, with = FALSE])
rownames(counts_mat) <- counts[[1]]
storage.mode(counts_mat) <- "integer"

meta <- read.csv(opt$metadata, stringsAsFactors = FALSE)
meta <- meta[, c(1, 4)]
colnames(meta) <- c("ID", "group")
meta$group <- factor(meta$group)
rownames(meta) <- meta$ID

# Align samples
shared <- intersect(colnames(counts_mat), meta$ID)
counts_mat <- counts_mat[, shared, drop = FALSE]
meta <- meta[shared, ]

# ── DESeq2 ───────────────────────────────────────────────────────────────────
dds <- DESeqDataSetFromMatrix(countData = counts_mat, colData = meta, design = ~ group)
dds <- DESeq(dds)

# Get results and apply apeglm shrinkage
res <- results(dds, alpha = opt$pval)
res <- lfcShrink(dds, coef = resultsNames(dds)[2], type = "apeglm", quiet = TRUE)
res_df <- as.data.frame(res)
res_df$KO <- rownames(res_df)
res_df <- res_df[order(res_df$pvalue), ]

# Significance categories
res_df$sig <- "NS"
res_df$sig[!is.na(res_df$padj) & res_df$padj < opt$pval & res_df$log2FoldChange >= opt$log2fc] <- "Up"
res_df$sig[!is.na(res_df$padj) & res_df$padj < opt$pval & res_df$log2FoldChange <= -opt$log2fc] <- "Down"

# Save results table
write.table(res_df, file.path(opt$outdir, "ko_deseq2_results.tsv"),
            sep = "\t", row.names = FALSE, quote = FALSE)

# ── Volcano plot ────────────────────────────────────────────────────────────
res_plot <- res_df[!is.na(res_df$padj), ]
res_plot$neg_log10_padj <- -log10(pmax(res_plot$padj, 1e-300))

groups <- levels(meta$group)
g1 <- groups[1]; g2 <- groups[2]

colors <- c("NS" = "#999999", "Up" = "#E07A5F", "Down" = "#3D6B8F")
ggplot(res_plot, aes(x = log2FoldChange, y = neg_log10_padj, color = sig)) +
  geom_point(size = 1.2, alpha = 0.7) +
  scale_color_manual(values = colors) +
  geom_hline(yintercept = -log10(opt$pval), linetype = "dashed", color = "grey60", linewidth = 0.5) +
  geom_vline(xintercept = c(-opt$log2fc, opt$log2fc), linetype = "dashed", color = "grey60", linewidth = 0.5) +
  labs(x = paste0("log2(Fold Change) [", g1, " / ", g2, "]"),
       y = "-log10(adjusted p-value)",
       title = paste0("KO Differential Expression: ", g1, " vs ", g2)) +
  theme_classic(base_size = 12) +
  theme(legend.position = c(0.9, 0.9),
        plot.title = element_text(face = "bold", hjust = 0.5, size = 13)) +
  geom_text_repel(
    data = subset(res_plot, sig != "NS") |> head(15),
    aes(label = KO), size = 3, max.overlaps = 20
  )
ggsave(file.path(opt$outdir, "ko_volcano.pdf"), width = 10, height = 8, dpi = 300)
ggsave(file.path(opt$outdir, "ko_volcano.png"), width = 10, height = 8, dpi = 150)
# Ensure all ggsave devices are closed before heatmap
while (dev.cur() > 1) dev.off()
cat(sprintf("Volcano plot saved -> %s/ko_volcano.pdf\n", opt$outdir))
cat(sprintf("Differential KOs: Up=%d, Down=%d, NS=%d\n",
            sum(res_plot$sig == "Up"), sum(res_plot$sig == "Down"), sum(res_plot$sig == "NS")))

# ── Heatmap ──────────────────────────────────────────────────────────────────
top_ko <- head(res_df[res_df$sig != "NS", ], opt$top_n)$KO
if (length(top_ko) >= 5) {
  rld <- rlog(dds, blind = FALSE)
  mat <- assay(rld)[top_ko, , drop = FALSE]
  mat <- mat[apply(mat, 1, sd) > 0, , drop = FALSE]
  if (nrow(mat) < 3) stop("Not enough variable rows for heatmap")
  rownames(mat) <- gsub("^ko:", "", rownames(mat))

  ann_col <- data.frame(Group = meta$group, row.names = meta$ID)
  ann_colors <- list(Group = c("#E07A5F", "#3D6B8F", "#81B29A", "#F2CC8F")[seq_along(groups)])
  names(ann_colors$Group) <- groups

  # Heatmap
  pdf_path <- file.path(opt$outdir, "ko_heatmap.pdf")
  tryCatch({
    pdf(pdf_path, width = 10, height = 8)
    pheatmap(mat,
             annotation_col       = ann_col,
             annotation_colors    = ann_colors,
             scale                = "row",
             clustering_method    = "ward.D2",
             color                = colorRampPalette(rev(RColorBrewer::brewer.pal(9, "RdYlBu")))(100),
             fontsize_row         = 7,
             fontsize_col         = 9,
             main                 = paste0("Top ", nrow(mat), " Differential KOs (DESeq2 rlog)"),
             border_color         = NA)
    dev.off()
    cat(sprintf("Heatmap saved -> %s (%d bytes)\n", pdf_path, file.size(pdf_path)))
  }, error = function(e) {
    cat(sprintf("Heatmap ERROR: %s\n", e$message))
  })
} else {
  cat("Not enough significant KOs for heatmap (need >= 5, found ", length(top_ko), ")\n", sep = "")
}
