# Pipelines

## call_haplotypes

A Nextflow pipeline to launch Cyrius and aldy from an input CRAM file. Requires nextflow and the docker image defined in `call_haplotypes/Dockerfile`. Supports two different launching profiles: `local` and `awsbatch`.

### Running locally

**Deployment**

1. Obtain a copy of the nextflow workflow from the present repository.
2. Build the docker image:

```bash
docker build -t sg10k-cyp2d6-call_haplotypes .
```

**Launch instructions**

*Usage*

```bash
REPO_ROOT="/path/to/this/repo"

nextflow run $REPO_ROOT/pipelines/call_haplotypes/main.nf --help
# N E X T F L O W  ~  version 21.04.3
# Launching `/home/jupyter-mgonzalezporta/workspace/git/SG10K-CYP2D6/pipelines/call_haplotypes/main.nf` [awesome_bernard] - revision: 21f1d56b36

# ==============================================
# call_haplotypes  ~  version 0.3
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
    --cram_list "s3://sg10k-cyp2d6/concept/NA12878-DRAGENv3.7.6-call_haplotypes/v0.3/input_crams.txt" \
    --reference "s3://sg10k-cyp2d6/reference/hg38.fasta" \
    --genome "38" \
    -profile "local" \
    -resume
# N E X T F L O W  ~  version 21.04.3
# Launching `/home/jupyter-mgonzalezporta/workspace/git/SG10K-CYP2D6/pipelines/call_haplotypes/main.nf` [soggy_gutenberg] - revision: 21f1d56b36
# WARN: It appears you have never run this project before -- Option `-resume` is ignored
# executor >  local (2)
# [df/1746d5] process > CYRIUS (NA12878) [100%] 1 of 1 ✔
# [61/df3895] process > ALDY (NA12878)   [100%] 1 of 1 ✔

# ==============================================
# EXECUTION SUMMARY
# ==============================================
# Workflow launched : main.nf 0.3
# Command line      : nextflow run /home/jupyter-mgonzalezporta/workspace/git/SG10K-CYP2D6/pipelines/call_haplotypes/main.nf --cram_list 's3://sg10k-cyp2d6/concept/NA12878-DRAGENv3.7.6-call_haplotypes/v0.3/input_crams.txt' --reference 's3://sg10k-cyp2d6/reference/hg38.fasta' --genome 38 -profile local -resume
# Output directory  : /home/jupyter-mgonzalezporta/test
# Completed at      : 2021-10-07T02:45:09.301310Z
# Duration          : 3m 6s
# Success           : true
# Exit status       : 0

# Completed at: 07-Oct-2021 02:45:09
# Duration    : 3m 6s
# CPU hours   : (a few seconds)
# Succeeded   : 2

## NOTE: remember to remove the work directory when no longer needed

tree .
# .
# ├── info
# │   ├── dag.html
# │   ├── timeline.html
# │   ├── trace.txt
# ├── outputs
# │   └── NA12878
# │       ├── aldy
# │       │   └── NA12878.aldy
# │       └── cyrius
# │           ├── NA12878.json
# │           └── NA12878.tsv
# └── work
#     ├── bb
#     │   └── 2ac0bfcb49c6ab7f371e87d6b7491e
#     │       ├── NA12878.aldy
#     │       ├── NA12878.cram -> /home/jupyter-mgonzalezporta/test/work/stage/82/834c14ecadaa4f9b59aaf92b53cf83/NA12878.cram
#     │       ├── NA12878.cram.crai -> /home/jupyter-mgonzalezporta/test/work/stage/56/a8ee91c874e373ddd06980420d742d/NA12878.cram.crai
#     │       ├── hg38.fasta -> /home/jupyter-mgonzalezporta/test/work/stage/0f/d71f57c98cd73fe3a98dde031384ef/hg38.fasta
#     │       └── hg38.fasta.fai -> /home/jupyter-mgonzalezporta/test/work/stage/a6/7ffcaf91a5a5db551c5b083394318f/hg38.fasta.fai
#     ├── d9
#     │   └── 7f4b5e62b4652b6db790790c9ece44
#     │       ├── NA12878.cram -> /home/jupyter-mgonzalezporta/test/work/stage/82/834c14ecadaa4f9b59aaf92b53cf83/NA12878.cram
#     │       ├── NA12878.cram.crai -> /home/jupyter-mgonzalezporta/test/work/stage/56/a8ee91c874e373ddd06980420d742d/NA12878.cram.crai
#     │       ├── NA12878.json
#     │       ├── NA12878.tsv
#     │       ├── hg38.fasta -> /home/jupyter-mgonzalezporta/test/work/stage/0f/d71f57c98cd73fe3a98dde031384ef/hg38.fasta
#     │       ├── hg38.fasta.fai -> /home/jupyter-mgonzalezporta/test/work/stage/a6/7ffcaf91a5a5db551c5b083394318f/hg38.fasta.fai
#     │       └── manifest.txt
#     └── stage
#         ├── 0f
#         │   └── d71f57c98cd73fe3a98dde031384ef
#         │       └── hg38.fasta
#         ├── 56
#         │   └── a8ee91c874e373ddd06980420d742d
#         │       └── NA12878.cram.crai
#         ├── 82
#         │   └── 834c14ecadaa4f9b59aaf92b53cf83
#         │       └── NA12878.cram
#         └── a6
#             └── 7ffcaf91a5a5db551c5b083394318f
#                 └── hg38.fasta.fai
```

### Running on AWS Batch

**Deployment**

1. Obtain a copy of the nextflow workflow from the present repository.
2. Prepare the docker image:
    1. Build the docker image:
    ```bash
    docker build -t sg10k-cyp2d6-call_haplotypes .
    ```
    2. Create a new ECR repository called `sg10k-cyp2d6-call_haplotypes`.
    3. Push the docker image to the newly created repository. You can follow the instructions displayed in the AWS console.
    4. Add the name of your ECR image to your `nextflow.config` (under `awsbatch` profile > `process.container`).
3. Set up your AWS Batch queue:
    1. Configure a new AWS Batch queue (see [Nextflow manual](https://www.nextflow.io/docs/latest/awscloud.html) for guidance).
    2. Update your `nextflog.config` with the name of your queue (under `awsbatch` profile > `process.queue`).

**Launch instructions**

*Usage*

See above.

*Example run*

```bash
REPO_ROOT="/path/to/this/repo"
LAUNCH_DIR="./test"
cd $LAUNCH_DIR

nextflow run $REPO_ROOT/pipelines/call_haplotypes/main.nf \
    --cram_list "s3://sg10k-cyp2d6/concept/NA12878-DRAGENv3.7.6-call_haplotypes/v0.3/input_crams.txt" \
    --reference "s3://sg10k-cyp2d6/reference/hg38.fasta" \
    --genome "38" \
    -profile "awsbatch" \
    -work-dir "s3://sg10k-cyp2d6-workspace/call_haplotypes/dev/v0.3/work/" \
    -resume
# not run

## NOTE: remember to remove the work directory when no longer needed
```
