# StellarPGx

|  Item | Details |
|---|---|
|  Description | Calling star alleles in highly polymorphic pharmacogenes by leveraging genome graph-based variant detection. |
| Official documentation | https://github.com/SBIMB/StellarPGx |
| License | MIT |

**Launch instructions**

**IMPORTANT:** Launching StellarPGx from a docker container requires the `--privileged` argument. Please consider security implications if ever planning to use this code in production.

```bash
# build docker image
# run from root directory in this repository
docker build -t stellarpgx:1.2.5 tools/stellarpgx/1.2.5/

# prepare input files
# run from root directory in shared S3 bucket
WORKDIR="concept/NA12878-DRAGENv3.7.6-stellarpgx_v1.2.5"
# check that nextflow config exists
ls $WORKDIR/nextflow.config
# link remaining inputs
ln reference/hg38.fasta $WORKDIR
ln reference/hg38.fasta.fai $WORKDIR
ln concept/NA12878-DRAGENv3.7.6/NA12878.cram $WORKDIR
ln concept/NA12878-DRAGENv3.7.6/NA12878.cram.crai $WORKDIR

# run tool
cd $WORKDIR
docker run --privileged -it -v `pwd`:/data stellarpgx:1.2.5 nextflow run main.nf \
    -profile standard \
    -c /data/nextflow.config \
    --format compressed \
    --build hg38 \
    --gene cyp2d6

# (optional) tidy up workdir by removing hard links
ls -l | grep -v '^total' | awk '$2>1 {print $NF}' | grep -v results | xargs rm
```
