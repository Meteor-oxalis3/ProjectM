rule alpha_diversity:
    input:
        matrix   = f"{OUTPUT_DIR}/09_mpa2matrix/mpa_relative_abundance_matrix.tsv",
        metadata = args_metadata
    output:
        tsv = f"{OUTPUT_DIR}/20_alpha_diversity/alpha_diversity.tsv",
        pdf = f"{OUTPUT_DIR}/20_alpha_diversity/alpha_diversity.pdf",
        log = f"{OUTPUT_DIR}/20_alpha_diversity/alpha_diversity.log"
    shell:
        """
        mkdir -p {OUTPUT_DIR}/20_alpha_diversity;
        python {SCRIPT_DIR}/alpha_diversity.py \
            -i {input.matrix} \
            -m {input.metadata} \
            -o {OUTPUT_DIR}/20_alpha_diversity \
            > {output.log} 2>&1
        """
