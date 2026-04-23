rule bwa_phix:
    input:
        host_removed_fastq1 = f"{OUTPUT_DIR}/04_bwa_host/{{sample}}_1.fastq.gz",
        host_removed_fastq2 = f"{OUTPUT_DIR}/04_bwa_host/{{sample}}_2.fastq.gz",
        phix_ref = f"{ROOT_DIR}/db/reference/phiX/phiX.fasta"
    output:
        phix_removed_fastq1 = f"{OUTPUT_DIR}/05_bwa_phix/{{sample}}_1.fastq.gz",
        phix_removed_fastq2 = f"{OUTPUT_DIR}/05_bwa_phix/{{sample}}_2.fastq.gz",
        bwa_phix_log = f"{OUTPUT_DIR}/05_bwa_phix/bwa_phix_{{sample}}.log"
    threads:
        thread_bwa
    shell:
        """
        echo "Running BWA (phix) for {wildcards.sample}...";
        (bwa mem \
        -t {thread_bwa} \
        {input.phix_ref} \
        {input.host_removed_fastq1} \
        {input.host_removed_fastq2} | \
        samtools view -b -f 12 -F 256 - | \
        samtools fastq -1 {output.phix_removed_fastq1} -2 {output.phix_removed_fastq2} -0 /dev/null -s /dev/null -n ) \
        > {output.bwa_phix_log} 2>&1
        """