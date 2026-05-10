rule eggnog_mapper:
    """
    eggNOG-mapper functional annotation of CD-HIT clustered protein sequences
    (offline mode only — requires local eggNOG database).

    PREREQUISITES:
      1. Download eggNOG database:
           download_eggnog_data.py --data_dir /path/to/eggnog_db
      2. Set `eggnog_data_dir` in snakemake config:
           --config eggnog_data_dir=/path/to/eggnog_db

    Output per sample: .emapper.annotations file containing KO, GO, COG, etc.
    """
    input:
        faa = f"{OUTPUT_DIR}/14_cdhit/{{sample}}_genes_cdhit.faa"
    output:
        annotations = f"{OUTPUT_DIR}/15_eggnog_mapper/{{sample}}.emapper.annotations",
        log         = f"{OUTPUT_DIR}/15_eggnog_mapper/eggnog_{{sample}}.log"
    params:
        out_prefix = lambda wildcards: f"{OUTPUT_DIR}/15_eggnog_mapper/{wildcards.sample}",
        tax_scope  = config.get("eggnog_tax_scope", "prokaryota_broad")
    threads: thread_prodigal
    shell:
        """
        if [ -z "{EGGNOG_DB_DIR}" ] || [ ! -d "{EGGNOG_DB_DIR}" ]; then
            echo "ERROR: eggNOG data directory not found: {EGGNOG_DB_DIR}" >&2
            echo "Download with: download_eggnog_data.py --data_dir /path/to/eggnog_db" >&2
            echo "Then set EGGNOG_DB_DIR in Snakefile" >&2
            exit 1
        fi

        mkdir -p {OUTPUT_DIR}/15_eggnog_mapper
        echo "Running eggNOG-mapper for {wildcards.sample} (offline, data_dir={EGGNOG_DB_DIR})..."

        micromamba run -n eggnog emapper.py \
            -i {input.faa} \
            --output {params.out_prefix} \
            --cpu {threads} \
            --tax_scope {params.tax_scope} \
            --data_dir {EGGNOG_DB_DIR} \
            > {output.log} 2>&1

        echo "eggNOG-mapper complete for {wildcards.sample}."
        """
