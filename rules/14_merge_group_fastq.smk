rule merge_group_fastq:
    output:
        merged_fastq1 = f"{OUTPUT_DIR}/14_megahit_merged/{{group}}_merged_1.fastq.gz",
        merged_fastq2 = f"{OUTPUT_DIR}/14_megahit_merged/{{group}}_merged_2.fastq.gz",
    run:
        import glob
        import os
        group_samples = group_dict[wildcards.group]
        merged_fastq1_files = [f"{OUTPUT_DIR}/05_bwa_phix/{sample}_1.fastq.gz" for sample in group_samples]
        merged_fastq2_files = [f"{OUTPUT_DIR}/05_bwa_phix/{sample}_2.fastq.gz" for sample in group_samples]
        with open(output.merged_fastq1, 'wb') as wfd:
            for f in merged_fastq1_files:
                with open(f, 'rb') as fd:
                    wfd.write(fd.read())
        with open(output.merged_fastq2, 'wb') as wfd:
            for f in merged_fastq2_files:
                with open(f, 'rb') as fd:
                    wfd.write(fd.read())