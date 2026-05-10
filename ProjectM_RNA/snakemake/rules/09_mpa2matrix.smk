rule mpa2matrix:
    input:
        mpa_json_path = f"{OUTPUT_DIR}/08_kreport2mpa/mpa.json",
        metadata = args_metadata
    output:
        matrix = f"{OUTPUT_DIR}/09_mpa2matrix/mpa_matrix.tsv",
        relative_abundance_matrix = f"{OUTPUT_DIR}/09_mpa2matrix/mpa_relative_abundance_matrix.tsv",
        # filter_abundance_matrix = f"{OUTPUT_DIR}/09_mpa2matrix/mpa_filter_abundance_matrix.tsv",
        group_added_matrix = f"{OUTPUT_DIR}/09_mpa2matrix/mpa_group_added_matrix.tsv"
    shell:
        """
        echo "Running mpa2matrix...";
        Rscript {SCRIPT_DIR}/mpa2matrix.R -i {input.mpa_json_path} -o {output.matrix};
        python {SCRIPT_DIR}/relative_abundance.py -i {output.matrix} -o {output.relative_abundance_matrix};
        python {SCRIPT_DIR}/group_info.py -i {output.relative_abundance_matrix} -g {input.metadata} -o {output.group_added_matrix};
        echo "Finished mpa2matrix!"
        """