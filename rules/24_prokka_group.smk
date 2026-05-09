rule prokka_group:
    """
    Prokka functional annotation of the group-level MEGAHIT assembly.
    Uses --metagenome flag (activates Prodigal meta mode, improves sensitivity).
    Outputs: GFF3, GenBank, protein FASTA, nucleotide FASTA, annotation summary.
    """
    input:
        assembly = f"{OUTPUT_DIR}/15_megahit_group/{{group}}/final.contigs.fa"
    output:
        gff = f"{OUTPUT_DIR}/24_prokka/{{group}}/{{group}}.gff",
        faa = f"{OUTPUT_DIR}/24_prokka/{{group}}/{{group}}.faa",
        txt = f"{OUTPUT_DIR}/24_prokka/{{group}}/{{group}}.txt",
        log = f"{OUTPUT_DIR}/24_prokka/{{group}}/prokka.log"
    params:
        out_dir = lambda wildcards: f"{OUTPUT_DIR}/24_prokka/{wildcards.group}"
    threads: thread_prodigal
    shell:
        """
        echo "Running Prokka annotation for group {wildcards.group}...";
        micromamba run -n prokka prokka \
            --metagenome \
            --outdir {params.out_dir} \
            --prefix {wildcards.group} \
            --cpus {threads} \
            --force \
            {input.assembly} \
            > {output.log} 2>&1;
        echo "Prokka annotation complete for group {wildcards.group}!";
        """
