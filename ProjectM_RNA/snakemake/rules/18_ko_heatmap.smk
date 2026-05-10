rule ko_heatmap:
    input:
        matrix   = f"{OUTPUT_DIR}/17_ko_matrix/ko_group_added_matrix.tsv",
        metadata = args_metadata
    output:
        pdf = f"{OUTPUT_DIR}/18_ko_heatmap/ko_heatmap.pdf",
        log = f"{OUTPUT_DIR}/18_ko_heatmap/ko_heatmap.log"
    shell:
        """
        mkdir -p {OUTPUT_DIR}/18_ko_heatmap
        python {SCRIPT_DIR}/ko_heatmap.py \
            -i {input.matrix} \
            -m {input.metadata} \
            -o {OUTPUT_DIR}/18_ko_heatmap \
            -n 30 \
            > {output.log} 2>&1
        """
