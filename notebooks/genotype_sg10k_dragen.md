# Step 1: Launching Cyrius and aldy (call_haplotypes nextflow workflow)

```bash
## prepare a txt file with a list of input cram files, e.g.
head -2 sg10k_dragen.batch1_100.txt
# s3://sg10k-reanalysis-dev-s3-1/WHB4998/246fdee7-34e1-4f19-8c3a-55b4c5d0a870/output/try-1/WHB4998.cram
# s3://sg10k-reanalysis-dev-s3-1/WHB4305/28d8be0d-1d5b-495e-95b5-0d2839e24c85/output/try-1/WHB4305.cram

## launch the nextflow workflow
nextflow run /home/jupyter-mgonzalezporta/workspace/git/SG10K-CYP2D6/pipelines/call_haplotypes/main.nf \
    --cram_list "/data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/sg10k_dragen.batch1_100.txt" \
    --reference "/data/SG10K-CYP2D6/s3/sg10k-cyp2d6/reference/hg38.fasta" \
    --genome "38" \
    -work-dir "s3://sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/work" \
    -profile "awsbatch" \
    -resume

## IMPORTANT! Remove contents of the work directory when done

## sanity check: aldy
## check that outputs are not empty
ls */aldy/*.aldy | sort | while read line
do
    n=$(cat $line | grep '#Solution' | wc -l)
    echo "$line,$n"
done > aldy.done
## failed samples
cat aldy.done | grep ',0'
WHB3694/aldy/WHB3694.aldy,0
WHB4149/aldy/WHB4149.aldy,0
WHB4689/aldy/WHB4689.aldy,0

## sanity check: cyrius
## check that outputs are not empty
ls */cyrius/*.tsv | sort | while read line
do
    n=$(cat $line | grep '^W' | wc -l)
    echo "$line,$n"
done > cyrius.done
## failed samples
cat cyrius.done | grep ',0'
WHB3978/cyrius/WHB3978.tsv,0
```

# Step 2: Launching StellarPGx (launch_stellar_pgx.py)

```bash
## prepare a txt file with a list of input cram files, e.g.
head -2 sg10k_dragen.batch1_100.txt
# s3://sg10k-reanalysis-dev-s3-1/WHB4998/246fdee7-34e1-4f19-8c3a-55b4c5d0a870/output/try-1/WHB4998.cram
# s3://sg10k-reanalysis-dev-s3-1/WHB4305/28d8be0d-1d5b-495e-95b5-0d2839e24c85/output/try-1/WHB4305.cram

## launch python wrapper serially for each of the input files
cat /data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/launch_stellarpgx/sg10k-dragen/sg10k_dragen.batch1_100.txt | while read input
do
    sample_id=$(echo $input | awk -F '/' '{print $NF}' | sed 's/.cram//g')
    echo ">>> Processing $sample_id"
    out_dir="/data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/launch_stellarpgx/sg10k-dragen/outputs/$sample_id"
    mkdir -p $out_dir
    time python launch_stellarpgx.py \
        --bam "$input" \
        --ref_fa "/data/SG10K-CYP2D6/s3/sg10k-cyp2d6/reference/hg38.fasta" \
        --out_dir "$out_dir" \
        --loglevel "DEBUG" \
        --goofys "/home/jupyter-mgonzalezporta/workspace/tools/goofys/goofys" \
        > $out_dir/log.out 2> "$out_dir"/log.err
done

## sanity checks: stellarpgx
## check that outputs are not empty
ls /data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/launch_stellarpgx/sg10k-dragen/outputs/*/results/cyp2d6/alleles/*_cyp2d6.alleles | while read line
do
    n=$(cat $line | grep -A1 '^Result:' | grep -v 'Result' | wc -l)
    echo "$line,$n"
done > stellarpgx.done
## failed samples
cat stellarpgx.done | grep -v ',1'
```

# Step 3: Resolving consensus haplotype calls

*TBD*