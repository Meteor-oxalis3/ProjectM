LEFSE_BIOMARKERS_DIR = f"{OUTPUT_DIR}/09_lefse/biomarkers/"
rule lefse:
    input:
        mpa_matrix = f"{OUTPUT_DIR}/08_mpa2matrix/mpa_group_added_matrix.tsv",
    output:
        lefse_in = f"{OUTPUT_DIR}/09_lefse/lefse.in",
        lefse_res = f"{OUTPUT_DIR}/09_lefse/lefse.res",
        lefse_species_LDA_res = f"{OUTPUT_DIR}/09_lefse/lefse_species_LDA.res",
        lefse_species_cladogram_res = f"{OUTPUT_DIR}/09_lefse/lefse_species_cladogram.res",
        lefse_bar_pdf = f"{OUTPUT_DIR}/09_lefse/LDA_bar.pdf",
        lefse_cladogram_pdf = f"{OUTPUT_DIR}/09_lefse/cladogram.pdf",
        lefse_log = f"{OUTPUT_DIR}/09_lefse/lefse.log",
    shell:
        """
        echo "Running LEfSe analysis...";
        (micromamba run -n lefse lefse_format_input.py {input.mpa_matrix} {output.lefse_in} -c 1 -u 2 -s -3 -o 1000000; \
        micromamba run -n lefse lefse_run.py {output.lefse_in} {output.lefse_res} -l {args_lefse_LDA} -s 1; \
        micromamba run -n lefse grep -E "{lefse_pattern}" {output.lefse_res} | grep "{args_lefse_level}" > {output.lefse_species_LDA_res}; \
        micromamba run -n lefse grep -E "{lefse_pattern}" {output.lefse_res} > {output.lefse_species_cladogram_res}; \
        micromamba run -n lefse lefse_plot_res.py {output.lefse_species_LDA_res} {output.lefse_bar_pdf} --format pdf --dpi 600 --left_space 0.3 --width 12; \
        micromamba run -n lefse lefse_plot_cladogram.py {output.lefse_species_cladogram_res} {output.lefse_cladogram_pdf} --format pdf --dpi 600 --right_space 0.3 --left_space 0.0 --labeled_stop_lev 6 --abrv_stop_lev 6; \
        mkdir -p {LEFSE_BIOMARKERS_DIR}; \
        micromamba run -n lefse lefse_plot_features.py {output.lefse_in} {output.lefse_species_LDA_res} {LEFSE_BIOMARKERS_DIR} --dpi 600 --format pdf; \
        ) > {output.lefse_log} 2>&1; \
        echo "LEfSe analysis completed!";
        """