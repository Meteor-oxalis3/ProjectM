rule megahit_group:
    input:
        merged_fastq1 = f"{OUTPUT_DIR}/14_megahit_merged/{{group}}_merged_1.fastq.gz",
        merged_fastq2 = f"{OUTPUT_DIR}/14_megahit_merged/{{group}}_merged_2.fastq.gz",
    output:
        contigs = f"{OUTPUT_DIR}/15_megahit_group/{{group}}/final.contigs.fa",
        megahit_log = f"{OUTPUT_DIR}/15_megahit_group/{{group}}_megahit.log"
    threads:
        thread_megahit
    shell:
        """
        echo "Running MEGAHIT for group {wildcards.group} ...";
        rm -rf {OUTPUT_DIR}/15_megahit_group/{wildcards.group}; \
        megahit \
        -1 {input.merged_fastq1} \
        -2 {input.merged_fastq2} \
        -o {OUTPUT_DIR}/15_megahit_group/{wildcards.group} \
        -t {thread_megahit} \
        > {output.megahit_log} 2>&1;
        echo "Finished MEGAHIT for group {wildcards.group} ...";
        """