rule sortmerna:
    input:
        phix_removed_fastq1 = f"{OUTPUT_DIR}/05_bwa_phix/{{sample}}_1.fastq.gz",
        phix_removed_fastq2 = f"{OUTPUT_DIR}/05_bwa_phix/{{sample}}_2.fastq.gz",
    output:
        rRNA_removed_fastq1 = f"{OUTPUT_DIR}/06_sortmerna/{{sample}}_1.fastq.gz",
        rRNA_removed_fastq2 = f"{OUTPUT_DIR}/06_sortmerna/{{sample}}_2.fastq.gz",
        sortmerna_log = f"{OUTPUT_DIR}/06_sortmerna/sortmerna_{{sample}}.log"
    threads:
        thread_sortmerna
    shell:
        """
        echo "Running SortMeRNA for {wildcards.sample}...";
        sortmerna --ref {SORTMERNA_DB_FILE} \
        --reads {input.phix_removed_fastq1} \
        --reads {input.phix_removed_fastq2} \
        --threads {thread_sortmerna} \
        --workdir {OUTPUT_DIR}/06_sortmerna/{wildcards.sample} > {output.sortmerna_log} 2>&1;
        cat {OUTPUT_DIR}/06_sortmerna/{wildcards.sample}/readb/fwd_*.fq.gz > {output.rRNA_removed_fastq1};
        cat {OUTPUT_DIR}/06_sortmerna/{wildcards.sample}/readb/rev_*.fq.gz > {output.rRNA_removed_fastq2};
        echo "Finished SortMeRNA for {wildcards.sample}!";
        """