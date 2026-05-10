rule prodigal:
    input:
        contigs = f"{OUTPUT_DIR}/11_megahit/{{sample}}_contigs.fa",
    output:
        prodigal_gff = f"{OUTPUT_DIR}/12_prodigal/{{sample}}_genes.gff",
        prodigal_faa = f"{OUTPUT_DIR}/12_prodigal/{{sample}}_genes.faa",
        prodigal_fna = f"{OUTPUT_DIR}/12_prodigal/{{sample}}_genes.fna",
        prodigal_log = f"{OUTPUT_DIR}/12_prodigal/prodigal_{{sample}}.log"
    threads:
        thread_prodigal
    shell:
        """
        echo "Running Prodigal for {wildcards.sample}...";
        prodigal \
        -i {input.contigs} \
        -a {output.prodigal_faa} \
        -d {output.prodigal_fna} \
        -f gff \
        -o {output.prodigal_gff} \
        -p meta \
        > {output.prodigal_log} 2>&1;
        echo "Finished Prodigal for {wildcards.sample}!";
        """