# aldy

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

# run tool
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