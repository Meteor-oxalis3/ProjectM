rule krona:
    input:
        kraken2_report = f"{OUTPUT_DIR}/06_kraken2/{{sample}}.report"
    output:
        krona_file = f"{OUTPUT_DIR}/13_krona/{{sample}}.krona",
        krona_html = f"{OUTPUT_DIR}/13_krona/{{sample}}_krona.html",
        krona_log = f"{OUTPUT_DIR}/13_krona/krona_{{sample}}.log"
    shell:
        """
        echo "Running krona...";
        (kreport2krona.py -r {input.kraken2_report} -o {output.krona_file};\
        ktImportText {output.krona_file} -o {output.krona_html}) > {output.krona_log} 2>&1;
        echo "Finished krona for {wildcards.sample}!"
        """