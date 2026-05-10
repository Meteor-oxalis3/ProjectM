rule megahit:
    input:
        rRNA_removed_fastq1 = f"{OUTPUT_DIR}/06_sortmerna/{{sample}}_1.fastq.gz",
        rRNA_removed_fastq2 = f"{OUTPUT_DIR}/06_sortmerna/{{sample}}_2.fastq.gz",
    output:
        contigs = f"{OUTPUT_DIR}/11_megahit/{{sample}}_contigs.fa",
        megahit_log = f"{OUTPUT_DIR}/11_megahit/megahit_{{sample}}.log"
    threads:
        thread_megahit
    shell:
        """
        echo "Running MEGAHIT for {wildcards.sample}...";
        megahit \
        -1 {input.rRNA_removed_fastq1} \
        -2 {input.rRNA_removed_fastq2} \
        -o {OUTPUT_DIR}/11_megahit/{wildcards.sample} \
        -t {thread_megahit} \
        > {output.megahit_log} 2>&1;
        rm {OUTPUT_DIR}/11_megahit/{wildcards.sample}/log;
        ln -s {OUTPUT_DIR}/11_megahit/{wildcards.sample}/final.contigs.fa {output.contigs};
        echo "Finished MEGAHIT for {wildcards.sample}";
        """