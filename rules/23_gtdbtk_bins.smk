rule gtdbtk_bins:
    """
    GTDB-Tk taxonomic classification of MetaBAT2 MAG bins.

    PREREQUISITES (run once before using this rule):
      1. Download the GTDB-Tk reference database (~57 GB):
           micromamba run -n gtdbtk download-db.sh --db_version R226
         or set GTDBTK_DATA_PATH to an existing database directory.
      2. Configure the database path:
           micromamba run -n gtdbtk gtdbtk configure --db_path /path/to/gtdbtk_db

    This rule is included in the Snakefile but its output is NOT in rule all by default.
    To activate, uncomment the corresponding line in the Snakefile's rule all.
    """
    input:
        depth   = f"{OUTPUT_DIR}/21_mag_bins/{{group}}/depth.txt",
        mag_log = f"{OUTPUT_DIR}/21_mag_bins/{{group}}/mag_bin.log"
    output:
        log     = f"{OUTPUT_DIR}/23_gtdbtk/{{group}}/gtdbtk.log",
        summary = f"{OUTPUT_DIR}/23_gtdbtk/{{group}}/gtdbtk.bac120.summary.tsv"
    params:
        bins_dir = lambda wildcards: f"{OUTPUT_DIR}/21_mag_bins/{wildcards.group}/bins",
        out_dir  = lambda wildcards: f"{OUTPUT_DIR}/23_gtdbtk/{wildcards.group}"
    threads: thread_bwa
    shell:
        """
        mkdir -p {params.out_dir}
        echo "Running GTDB-Tk classify_wf for group {wildcards.group}..." > {output.log}

        n_bins=$(ls {params.bins_dir}/*.fa 2>/dev/null | wc -l)
        echo "Found $n_bins bin(s)" >> {output.log}

        if [ "$n_bins" -eq 0 ]; then
            echo "No bins found, skipping GTDB-Tk." >> {output.log}
            echo -e "user_genome\tclassification" > {output.summary}
        else
            micromamba run -n gtdbtk gtdbtk classify_wf \
                --genome_dir {params.bins_dir} \
                --extension fa \
                --out_dir {params.out_dir} \
                --cpus {threads} \
                --skip_ani_screen \
                >> {output.log} 2>&1

            # Ensure summary file exists even if no bacteria found
            if [ ! -f {output.summary} ]; then
                echo -e "user_genome\tclassification" > {output.summary}
                echo "No bacterial summary produced (may be archaea or empty)." >> {output.log}
            fi
        fi

        echo "GTDB-Tk complete." >> {output.log}
        """
