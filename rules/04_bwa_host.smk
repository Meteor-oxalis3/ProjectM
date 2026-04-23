rule bwa_host:
    input:
        clean_fastq1 = f"{OUTPUT_DIR}/02_fastp/clean_{{sample}}_1.fastq.gz",
        clean_fastq2 = f"{OUTPUT_DIR}/02_fastp/clean_{{sample}}_2.fastq.gz",
        ref = f"{REF_DIR}/{args_ref}.fasta"
    output:
        host_removed_fastq1 = f"{OUTPUT_DIR}/04_bwa_host/{{sample}}_1.fastq.gz",
        host_removed_fastq2 = f"{OUTPUT_DIR}/04_bwa_host/{{sample}}_2.fastq.gz",
        bwa_host_log = f"{OUTPUT_DIR}/04_bwa_host/bwa_host_{{sample}}.log"
    threads: 
        thread_bwa
    shell:
        """
        echo "Running BWA (host) for {wildcards.sample}...";
        (bwa mem \
        -t {thread_bwa} \
        {input.ref} \
        {input.clean_fastq1} \
        {input.clean_fastq2} | \
        samtools view -b -f 12 -F 256 - | \
        samtools fastq -1 {output.host_removed_fastq1} -2 {output.host_removed_fastq2} -0 /dev/null -s /dev/null -n ) \
        > {output.bwa_host_log} 2>&1
        """