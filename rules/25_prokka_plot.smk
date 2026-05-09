rule prokka_plot:
    """
    Visualize Prokka annotation results across all groups.
    Requires all groups' Prokka runs to be complete.
    Produces 4 plots:
      - prokka_feature_counts.pdf   (CDS/tRNA/rRNA counts per group)
      - prokka_annotation_rate.pdf  (annotated vs hypothetical CDS donut)
      - prokka_top_products.pdf     (top N gene products per group)
      - prokka_product_bubble.pdf   (shared/group-enriched functions, 2-group only)
    """
    input:
        expand(f"{OUTPUT_DIR}/24_prokka/{{group}}/{{group}}.gff", group=list_group)
    output:
        feat_pdf   = f"{OUTPUT_DIR}/25_prokka_plot/prokka_feature_counts.pdf",
        rate_pdf   = f"{OUTPUT_DIR}/25_prokka_plot/prokka_annotation_rate.pdf",
        top_pdf    = f"{OUTPUT_DIR}/25_prokka_plot/prokka_top_products.pdf",
        log        = f"{OUTPUT_DIR}/25_prokka_plot/prokka_plot.log"
    shell:
        """
        mkdir -p {OUTPUT_DIR}/25_prokka_plot;
        python {SCRIPT_DIR}/prokka_plot.py \
            -d {OUTPUT_DIR}/24_prokka \
            -o {OUTPUT_DIR}/25_prokka_plot \
            -n 20 \
            > {output.log} 2>&1
        touch {output.feat_pdf} {output.rate_pdf} {output.top_pdf}
        """
