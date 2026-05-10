rule mag_bin:
    """
    MAG binning per group:
      1. BWA index the group assembly
      2. Map each group sample's clean reads (post-phix removal) → sorted BAM
      3. jgi_summarize_bam_contig_depths → contig depth profile
      4. MetaBAT2 → bins written to  21_mag_bins/{group}/bins/
    """
    input:
        assembly = f"{OUTPUT_DIR}/15_megahit_group/{{group}}/final.contigs.fa",
        reads_r1 = lambda wildcards: [
            f"{OUTPUT_DIR}/05_bwa_phix/{s}_1.fastq.gz"
            for s in group_dict[wildcards.group]
        ],
        reads_r2 = lambda wildcards: [
            f"{OUTPUT_DIR}/05_bwa_phix/{s}_2.fastq.gz"
            for s in group_dict[wildcards.group]
        ]
    output:
        depth = f"{OUTPUT_DIR}/21_mag_bins/{{group}}/depth.txt",
        log   = f"{OUTPUT_DIR}/21_mag_bins/{{group}}/mag_bin.log"
    params:
        samples  = lambda wildcards: group_dict[wildcards.group],
        bam_dir  = lambda wildcards: f"{OUTPUT_DIR}/21_mag_bins/{wildcards.group}/bams",
        bins_dir = lambda wildcards: f"{OUTPUT_DIR}/21_mag_bins/{wildcards.group}/bins"
    threads: thread_bwa
    run:
        import os
        os.makedirs(params.bam_dir, exist_ok=True)
        os.makedirs(params.bins_dir, exist_ok=True)

        log_file = output.log
        assembly = input.assembly

        shell(f"echo 'Indexing {wildcards.group} assembly...' > {log_file}")
        shell(f"bwa index {assembly} >> {log_file} 2>&1")

        bam_files = []
        for sample in params.samples:
            r1  = f"{OUTPUT_DIR}/05_bwa_phix/{sample}_1.fastq.gz"
            r2  = f"{OUTPUT_DIR}/05_bwa_phix/{sample}_2.fastq.gz"
            bam = f"{params.bam_dir}/{sample}.bam"
            shell(
                f"echo 'Mapping {sample}...' >> {log_file}; "
                f"bwa mem -t {threads} {assembly} {r1} {r2} 2>> {log_file} | "
                f"samtools sort -@ {threads} -o {bam}; "
                f"samtools index {bam}"
            )
            bam_files.append(bam)

        bam_str = " ".join(bam_files)
        shell(
            f"echo 'Calculating contig depths...' >> {log_file}; "
            f"jgi_summarize_bam_contig_depths --outputDepth {output.depth} "
            f"{bam_str} >> {log_file} 2>&1"
        )

        shell(
            f"echo 'Running MetaBAT2...' >> {log_file}; "
            f"metabat2 -i {assembly} -a {output.depth} "
            f"-o {params.bins_dir}/bin -t {threads} >> {log_file} 2>&1 || "
            f"echo 'MetaBAT2: no bins produced (contigs may be too short or depth insufficient)' >> {log_file}"
        )

        n_bins = len([f for f in os.listdir(params.bins_dir) if f.endswith('.fa')])
        shell(f"echo 'MetaBAT2 produced {n_bins} bin(s) in {params.bins_dir}' >> {log_file}")
