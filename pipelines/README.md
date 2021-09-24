# Pipelines

## call_haplotypes

A Nextflow pipeline to launch Cyrius and aldy from an input CRAM file. Requires nextflow and third-party tools defined under `/SG10K-CYP2D6/tools/`.

**Launch instructions**

*Usage*

```bash
REPO_ROOT="/path/to/this/repo"
nextflow run $REPO_ROOT/pipelines/call_haplotypes/main.nf --help

# N E X T F L O W  ~  version 21.04.3
# Launching `/home/jupyter-mgonzalezporta/workspace/git/SG10K-CYP2D6/pipelines/call_haplotypes/main.nf` [lethal_brown] - revision: aeb6541a4f

# ==============================================
# call_haplotypes  ~  version 0.2
# ==============================================

# Mandatory arguments:
# --cram_list   Path to file with list of input crams (one file per line). Note: cram index must be available as <cram>.crai.
# --reference   Path to genome reference. Note: reference index must be available as <fasta>.fai or <fa>.fai.
# --genome      Genome build. One of: 19, 37, 38.

# Additional arguments:
# --help
# --version
```

*Example run*

```bash
REPO_ROOT="/path/to/this/repo"
LAUNCH_DIR="./test"

cd $LAUNCH_DIR
nextflow run $REPO_ROOT/pipelines/call_haplotypes/main.nf \
    --cram_list "s3://sg10k-cyp2d6/concept/NA12878-DRAGENv3.7.6-call_haplotypes/v0.2/input_crams.txt" \
    --reference "s3://sg10k-cyp2d6/reference/hg38.fasta" \
    --genome "38" \
    -profile standard \
    -resume
# N E X T F L O W  ~  version 21.04.3
# Launching `/home/jupyter-mgonzalezporta/workspace/git/SG10K-CYP2D6/pipelines/call_haplotypes/main.nf` [jovial_mccarthy] - revision: aeb6541a4f
# WARN: It appears you have never run this project before -- Option `-resume` is ignored
# executor >  local (2)
# [bd/3acf9f] process > CYRIUS (NA12878) [100%] 1 of 1 ✔
# [fa/eb118f] process > ALDY (NA12878)   [100%] 1 of 1 ✔

# ==============================================
# EXECUTION SUMMARY
# ==============================================
# Workflow launched : main.nf 0.2
# Command line      : nextflow run /home/jupyter-mgonzalezporta/workspace/git/SG10K-CYP2D6/pipelines/call_haplotypes/main.nf --cram_list 's3://sg10k-cyp2d6/concept/NA12878-DRAGENv3.7.6-call_haplotypes/v0.2/input_crams.txt' --reference 's3://sg10k-cyp2d6/reference/hg38.fasta' --genome 38 -profile standard -resume
# Output directory  : /data/SG10K-CYP2D6/sandbox/call_haplotypes_pilot/test
# Completed at      : 2021-09-24T03:38:43.482522Z
# Duration          : 3m 3s
# Success           : true
# Exit status       : 0

tree .
# .
# ├── info
# │   ├── dag.html
# │   ├── timeline.html
# │   └── trace.txt
# ├── input_crams.txt
# ├── outputs
# │   └── NA12878
# │       ├── aldy
# │       │   └── NA12878.aldy
# │       └── cyrius
# │           ├── NA12878.json
# │           └── NA12878.tsv
# └── work
#     ├── bd
#     │   └── 3acf9fa37523a2065f1142afa69e7d
#     │       ├── NA12878.cram -> /data/SG10K-CYP2D6/sandbox/call_haplotypes_pilot/test/work/stage/91/c83cf34c689ea172299f64aca6ecad/NA12878.cram
#     │       ├── NA12878.cram.crai -> /data/SG10K-CYP2D6/sandbox/call_haplotypes_pilot/test/work/stage/1b/824fef9c7d291c805d63ee9e6d62fe/NA12878.cram.crai
#     │       ├── NA12878.json
#     │       ├── NA12878.tsv
#     │       ├── hg38.fasta -> /data/SG10K-CYP2D6/sandbox/call_haplotypes_pilot/test/work/stage/3c/e58f78af82ec0d0dc06a20e1de40fb/hg38.fasta
#     │       ├── hg38.fasta.fai -> /data/SG10K-CYP2D6/sandbox/call_haplotypes_pilot/test/work/stage/08/b6764d6ac6a8857f4b5154d152b525/hg38.fasta.fai
#     │       └── manifest.txt
#     ├── fa
#     │   └── eb118fa7eedfcc294689f02e8f087a
#     │       ├── NA12878.aldy
#     │       ├── NA12878.cram -> /data/SG10K-CYP2D6/sandbox/call_haplotypes_pilot/test/work/stage/91/c83cf34c689ea172299f64aca6ecad/NA12878.cram
#     │       ├── NA12878.cram.crai -> /data/SG10K-CYP2D6/sandbox/call_haplotypes_pilot/test/work/stage/1b/824fef9c7d291c805d63ee9e6d62fe/NA12878.cram.crai
#     │       ├── hg38.fasta -> /data/SG10K-CYP2D6/sandbox/call_haplotypes_pilot/test/work/stage/3c/e58f78af82ec0d0dc06a20e1de40fb/hg38.fasta
#     │       └── hg38.fasta.fai -> /data/SG10K-CYP2D6/sandbox/call_haplotypes_pilot/test/work/stage/08/b6764d6ac6a8857f4b5154d152b525/hg38.fasta.fai
#     └── stage
#         ├── 08
#         │   └── b6764d6ac6a8857f4b5154d152b525
#         │       └── hg38.fasta.fai
#         ├── 1b
#         │   └── 824fef9c7d291c805d63ee9e6d62fe
#         │       └── NA12878.cram.crai
#         ├── 3c
#         │   └── e58f78af82ec0d0dc06a20e1de40fb
#         │       └── hg38.fasta
#         └── 91
#             └── c83cf34c689ea172299f64aca6ecad
#                 └── NA12878.cram
```