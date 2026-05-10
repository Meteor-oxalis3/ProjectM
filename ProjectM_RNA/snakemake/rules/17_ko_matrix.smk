rule ko_matrix:
    input:
        annotations = expand(f"{OUTPUT_DIR}/15_eggnog_mapper/{{sample}}.emapper.annotations", sample=list_ID),
        metadata    = args_metadata
    output:
        ko_count_matrix      = f"{OUTPUT_DIR}/17_ko_matrix/ko_count_matrix.tsv",
        ko_relative_matrix   = f"{OUTPUT_DIR}/17_ko_matrix/ko_relative_abundance_matrix.tsv",
        ko_group_added_matrix = f"{OUTPUT_DIR}/17_ko_matrix/ko_group_added_matrix.tsv",
        log                  = f"{OUTPUT_DIR}/17_ko_matrix/ko_matrix.log"
    shell:
        """
        mkdir -p {OUTPUT_DIR}/17_ko_matrix
        python {SCRIPT_DIR}/ko_matrix.py \
            -a {input.annotations} \
            -o {output.ko_count_matrix} \
            -r {output.ko_relative_matrix} \
            -g {output.ko_group_added_matrix} \
            -m {input.metadata} \
            > {output.log} 2>&1
        echo "KO matrix built."
        """
