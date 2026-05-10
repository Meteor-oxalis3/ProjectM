rule stacked_bar:
    input:
        matrix   = f"{OUTPUT_DIR}/09_mpa2matrix/mpa_relative_abundance_matrix.tsv",
        metadata = args_metadata
    output:
        pdf = f"{OUTPUT_DIR}/22_stacked_bar/stacked_bar.pdf",
        log = f"{OUTPUT_DIR}/22_stacked_bar/stacked_bar.log"
    shell:
        """
        mkdir -p {OUTPUT_DIR}/22_stacked_bar;
        Rscript {SCRIPT_DIR}/stacked_bar.R \
            -i {input.matrix} \
            -m {input.metadata} \
            -o {OUTPUT_DIR}/22_stacked_bar \
            -n 20 \
            > {output.log} 2>&1
        """
