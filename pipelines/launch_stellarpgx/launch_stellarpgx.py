#!/usr/bin/env python3
# Requires python 3.10 or above

import logging
import argparse
import subprocess
from pathlib import Path


NF_CONFIG_TEMPLATE = """
manifest {
    author = 'launch_stellarpgx.py'
    description = 'Pipeline calls CYP450 star alleles from WGS BAM/CRAM files. Model gene: CYP2D6'
    mainScript = 'main.nf'
    version = '1.2.5'
}

params {
    // User-defined parameters

    // reference genome
    ref_file = '<REF_FILE>'  // .fai index should be in the same folder

    // BAM/CRAM file(s) and respective indexes
    in_bam = '<IN_BAM>'

    // Output directoy (Default is $PWD/results). User-defined path should be an absolute path
    out_dir = '<OUT_DIR>'

    // DO NOT modify these lines
    gene = "cyp2d6"
    db_init = "$PWD/database"
    res_init = "$PWD/resources"
    caller_init = "$PWD/scripts"
}

singularity {
    enabled = true // set to false when using Docker
    autoMounts = true
    cacheDir = "$PWD/containers"
    runOptions = " --cleanenv"
}

process {
    // ALL PROCESSES
    cache = true
    stageInMode = 'symlink'
    stageOutMode = 'rsync'

    // Singularity
    container = "$PWD/containers/stellarpgx-dev.sif"
}

profiles {
    // Local machine (MacOS, Linux, cluster node etc)
    standard {
        process.executor = 'local'
    }
}
"""


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--bam", required=True, default=None,
                        help="Path to input BAM or CRAM. Default: None.")
    parser.add_argument("--ref_fa", required=False, default=None,
                        help="Path to genome fasta. Default: None.")
    parser.add_argument("--out_dir", required=False, default=".",
                        help="Path to output directory (also used as work directory). Default: ./")
    parser.add_argument("--tidy", required=False, default=True,
                        help="Remove temporary files from output directory. Default: True")
    parser.add_argument("--loglevel", required=False, default="INFO",
                        help="Set logging level to INFO (default), WARNING or DEBUG.")
    args = parser.parse_args()

    set_logging(args.loglevel)

    args.sample_id = Path(args.bam).stem
    args.input_suffix = Path(args.bam).suffix

    # stage s3 files locally
    if "s3" in args.bam:
        # update args to reflect local path
        bam_name = Path(args.bam).name
        args.bam = Path(f"{args.out_dir}/{bam_name}")
        # stage if file not already available locally
        if Path(args.bam).exists():
            logging.info(f"S3 path detected, local copy already available: {args.bam}")
        else:
            logging.info(f"S3 path detected, staging inputs: {args.bam}")
            cmd = f"aws s3 cp {args.bam} {args.out_dir}"
            try_run_command(cmd=cmd, cwd=args.out_dir)
            if args.input_suffix == ".bam":
                cmd = f"aws s3 cp {args.bam}.bai {args.out_dir}"
                try_run_command(cmd=cmd, cwd=args.out_dir)
            elif args.input_suffix == ".cram":
                cmd = f"aws s3 cp {args.bam}.crai {args.out_dir}"
                try_run_command(cmd=cmd, cwd=args.out_dir)

    if not Path(args.bam).exists():
        logging.error(f"Couldn't find input file: {args.bam}")
        exit(1)

    if not Path(args.ref_fa).exists():
        logging.error(f"Couldn't find input file: {args.ref_fa}")
        exit(1)

    # done
    return args


def set_logging(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {loglevel}")
    logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", level=numeric_level)


def try_run_command(cmd, cwd, return_stdout=False):
    logging.debug(f"CMD: {cmd}; CWD: {cwd}")
    try:
        if return_stdout:
            p = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE)
            stdout = p.stdout.read().decode("utf-8").strip()
            return stdout
        else:
            p = subprocess.run(cmd, shell=True, cwd = cwd)
    except:
        logging.error(f"Error when running command: {cmd}")
        exit(1)


def prepare_stellarpgx_inputs(args):
    logging.info("Preparing StellarPGx inputs...")

    # input files: reference and index
    ref_fa_name = Path(args.ref_fa).name
    # note: requires python 3.10+
    Path(f"{args.out_dir}/{ref_fa_name}").hardlink_to(args.ref_fa)
    Path(f"{args.out_dir}/{ref_fa_name}.fai").hardlink_to(f"{args.ref_fa}.fai")
    nf_fa = f"/data/{ref_fa_name}"

    # input files: bam/cram and index
    # note: hardlinks are not needed because we'll call subprocess from out_dir
    bam_name = Path(args.bam).name
    if args.input_suffix == ".bam":
        # Path(f"{args.out_dir}/{bam_name}").hardlink_to(args.bam)
        # Path(f"{args.out_dir}/{bam_name}.bai").hardlink_to(f"{args.bam}.bai")
        nf_bam = f"/data/%s" % bam_name.replace(".bam", ".*{bam,bai}")
    elif args.input_suffix == ".cram":
        # Path(f"{args.out_dir}/{bam_name}").hardlink_to(args.bam)
        # Path(f"{args.out_dir}/{bam_name}.crai").hardlink_to(f"{args.bam}.crai")
        nf_bam = f"/data/%s" % bam_name.replace(".cram", ".*{cram,crai}")
    else:
        logging.error("Unrecognised input file type; must be .bam or .cram.")
        exit(1)

    # output directory
    nf_out = "/data/results"

    # config
    nf_config = NF_CONFIG_TEMPLATE
    nf_config = nf_config.replace("<REF_FILE>", nf_fa)
    nf_config = nf_config.replace("<IN_BAM>", nf_bam)
    nf_config = nf_config.replace("<OUT_DIR>", nf_out)

    nf_config_path = f"{args.out_dir}/nextflow.config"
    with open(nf_config_path, "w") as f:
        f.write(nf_config)


def run_stellarpgx(args):
    cmd = "docker run --privileged -it -v `pwd`:/data stellarpgx:1.2.5 nextflow run main.nf"
    cmd += f" -profile standard -c /data/nextflow.config --format compressed --build hg38 --gene cyp2d6"
    try_run_command(cmd=cmd, cwd=args.out_dir)


def done(args):
    # tidy up workdir
    if args.tidy:
        ref_fa_name = Path(args.ref_fa).name
        bam_name = Path(args.bam).name
        cmd = f"rm {ref_fa_name}* {bam_name}*"
        try_run_command(cmd=cmd, cwd=args.out_dir)

    # done
    logging.info(f"DONE: {args.out_dir}")


if __name__ == "__main__":
    args = parse_args()
    prepare_stellarpgx_inputs(args)
    run_stellarpgx(args)
    done(args)