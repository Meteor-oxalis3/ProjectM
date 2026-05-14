#!/usr/bin/env Rscript
#' Rarefaction Curves using vegan
#' Plots rarefaction curves for each sample, colored by group,
#' to assess sequencing depth sufficiency.
#'
#' Usage:
#'   Rscript rarefaction_curve.R -i mpa_matrix.tsv -m metadata.csv -o outdir

suppressPackageStartupMessages({
  library(optparse)
  library(data.table)
  library(vegan)
})

# ── CLI ────────────────────────────────────────────────────────────────────────
option_list <- list(
  make_option(c("-i", "--input"), type = "character",
              help = "Raw count matrix TSV (samples as columns, taxa as rows)"),
  make_option(c("-m", "--metadata"), type = "character",
              help = "Sample metadata CSV with ID and group columns"),
  make_option(c("-o", "--outdir"), type = "character",
              help = "Output directory")
)

parser    <- OptionParser(option_list = option_list)
arguments <- parse_args(parser)

stopifnot(is.character(arguments$input),
          is.character(arguments$metadata),
          is.character(arguments$outdir))

dir.create(arguments$outdir, showWarnings = FALSE, recursive = TRUE)

# ── Load data ──────────────────────────────────────────────────────────────────
# use data.table::fread to avoid quote/EOL issues with taxonomy strings
counts_dt <- fread(arguments$input, header = TRUE, sep = "\t")
counts    <- as.data.frame(counts_dt)
rownames(counts) <- counts[[1]]
counts[[1]] <- NULL

meta   <- read.csv(arguments$metadata, stringsAsFactors = FALSE)
colnames(meta)[1:2] <- c("ID", "group")
group_dict <- setNames(meta$group, meta$ID)

# vegan requires samples as rows, species as columns
counts_t <- as.data.frame(t(counts))

# Keep only samples present in metadata
common <- intersect(rownames(counts_t), names(group_dict))
counts_t <- counts_t[common, , drop = FALSE]

# ── Richness (rarefied per sample) ─────────────────────────────────────────────
# Determine rarefaction depth: minimum sample sum, but bounded for plotting
sample_sums   <- rowSums(counts_t)
min_depth     <- min(sample_sums)
rarefy_depth  <- min_depth  # can be overridden

cat(sprintf("Sample read counts: %s\n", paste(sample_sums, collapse = ", ")))
cat(sprintf("Minimum sample depth: %.0f\n", min_depth))

# Rarefied richness
rarefied_richness <- rarefy(counts_t, sample = rarefy_depth)

# Write summary table
richness_df <- data.frame(
  Sample            = names(rarefied_richness),
  Original_Reads    = sample_sums,
  Rarefied_Richness = rarefied_richness,
  Group             = group_dict[names(rarefied_richness)],
  row.names         = NULL
)
write.table(richness_df, file.path(arguments$outdir, "rarefaction_summary.tsv"),
            sep = "\t", row.names = FALSE, quote = FALSE)

# ── Colors ─────────────────────────────────────────────────────────────────────
groups  <- unique(group_dict[common])
n_group <- length(groups)
palette <- c("#E07A5F", "#3D6B8F", "#81B29A", "#F2CC8F", "#574B90",
             "#E8A87C", "#95B8D1", "#C38D9E", "#7C6A8A", "#A8D0E6")
color_map <- setNames(palette[seq_len(n_group)], groups)

sample_colors <- color_map[group_dict[common]]
names(sample_colors) <- common

# ── Rarefaction curve plot ─────────────────────────────────────────────────────
pdf(file.path(arguments$outdir, "rarefaction_curve.pdf"),
    width = 6, height = 5)

rarecurve(counts_t,
          step  = max(1, floor(min_depth / 100)),
          sample = NULL,
          col    = sample_colors,
          lwd    = 1.5,
          cex    = 0.8,
          label  = TRUE,
          ylab   = "Number of Species (Richness)",
          xlab   = "Number of Reads Sampled",
          main   = "Rarefaction Curves",
          cex.lab = 1.2,
          cex.axis = 1.0,
          cex.main = 1.3)

# Add vertical line at rarefaction depth
abline(v = rarefy_depth, lty = 2, col = "darkgray", lwd = 1.2)
text(x = rarefy_depth * 0.88, y = max(rowSums(counts_t > 0)) * 0.95,
     labels = sprintf("Resampling depth: %.0f reads", rarefy_depth),
     cex = 1.0, col = "darkgray")

invisible(dev.off())

# ── PNG version ────────────────────────────────────────────────────────────────
png(file.path(arguments$outdir, "rarefaction_curve.png"),
    width = 6, height = 5, units = "in", res = 150)

rarecurve(counts_t,
          step  = max(1, floor(min_depth / 100)),
          sample = NULL,
          col    = sample_colors,
          lwd    = 1.5,
          cex    = 0.8,
          label  = TRUE,
          ylab   = "Number of Species (Richness)",
          xlab   = "Number of Reads Sampled",
          main   = "Rarefaction Curves",
          cex.lab = 1.2,
          cex.axis = 1.0,
          cex.main = 1.3)

abline(v = rarefy_depth, lty = 2, col = "darkgray", lwd = 1.2)

invisible(dev.off())
