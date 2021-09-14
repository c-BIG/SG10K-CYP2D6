# Pipelines

## call_haplotypes

A Nextflow pipeline to launch Cyrius and aldy from an input CRAM file. Depends on third-party tools defined under `/SG10K-CYP2D6/tools/`.

**Launch instructions**

*Usage*

```bash
REPO_ROOT="/path/to/this/repo"
nextflow run $REPO_ROOT/pipelines/call_haplotypes/main.nf --help

# N E X T F L O W  ~  version 21.04.3
# Launching `/path/to/this/repo/pipelines/call_haplotypes/main.nf` [soggy_murdock] - revision: f60368ff45

# ==============================================
# call_haplotypes  ~  version 0.1
# ==============================================

# Mandatory arguments:
# --cram       Path to input cram. Note: cram index must be available in the same directory.
# --reference  Path to genome reference. Note: reference index must be available in the same directory.
# --genome     Genome build. One of: 19, 37, 38.

# Additional arguments:
# --help
# --version
```

*Example run*

```bash
REPO_ROOT="/path/to/this/repo"
DATA_ROOT="/path/to/shared/s3/"
LAUNCH_DIR="./test_20210914"

cd $LAUNCH_DIR
nextflow run $REPO_ROOT/pipelines/call_haplotypes/main.nf \
    --cram "$DATA_ROOT/concept/NA12878-DRAGENv3.7.6/NA12878.cram" \
    --reference "$DATA_ROOT/reference/hg38.fasta" \
    --genome "38" \
    -resume

# N E X T F L O W  ~  version 21.04.3
# Launching `/path/to/this/repo/pipelines/call_haplotypes/main.nf` [spontaneous_yalow] - revision: f60368ff45
# executor >  local (2)
# [7b/89a8d3] process > CYRIUS (NA12878) [100%] 1 of 1 ✔
# [1d/1374d6] process > ALDY (NA12878)   [100%] 1 of 1 ✔

# ==============================================
# EXECUTION SUMMARY
# ==============================================
# Workflow launched : main.nf 0.1
# Command line      : nextflow run /path/to/this/repo/pipelines/call_haplotypes/main.nf --cram /path/to/shared/s3/concept/NA12878-DRAGENv3.7.6/NA12878.cram --reference /path/to/shared/s3/reference/hg38.fasta --genome 38 -resume
# Output directory  : ./test_20210914
# Completed at      : 2021-09-14T01:42:26.527Z
# Duration          : 2m 23s
# Success           : true
# Exit status       : 0

tree .
# .
# ├── info
# │   ├── dag.html
# │   ├── timeline.html
# │   └── trace.txt
# ├── outputs
# │   ├── aldy
# │   │   └── NA12878.aldy
# │   └── cyrius
# │       ├── NA12878.json
# │       └── NA12878.tsv
# └── work
#     ├── 1d
#     │   └── 1374d6efb2c792898a52e0a47b0545
#     │       ├── NA12878.aldy
#     │       ├── NA12878.cram -> /path/to/shared/s3/concept/NA12878-DRAGENv3.7.6/NA12878.cram
#     │       ├── NA12878.cram.crai -> /path/to/shared/s3/concept/NA12878-DRAGENv3.7.6/NA12878.cram.crai
#     │       ├── hg38.fasta -> /path/to/shared/s3/reference/hg38.fasta
#     │       └── hg38.fasta.fai -> /path/to/shared/s3/reference/hg38.fasta.fai
#     └── 7b
#         └── 89a8d383090f313fdde69eb0cc8227
#             ├── NA12878.cram -> /path/to/shared/s3/concept/NA12878-DRAGENv3.7.6/NA12878.cram
#             ├── NA12878.cram.crai -> /path/to/shared/s3/concept/NA12878-DRAGENv3.7.6/NA12878.cram.crai
#             ├── NA12878.json
#             ├── NA12878.tsv
#             ├── hg38.fasta -> /path/to/shared/s3/reference/hg38.fasta
#             ├── hg38.fasta.fai -> /path/to/shared/s3/reference/hg38.fasta.fai
#             └── manifest.txt
```