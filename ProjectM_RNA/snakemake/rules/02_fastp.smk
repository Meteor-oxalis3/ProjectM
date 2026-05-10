rule fastp:
    input:
        fastq1 = f"{OUTPUT_DIR}/00_raw_data/{{sample}}_1.fastq.gz",
        fastq2 = f"{OUTPUT_DIR}/00_raw_data/{{sample}}_2.fastq.gz"
    output:
        fastp_json = f"{OUTPUT_DIR}/02_fastp/{{sample}}.json",
        fastp_html = f"{OUTPUT_DIR}/02_fastp/{{sample}}.html",
        clean_fastq1 = f"{OUTPUT_DIR}/02_fastp/clean_{{sample}}_1.fastq.gz",
        clean_fastq2 = f"{OUTPUT_DIR}/02_fastp/clean_{{sample}}_2.fastq.gz",
        fastp_log = f"{OUTPUT_DIR}/02_fastp/Fastp_{{sample}}.log"
    threads:
        thread_fastp
    shell:
        """
        echo "Running Fastp for {wildcards.sample}...";
        fastp --detect_adapter_for_pe \
            -5 -c \
            --cut_mean_quality 20 \
            --length_required 36 \
            -i {input.fastq1} \
            -I {input.fastq2} \
            -o {output.clean_fastq1} \
            -O {output.clean_fastq2} \
            -j {output.fastp_json} \
            -h {output.fastp_html} \
            -w {thread_fastp} > {output.fastp_log} 2>&1
        """