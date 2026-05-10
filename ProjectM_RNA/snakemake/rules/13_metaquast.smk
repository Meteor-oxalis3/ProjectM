rule metaquast:
    input:
        contigs = f"{OUTPUT_DIR}/11_megahit/{{sample}}_contigs.fa",
    output:
        metaquast_log = f"{OUTPUT_DIR}/13_metaquast/metaquast_{{sample}}.log"
    threads:
        thread_metaquast
    shell:
        """
        echo "Running metaQUAST for {wildcards.sample}...";
        mkdir -p {OUTPUT_DIR}/13_metaquast/{wildcards.sample};
        metaquast.py \
        {input.contigs} \
        -r {METAQUAST_DB_SILVA_DIR} \
        --threads {thread_metaquast} \
        -o {OUTPUT_DIR}/13_metaquast/{wildcards.sample}/ \
        > {output.metaquast_log} 2>&1;
        echo "Finished metaQUAST for {wildcards.sample}!";
        """