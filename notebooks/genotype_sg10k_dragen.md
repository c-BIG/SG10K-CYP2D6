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

## Troubleshooting failed executions

### aldy: WHB3694

```bash
cd /data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/call_haplotypes/troubleshooting/WHB3694/

# prepare work dir
aws s3 cp s3://sg10k-reanalysis-dev-s3-1/WHB3694/4819db9f-1eaf-43ef-9324-bd32a5321aed/output/try-1/WHB3694.cram ./
# BLOCKED
# warning: Skipping file s3://sg10k-reanalysis-dev-s3-1/WHB3694/4819db9f-1eaf-43ef-9324-bd32a5321aed/output/try-1/WHB3694.cram. Object is of storage class GLACIER. Unable to perform download operations on GLACIER objects. You must restore the object to be able to perform the operation. See aws s3 download help for additional parameter options to ignore or force these transfers.
aws s3 cp s3://sg10k-reanalysis-dev-s3-1/WHB3694/4819db9f-1eaf-43ef-9324-bd32a5321aed/output/try-1/WHB3694.cram.crai ./
ln /data/SG10K-CYP2D6/s3/sg10k-cyp2d6/reference/hg38.fasta ./
ln /data/SG10K-CYP2D6/s3/sg10k-cyp2d6/reference/hg38.fasta.fai ./

# run aldy (see SG10K-CYP2D6/tools/aldy/README.md)
docker run -it -v `pwd`:/data aldy:3.3 aldy genotype \
    --profile illumina \
    --gene CYP2D6 \
    --reference hg38.fasta \
    --output WHB3694.aldy \
    WHB3694.cram

# manual execution completed successfully
# upload results to s3
cp WHB3694.aldy \
    /data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/outputs/WHB3694/aldy/
aws s3 sync \
    /data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/outputs/WHB3694/aldy/ \
    s3://sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/outputs/WHB3694/aldy/
```

### aldy: WHB4149

Manually launch following instructions above

```bash
# manual execution completed with an error
# upload logs to s3 and notify authors
aws s3 sync /data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/outputs/WHB4149/aldy/ \
s3://sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/outputs/WHB4149/aldy/
```

### aldy: WHB4689

Manually launch following instructions above

```bash
# manual execution completed successfully
# upload results to s3
cp WHB4689.aldy \
    /data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/outputs/WHB4689/aldy/
aws s3 sync \
    /data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/outputs/WHB4689/aldy/ \
    s3://sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/outputs/WHB4689/aldy/
```

### Cyrius: WHB3978

```bash
cd /data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/call_haplotypes/troubleshooting/WHB3978

# prepare work dir
aws s3 cp s3://sg10k-reanalysis-dev-s3-1/WHB3978/a3067955-ea43-40d6-94f7-e25c8f3b08f6/output/try-1/WHB3978.cram ./
# BLOCKED
# warning: Skipping file s3://sg10k-reanalysis-dev-s3-1/WHB3978/a3067955-ea43-40d6-94f7-e25c8f3b08f6/output/try-1/WHB3978.cram. Object is of storage class GLACIER. Unable to perform download operations on GLACIER objects. You must restore the object to be able to perform the operation. See aws s3 download help for additional parameter options to ignore or force these transfers
aws s3 cp s3://sg10k-reanalysis-dev-s3-1/WHB3978/a3067955-ea43-40d6-94f7-e25c8f3b08f6/output/try-1/WHB3978.cram.crai ./
ln /data/SG10K-CYP2D6/s3/sg10k-cyp2d6/reference/hg38.fasta ./
ln /data/SG10K-CYP2D6/s3/sg10k-cyp2d6/reference/hg38.fasta.fai ./
echo "/data/WHB3978.cram" > manifest.txt

# run cyrius (see SG10K-CYP2D6/tools/cyrius/README.md)
docker run -it -v `pwd`:/data cyrius:1.1.1 star_caller.py \
    --manifest manifest.txt \
    --genome 38 \
    --reference hg38.fasta \
    --prefix WHB3978 \
    --outDir ./

# manual execution completed succesfully
# upload results to s3
cp WHB3978.json \
    /data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/outputs/WHB3978/cyrius/
cp WHB3978.tsv \
    /data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/outputs/WHB3978/cyrius/
aws s3 sync \
    /data/SG10K-CYP2D6/s3/sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/outputs/WHB3978/cyrius/ \
    s3://sg10k-cyp2d6-workspace/call_haplotypes/sg10k-dragen/outputs/WHB3978/cyrius/
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
## no failed samples
```

# Step 3: Resolving consensus haplotype calls

*TBD*