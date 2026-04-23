rule kraken2:
    input:
        phix_removed_fastq1 = f"{OUTPUT_DIR}/05_bwa_phix/{{sample}}_1.fastq.gz",
        phix_removed_fastq2 = f"{OUTPUT_DIR}/05_bwa_phix/{{sample}}_2.fastq.gz",
    output:
        kraken2_output = f"{OUTPUT_DIR}/06_kraken2/{{sample}}.kraken",
        kraken2_report = f"{OUTPUT_DIR}/06_kraken2/{{sample}}.report",
        kraken2_log = f"{OUTPUT_DIR}/06_kraken2/kraken2_{{sample}}.log"
    threads: 
        thread_kraken2
    shell:
        """
        echo "Running Kraken2 for {wildcards.sample}...";
        kraken2 --db {KRAKEN2_DB_DIR} \
        --paired {input.phix_removed_fastq1} {input.phix_removed_fastq2} \
        --use-names \
        --output {output.kraken2_output} \
        --report {output.kraken2_report} \
        --threads {thread_kraken2} \
        > {output.kraken2_log} 2>&1;
        echo "Finished Kraken2 for {wildcards.sample}!";
        """