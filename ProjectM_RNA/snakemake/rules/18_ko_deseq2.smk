rule ko_deseq2:
    input:
        counts   = f"{OUTPUT_DIR}/17_ko_matrix/ko_count_matrix.tsv",
        metadata = args_metadata
    output:
        volcano      = f"{OUTPUT_DIR}/18_ko_deseq2/ko_volcano.pdf",
        heatmap      = f"{OUTPUT_DIR}/18_ko_deseq2/ko_heatmap.pdf",
        results      = f"{OUTPUT_DIR}/18_ko_deseq2/ko_deseq2_results.tsv",
        log          = f"{OUTPUT_DIR}/18_ko_deseq2/ko_deseq2.log"
    shell:
        """
        mkdir -p {OUTPUT_DIR}/18_ko_deseq2
        Rscript {SCRIPT_DIR}/ko_deseq2.R \
            -c {input.counts} \
            -m {input.metadata} \
            -o {OUTPUT_DIR}/18_ko_deseq2 \
            --pval 0.05 \
            --log2fc 1.0 \
            --top_n 30 \
            > {output.log} 2>&1
        """
