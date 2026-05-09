rule busco_bins:
    """
    BUSCO genome-mode quality assessment on each MetaBAT2 bin.
    Uses --auto-lineage-prok to automatically select the best prokaryotic lineage
    (requires internet access on first run to download the lineage database).
    Lineage data is cached under /ProjectM/busco_downloads/.
    Produces a short_summary per bin and an aggregated TSV report.
    """
    input:
        depth   = f"{OUTPUT_DIR}/21_mag_bins/{{group}}/depth.txt",
        mag_log = f"{OUTPUT_DIR}/21_mag_bins/{{group}}/mag_bin.log"
    output:
        log    = f"{OUTPUT_DIR}/22_busco/{{group}}/busco.log",
        report = f"{OUTPUT_DIR}/22_busco/{{group}}/busco_summary.tsv"
    params:
        bins_dir = lambda wildcards: f"{OUTPUT_DIR}/21_mag_bins/{wildcards.group}/bins",
        out_dir  = lambda wildcards: f"{OUTPUT_DIR}/22_busco/{wildcards.group}"
    threads: thread_megahit
    run:
        import os, glob

        os.makedirs(params.out_dir, exist_ok=True)
        log_file    = output.log
        report_file = output.report

        shell(f"echo 'BUSCO assessment for group {wildcards.group}' > {log_file}")

        bins = sorted(glob.glob(f"{params.bins_dir}/*.fa"))
        shell(f"echo 'Found {len(bins)} bin(s)' >> {log_file}")

        if not bins:
            shell(f"echo 'No bins found, skipping BUSCO.' >> {log_file}")
            shell(f"echo -e 'bin\tComplete\tSingle\tDuplicated\tFragmented\tMissing\tTotal' > {report_file}")
        else:
            shell(f"echo -e 'bin\tComplete\tSingle\tDuplicated\tFragmented\tMissing\tTotal' > {report_file}")
            for bin_fa in bins:
                bin_name = os.path.basename(bin_fa).replace('.fa', '')
                shell(
                    f"echo 'Running BUSCO on {bin_name}...' >> {log_file}; "
                    f"micromamba run -n busco busco "
                    f"  -i {bin_fa} "
                    f"  -m genome "
                    f"  --auto-lineage-prok "
                    f"  -o {bin_name} "
                    f"  --out_path {params.out_dir} "
                    f"  --download_path /ProjectM/busco_downloads "
                    f"  --cpu {threads} "
                    f"  --force "
                    f"  >> {log_file} 2>&1 || echo 'BUSCO failed for {bin_name}' >> {log_file}"
                )
                # Extract metrics from short_summary and append to report
                summary_glob = (
                    f"{params.out_dir}/{bin_name}/short_summary*.txt "
                    f"{params.out_dir}/{bin_name}/short_summary.*.{bin_name}.txt"
                )
                shell(
                    f"summary=$(ls {params.out_dir}/{bin_name}/short_summary*.txt 2>/dev/null | head -1); "
                    f"if [ -n \"$summary\" ]; then "
                    f"  C=$(grep -oP '(?<=C:)[0-9.]+' $summary | head -1); "
                    f"  S=$(grep -oP '(?<=S:)[0-9.]+' $summary | head -1); "
                    f"  D=$(grep -oP '(?<=D:)[0-9.]+' $summary | head -1); "
                    f"  F=$(grep -oP '(?<=F:)[0-9.]+' $summary | head -1); "
                    f"  M=$(grep -oP '(?<=M:)[0-9.]+' $summary | head -1); "
                    f"  T=$(grep -oP '(?<=n:)[0-9]+' $summary | head -1); "
                    f"  echo -e '{bin_name}\t$C\t$S\t$D\t$F\t$M\t$T' >> {report_file}; "
                    f"else "
                    f"  echo -e '{bin_name}\tNA\tNA\tNA\tNA\tNA\tNA' >> {report_file}; "
                    f"fi"
                )

        shell(f"echo 'BUSCO assessment complete.' >> {log_file}")
