# Step 1: Launching Cyrius and aldy (call_haplotypes nextflow workflow)

# Step 2: Launching StellarPGx (launch_stellar_pgx.py)

```bash
## prepare a txt file with a list of input cram files, e.g.
head -2 sg10k_dragen.batch1_100.txt
# s3://sg10k-reanalysis-dev-s3-1/WHB4998/246fdee7-34e1-4f19-8c3a-55b4c5d0a870/output/try-1/WHB4998.cram
# s3://sg10k-reanalysis-dev-s3-1/WHB4305/28d8be0d-1d5b-495e-95b5-0d2839e24c85/output/try-1/WHB4305.cram

## launch python wrapper serially for each of the input files
cat /data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/sg10k_dragen.batch1_100.txt | head -1 | while read input
do
python launch_stellarpgx.py \
    --bam "$input" \
    --ref_fa "/data/SG10K-CYP2D6/s3/sg10k-cyp2d6/reference/hg38.fasta" \
    --out_dir "/data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/launch_stellarpgx" \
    --loglevel "DEBUG"
done > log.out 2> log.err
```

# Step 3: Resolving consensus haplotype calls

*TBD*