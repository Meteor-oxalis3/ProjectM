rule lefse_ncbi_table:
    input:
        lefse_res = f"{OUTPUT_DIR}/09_lefse/lefse_species_LDA.res"
    output:
        html = f"{OUTPUT_DIR}/27_lefse_ncbi_table/lefse_ncbi_species.html",
        log  = f"{OUTPUT_DIR}/27_lefse_ncbi_table/lefse_ncbi_table.log"
    shell:
        """
        mkdir -p {OUTPUT_DIR}/27_lefse_ncbi_table
        python {SCRIPT_DIR}/lefse_ncbi_table.py \
            -i {input.lefse_res} \
            -o {OUTPUT_DIR}/27_lefse_ncbi_table \
            -l 2.0 \
            > {output.log} 2>&1
        """
