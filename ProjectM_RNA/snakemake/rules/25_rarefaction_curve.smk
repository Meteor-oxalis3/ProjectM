rule rarefaction_curve:
    input:
        matrix   = f"{OUTPUT_DIR}/09_mpa2matrix/mpa_matrix.tsv",
        metadata = args_metadata
    output:
        pdf = f"{OUTPUT_DIR}/25_rarefaction_curve/rarefaction_curve.pdf",
        tsv = f"{OUTPUT_DIR}/25_rarefaction_curve/rarefaction_summary.tsv",
        log = f"{OUTPUT_DIR}/25_rarefaction_curve/rarefaction_curve.log"
    shell:
        """
        mkdir -p {OUTPUT_DIR}/25_rarefaction_curve;
        Rscript {SCRIPT_DIR}/rarefaction_curve.R \
            -i {input.matrix} \
            -m {input.metadata} \
            -o {OUTPUT_DIR}/25_rarefaction_curve \
            > {output.log} 2>&1
        """
