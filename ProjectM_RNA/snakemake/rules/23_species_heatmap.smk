rule species_heatmap:
    input:
        matrix   = f"{OUTPUT_DIR}/09_mpa2matrix/mpa_relative_abundance_matrix.tsv",
        metadata = args_metadata
    output:
        pdf = f"{OUTPUT_DIR}/23_species_heatmap/species_heatmap.pdf",
        log = f"{OUTPUT_DIR}/23_species_heatmap/species_heatmap.log"
    shell:
        """
        mkdir -p {OUTPUT_DIR}/23_species_heatmap;
        python {SCRIPT_DIR}/heatmap.py \
            -i {input.matrix} \
            -m {input.metadata} \
            -o {OUTPUT_DIR}/23_species_heatmap \
            -n 30 \
            > {output.log} 2>&1
        """
