# Tools

## DRAGEN germline

|  Item | Details |
|---|---|
|  Description | Perform alignment and variant calling on germline WGS data. |
| Official documentation | https://sapac.illumina.com/products/by-type/informatics-products/dragen-bio-it-platform.html |
| License | Paid - see documentation |

**Launch instructions**

Note: The GIS team are launching DRAGEN as a workflow from the [Illumina Connected Analytics](https://sapac.illumina.com/products/by-type/informatics-products/connected-analytics.html) platform (ICA). We're providing the launch settings for reference below.

```bash
# launch settings
/opt/edico/bin/dragen \
    --lic-server `cat "$(inputs.license.path)"` \
    -f \
    -r /ephemeral/ref \
    --fastq-list "$(runtime.outdir)/fastq_list.csv" \
    --output-file-prefix "$(inputs.outprefix)" \
    --output-directory "." \
    --intermediate-results-dir /ephemeral/intermediate \
    --output-format CRAM \
    --enable-sort true \
    --enable-duplicate-marking true \
    --enable-map-align true \
    --enable-map-align-output true \
    --enable-variant-caller true \
    --enable-vcf-compression true \
    --vc-emit-ref-confidence GVCF \
    --vc-enable-vcf-output true \
    --vc-enable-joint-detection true \
    --enable-metrics-json true \
    --gc-metrics-enable true \
    --qc-coverage-region-1 "$(inputs.autosomes.path)" \
    --qc-coverage-reports-1 overall_mean_cov hist contig_mean_cov cov_report callability \
    --qc-coverage-filters-1 'mapq<11,bq<0' \
    --enable-sv true \
    --enable-cnv true \
    --cnv-enable-self-normalization true \
    --cnv-segmentation-mode slm \
    --auto-detect-sample-sex true \
    --vc-enable-roh true \
    --enable-cyp2d6 true \
    --repeat-genotype-enable true \
    --repeat-genotype-specs /opt/edico/repeat-specs/experimental/smn-catalog.hg38.json \
    --qc-cross-cont-vcf /opt/edico/config/sample_cross_contamination_resource_hg38.vcf.gz
```

## Cyrius

|  Item | Details |
|---|---|
|  Description | WGS-based CYP2D6 genotyper. |
| Official documentation | https://github.com/Illumina/Cyrius |
| License | SPDX:Apache-2.0 |

**Launch instructions**

```bash
# build docker image
# run from root directory in this repository
docker build -t cyrius:1.1.1 tools/cyrius/1.1.1/

# prepare input files
# run from root directory in shared S3 bucket
WORKDIR="concept/NA12878-DRAGENv3.7.6-Cyrius_v1.1.1"
mkdir $WORKDIR
ln reference/hg38.fasta $WORKDIR
ln reference/hg38.fasta.fai $WORKDIR
ln concept/NA12878-DRAGENv3.7.6/NA12878.cram $WORKDIR
ln concept/NA12878-DRAGENv3.7.6/NA12878.cram.crai $WORKDIR
echo "/data/NA12878.cram" > $WORKDIR/manifest.txt

# run cyrius
cd $WORKDIR
docker run -it -v `pwd`:/data cyrius:1.1.1 star_caller.py \
    --manifest manifest.txt \
    --genome 38 \
    --reference hg38.fasta \
    --prefix NA12878 \
    --outDir ./

# (optional) tidy up workdir by removing hard links
ls -l | grep -v '^total' | awk '$2>1 {print $NF}' | xargs rm
```

## aldy

|  Item | Details |
|---|---|
|  Description | A quick and nifty tool for genotyping and phasing popular pharmacogenes. |
| Official documentation | https://github.com/0xTCG/aldy |
| License | Paid for commercial use - see documentation |

**Launch instructions**

```bash
# build docker image
# run from root directory in this repository
docker build -t aldy:3.3 tools/aldy/3.3

# prepare input files
# run from root directory in shared S3 bucket
WORKDIR="concept/NA12878-DRAGENv3.7.6-aldy_v3.3"
mkdir $WORKDIR
ln reference/hg38.fasta $WORKDIR
ln reference/hg38.fasta.fai $WORKDIR
ln concept/NA12878-DRAGENv3.7.6/NA12878.cram $WORKDIR
ln concept/NA12878-DRAGENv3.7.6/NA12878.cram.crai $WORKDIR

# run cyrius
cd $WORKDIR
docker run -it -v `pwd`:/data aldy:3.3 aldy genotype \
    --profile illumina \
    --gene CYP2D6 \
    --reference hg38.fasta \
    --output NA12878-CYP2D6.aldy \
    NA12878.cram

# (optional) tidy up workdir by removing hard links
ls -l | grep -v '^total' | awk '$2>1 {print $NF}' | xargs rm
```