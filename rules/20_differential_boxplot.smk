rule differential_boxplot:
    input:
        matrix    = f"{OUTPUT_DIR}/08_mpa2matrix/mpa_relative_abundance_matrix.tsv",
        lefse_res = f"{OUTPUT_DIR}/09_lefse/lefse_species_LDA.res",
        metadata  = args_metadata
    output:
        pdf = f"{OUTPUT_DIR}/20_differential_boxplot/differential_boxplot.pdf",
        log = f"{OUTPUT_DIR}/20_differential_boxplot/differential_boxplot.log"
    shell:
        """
        mkdir -p {OUTPUT_DIR}/20_differential_boxplot;
        python {SCRIPT_DIR}/differential_boxplot.py \
            -i {input.matrix} \
            -l {input.lefse_res} \
            -m {input.metadata} \
            -o {OUTPUT_DIR}/20_differential_boxplot \
            -n 12 \
            > {output.log} 2>&1
        """
