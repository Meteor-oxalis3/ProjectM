rule ko_kegg_table:
    input:
        deseq2_res = f"{OUTPUT_DIR}/18_ko_deseq2/ko_deseq2_results.tsv"
    output:
        html = f"{OUTPUT_DIR}/26_ko_kegg_table/ko_kegg_table.html",
        log  = f"{OUTPUT_DIR}/26_ko_kegg_table/ko_kegg_table.log"
    shell:
        """
        mkdir -p {OUTPUT_DIR}/26_ko_kegg_table
        python {SCRIPT_DIR}/ko_kegg_table.py \
            -i {input.deseq2_res} \
            -o {OUTPUT_DIR}/26_ko_kegg_table \
            --pval 0.05 --log2fc 1.0 \
            > {output.log} 2>&1
        """
