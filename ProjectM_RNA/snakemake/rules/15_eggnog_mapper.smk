rule eggnog_mapper:
    """
    eggNOG-mapper functional annotation of CD-HIT clustered protein sequences.

    PREREQUISITES:
      1. Download eggNOG database (~20 GB for bacteria, ~50 GB for all):
           download_eggnog_data.py --data_dir /path/to/eggnog_db
      2. Set `eggnog_db` in snakemake config, e.g.:
           --config eggnog_db=/path/to/eggnog_db

    Output per sample: .emapper.annotations file containing KO, GO, COG, etc.
    """
    input:
        faa = f"{OUTPUT_DIR}/14_cdhit/{{sample}}_genes_cdhit.faa"
    output:
        annotations = f"{OUTPUT_DIR}/15_eggnog_mapper/{{sample}}.emapper.annotations",
        log         = f"{OUTPUT_DIR}/15_eggnog_mapper/eggnog_{{sample}}.log"
    params:
        out_prefix = lambda wildcards: f"{OUTPUT_DIR}/15_eggnog_mapper/{wildcards.sample}",
        data_dir   = config.get("eggnog_data_dir", ""),
        tax_scope  = config.get("eggnog_tax_scope", "prokaryota_broad")
    threads: thread_prodigal
    shell:
        """
        mkdir -p {OUTPUT_DIR}/15_eggnog_mapper
        echo "Running eggNOG-mapper for {wildcards.sample}..."

        DATA_DIR_ARG=""
        if [ -n "{params.data_dir}" ] && [ -d "{params.data_dir}" ]; then
            DATA_DIR_ARG="--data_dir {params.data_dir}"
        fi

        micromamba run -n eggnog emapper.py \
            -i {input.faa} \
            --output {params.out_prefix} \
            --cpu {threads} \
            --tax_scope {params.tax_scope} \
            $DATA_DIR_ARG \
            > {output.log} 2>&1

        echo "eggNOG-mapper complete for {wildcards.sample}."
        """
