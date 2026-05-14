#!/micromamba/envs/ProjectM/bin/Rscript
# Stacked relative abundance bar chart (species level, top N + Others).
library(optparse)
library(data.table)
library(ggplot2)
library(tidyr)
library(dplyr)
library(RColorBrewer)

option_list <- list(
  make_option(c("-i", "--input"),    type = "character", help = "Relative abundance matrix TSV"),
  make_option(c("-m", "--metadata"), type = "character", help = "Sample metadata CSV (columns: ID, group)"),
  make_option(c("-o", "--outdir"),   type = "character", help = "Output directory"),
  make_option(c("-n", "--top_n"),    type = "integer",   default = 20,
              help = "Number of top species to show [default: %default]")
)
opt <- parse_args(OptionParser(option_list = option_list))
dir.create(opt$outdir, recursive = TRUE, showWarnings = FALSE)

# ── Read data ──────────────────────────────────────────────────────────────────
df   <- fread(opt$input)
meta <- fread(opt$metadata)
setnames(df, names(df)[1], "taxonomy")

# ── Filter to species level ────────────────────────────────────────────────────
species_df <- df[grepl("\\|s__[^|]+$", taxonomy) | grepl("^s__[^|]+$", taxonomy)]
species_df[, species := sub(".*\\|s__", "s__", taxonomy)]
species_df[, taxonomy := NULL]

# ── Melt to long format ────────────────────────────────────────────────────────
long <- melt(species_df, id.vars = "species",
             variable.name = "SampleID", value.name = "abundance")

group_map <- setNames(meta$group, meta$ID)
long[, group := group_map[as.character(SampleID)]]

# ── Top N species by mean abundance ───────────────────────────────────────────
top_species <- long[, .(mean_abu = mean(abundance)), by = species
                   ][order(-mean_abu)][seq_len(min(opt$top_n, .N)), species]

long[, label := fifelse(species %in% top_species, species, "Others")]
agg <- long[, .(abundance = sum(abundance)), by = .(SampleID, group, label)]

# ── Sample order: grouped by condition ────────────────────────────────────────
sample_order <- meta[order(group), ID]
agg[, SampleID := factor(SampleID, levels = sample_order)]

# ── Color palette ─────────────────────────────────────────────────────────────
n_top   <- length(top_species)
palette <- c(colorRampPalette(brewer.pal(12, "Paired"))(n_top), "#CCCCCC")
sp_lev  <- c(top_species, "Others")
agg[, label := factor(label, levels = rev(sp_lev))]

# ── Short display names (strip s__ prefix, replace _ with space) ──────────────
name_map   <- setNames(
  gsub("_", " ", sub("^s__", "", sp_lev)),
  sp_lev
)
name_map["Others"] <- "Others"

p <- ggplot(agg, aes(x = SampleID, y = abundance, fill = label)) +
  geom_bar(stat = "identity", position = "stack", width = 0.8) +
  scale_fill_manual(
    values = rev(palette),
    labels = rev(name_map[sp_lev]),
    name   = "Species"
  ) +
  facet_grid(. ~ group, scales = "free_x", space = "free_x") +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                     expand = expansion(mult = c(0, 0.02))) +
  labs(
    title = paste0("Relative Abundance by Sample (Top ", opt$top_n, " Species)"),
    x     = NULL,
    y     = "Relative Abundance"
  ) +
  theme_classic(base_size = 13) +
  theme(
    axis.text.x      = element_text(angle = 45, hjust = 1, size = 10),
    legend.text      = element_text(size = 9, face = "italic"),
    legend.key.size  = unit(0.45, "cm"),
    legend.title     = element_text(size = 11, face = "bold"),
    strip.background = element_rect(fill = "#E8E8E8", colour = NA),
    strip.text       = element_text(face = "bold", size = 11),
    plot.title       = element_text(face = "bold", hjust = 0.5, size = 14),
    panel.spacing    = unit(0.3, "cm")
  ) +
  guides(fill = guide_legend(ncol = 1, reverse = TRUE))

width_in <- max(6, length(sample_order) * 0.6 + 3)
ggsave(paste0(opt$outdir, "/stacked_bar.pdf"), plot = p,
       width = width_in, height = 5.5, dpi = 300)
ggsave(paste0(opt$outdir, "/stacked_bar.png"), plot = p,
       width = width_in, height = 5.5, dpi = 150)
cat(sprintf("Stacked bar chart saved → %s/stacked_bar.pdf\n", opt$outdir))
