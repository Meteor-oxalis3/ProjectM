rule fastqc_clean:
    input:
        fastq1 = f"{OUTPUT_DIR}/02_fastp/clean_{{sample}}_1.fastq.gz",
        fastq2 = f"{OUTPUT_DIR}/02_fastp/clean_{{sample}}_2.fastq.gz"
    output:
        fastqc_pair1_html=f"{OUTPUT_DIR}/03_fastqc_clean/clean_{{sample}}_1_fastqc.zip",
        fastqc_pair1_zip=f"{OUTPUT_DIR}/03_fastqc_clean/clean_{{sample}}_1_fastqc.html",
        fastqc_pair2_html=f"{OUTPUT_DIR}/03_fastqc_clean/clean_{{sample}}_2_fastqc.zip",
        fastqc_pair2_zip=f"{OUTPUT_DIR}/03_fastqc_clean/clean_{{sample}}_2_fastqc.html",
        fastqc_pair1_log=f"{OUTPUT_DIR}/03_fastqc_clean/clean_{{sample}}_1_fastqc.log",
        fastqc_pair2_log=f"{OUTPUT_DIR}/03_fastqc_clean/clean_{{sample}}_2_fastqc.log"
    threads:
        thread_fastqc
    shell:
        """
        echo "Running FastQC for clean {wildcards.sample}...";
        fastqc {input.fastq1} --threads {thread_fastqc} --outdir={OUTPUT_DIR}/03_fastqc_clean > {output.fastqc_pair1_log} 2>&1;
        fastqc {input.fastq2} --threads {thread_fastqc} --outdir={OUTPUT_DIR}/03_fastqc_clean > {output.fastqc_pair2_log} 2>&1
        """