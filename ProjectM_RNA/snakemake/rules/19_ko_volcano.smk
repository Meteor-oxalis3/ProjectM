rule ko_volcano:
    input:
        ko_count = f"{OUTPUT_DIR}/17_ko_matrix/ko_count_matrix.tsv",
        metadata = args_metadata
    output:
        pdf       = f"{OUTPUT_DIR}/19_ko_volcano/ko_volcano.pdf",
        diff_table = f"{OUTPUT_DIR}/19_ko_volcano/ko_diff_results.tsv",
        log       = f"{OUTPUT_DIR}/19_ko_volcano/ko_volcano.log"
    shell:
        """
        mkdir -p {OUTPUT_DIR}/19_ko_volcano
        python {SCRIPT_DIR}/ko_volcano.py \
            -i {input.ko_count} \
            -m {input.metadata} \
            -o {OUTPUT_DIR}/19_ko_volcano \
            --pval 0.05 \
            --log2fc 1.0 \
            > {output.log} 2>&1
        """
