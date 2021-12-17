# launch_stellarpgx.py

A Python wrapper to launch StellarPGx from an input CRAM file. Requires the docker image defined in `tools/stellarpgx`. To be launched locally.

**Deployment**

1. Obtain a copy of the `launch_stellarpgx.py` script from the present repository.
2. Build the docker image following the instructions provided in `tools/README.md`.

**Launch instructions**

*Usage*

```bash
python launch_stellarpgx.py -h
usage: launch_stellarpgx.py [-h] --bam BAM [--ref_fa REF_FA]
                            [--out_dir OUT_DIR] [--loglevel LOGLEVEL]

optional arguments:
  -h, --help           show this help message and exit
  --bam BAM            Path to input BAM or CRAM. Default: None.
  --ref_fa REF_FA      Path to genome fasta. Default: None.
  --out_dir OUT_DIR    Path to output directory (also used as work directory).
                       Default: ./
  --loglevel LOGLEVEL  Set logging level to INFO (default), WARNING or DEBUG.
```

*Example run*

```bash
python launch_stellarpgx.py \
    --bam NA12878.cram \
    --ref_fa hg38.fasta \
    --out_dir ./NA12878-test/ \
    --loglevel DEBUG
```