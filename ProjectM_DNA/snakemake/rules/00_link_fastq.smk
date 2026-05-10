rule link_fastq:
    input:
        fastq1 = lambda wildcards: sample_info[wildcards.sample]["fastq1"],
        fastq2 = lambda wildcards: sample_info[wildcards.sample]["fastq2"]
    output:
        fastq1 = f"{OUTPUT_DIR}/00_raw_data/{{sample}}_1.fastq.gz",
        fastq2 = f"{OUTPUT_DIR}/00_raw_data/{{sample}}_2.fastq.gz",
    shell:
        """
        ln -s {input.fastq1} {output.fastq1};
        ln -s {input.fastq2} {output.fastq2}
        """