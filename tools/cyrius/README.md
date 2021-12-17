# Cyrius

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

# run tool
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
