rule beta_diversity:
    input:
        matrix   = f"{OUTPUT_DIR}/09_mpa2matrix/mpa_relative_abundance_matrix.tsv",
        metadata = args_metadata
    output:
        dist = f"{OUTPUT_DIR}/21_beta_diversity/bray_curtis_distance.tsv",
        pdf  = f"{OUTPUT_DIR}/21_beta_diversity/beta_diversity_pcoa.pdf",
        log  = f"{OUTPUT_DIR}/21_beta_diversity/beta_diversity.log"
    shell:
        """
        mkdir -p {OUTPUT_DIR}/21_beta_diversity;
        python {SCRIPT_DIR}/beta_diversity.py \
            -i {input.matrix} \
            -m {input.metadata} \
            -o {OUTPUT_DIR}/21_beta_diversity \
            > {output.log} 2>&1
        """
