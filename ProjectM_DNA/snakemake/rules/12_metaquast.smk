rule metaquast:
    input:
        contigs = f"{OUTPUT_DIR}/10_megahit/{{sample}}_contigs.fa",
    output:
        metaquast_log = f"{OUTPUT_DIR}/12_metaquast/metaquast_{{sample}}.log"
    threads:
        thread_metaquast
    shell:
        """
        echo "Running metaQUAST for {wildcards.sample}...";
        mkdir -p {OUTPUT_DIR}/12_metaquast/{wildcards.sample};
        metaquast.py \
        {input.contigs} \
        --threads 4 \
        -o {OUTPUT_DIR}/12_metaquast/{wildcards.sample}/ \
        > {output.metaquast_log} 2>&1 || \
        (echo "metaQUAST failed (exit $?), skipped." >> {output.metaquast_log}; \
         touch {output.metaquast_log});
        echo "Finished metaQUAST for {wildcards.sample}!";
        """