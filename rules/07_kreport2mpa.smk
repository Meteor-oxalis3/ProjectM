rule kreport2mpa:
    input:
        kraken2_report = f"{OUTPUT_DIR}/06_kraken2/{{sample}}.report"
    output:
        mpa_output = f"{OUTPUT_DIR}/07_kreport2mpa/{{sample}}.mpa",
        kreport2mpa_log = f"{OUTPUT_DIR}/07_kreport2mpa/kreport2mpa_{{sample}}.log",
    shell:
        """
        echo "Running kreport2mpa for {wildcards.sample}...";
        kreport2mpa.py \
        -r {input.kraken2_report} \
        -o {output.mpa_output} \
        --no-intermediate-ranks \
        > {output.kreport2mpa_log} 2>&1;
        echo "Finished kreport2mpa for {wildcards.sample}!"
        """

rule mpa_json:
    input:
        mpa_files = expand(f"{OUTPUT_DIR}/07_kreport2mpa/{{sample}}.mpa", sample=list_ID)
    output:
        mpa_json = f"{OUTPUT_DIR}/07_kreport2mpa/mpa.json"
    run:
        import json
        group_mpa = {
            group: [f"{OUTPUT_DIR}/07_kreport2mpa/{sample}.mpa" for sample in samples]
            for group, samples in group_dict.items()
        }
        with open(output.mpa_json, 'w') as f:
            json.dump(group_mpa, f, indent=4)