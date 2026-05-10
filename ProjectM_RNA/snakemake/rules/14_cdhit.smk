rule cdhit:
    input:
        faa = f"{OUTPUT_DIR}/12_prodigal/{{sample}}_genes.faa",
        fna = f"{OUTPUT_DIR}/12_prodigal/{{sample}}_genes.fna"
    output:
        cdhit_faa = f"{OUTPUT_DIR}/14_cdhit/{{sample}}_genes_cdhit.faa",
        cdhit_fna = f"{OUTPUT_DIR}/14_cdhit/{{sample}}_genes_cdhit.fna",
        cdhit_faa_log = f"{OUTPUT_DIR}/14_cdhit/cdhit_{{sample}}_faa.log",
        cdhit_fna_log = f"{OUTPUT_DIR}/14_cdhit/cdhit_{{sample}}_fna.log",
    threads:
        thread_cdhit
    shell:
        """
        echo "Running CD-HIT and CD-HIT-EST for {wildcards.sample}...";
        cd-hit \
        -i {input.faa} \
        -o {output.cdhit_faa} \
        -c 0.95 \
        -T {thread_cdhit} \
        -M {mem_cdhit} \
        > {output.cdhit_faa_log} 2>&1;
        cd-hit-est \
        -i {input.fna} \
        -o {output.cdhit_fna} \
        -c 0.95 \
        -T {thread_cdhit} \
        -M {mem_cdhit} \
        > {output.cdhit_fna_log} 2>&1;
        echo "Finished CD-HIT and CD-HIT-EST completed for {wildcards.sample}!";
        """