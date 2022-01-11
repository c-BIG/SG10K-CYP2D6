#!/usr/bin/env python3
# Requires python 3.10 or above

import logging
import argparse
import subprocess
from pathlib import Path
import os


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
    parser.add_argument("--keep_tmp", required=False, default=False, action="store_true",
                        help="Keep temporary files. Default: False")
    parser.add_argument("--loglevel", required=False, default="INFO",
                        help="Set logging level to INFO (default), WARNING or DEBUG.")
    args = parser.parse_args()

    set_logging(args.loglevel)

    args.sample_id = Path(args.bam).stem
    args.input_suffix = Path(args.bam).suffix

    # check that launch dir matches output dir (needed to get docker to launch)
    if not Path(args.out_dir).exists():
        logging.error(f"Couldn't find the output directory: {args.out_dir}")
        exit(1)
    args.launch_dir = args.out_dir

    # stage s3 files locally
    if "s3" in args.bam:
        logging.info(f"S3 path detected, staging inputs...")

        # mount s3 bucket
        bucket = args.bam.replace("s3://", "").split("/")[0]
        prefix = Path("/".join(args.bam.replace("s3://", "").split("/")[1:])).parent
        mountpoint = f"{args.out_dir}/s3"
        if not os.path.exists(mountpoint):
            os.makedirs(mountpoint)
        cmd = f"/home/jupyter-mgonzalezporta/workspace/tools/goofys/goofys {bucket}:{prefix} {mountpoint}"
        try_run_command(cmd=cmd, cwd=args.launch_dir)

        # copy cram and crai files
        # cmd = f"cp {mountpoint}/args.sample_id.cram "
        # args.bam = Path(mountpoint + "/" + Path(args.bam).name)

        local_bam = Path(args.launch_dir + "/" + Path(args.bam).name)
        # stage if file not already available locally
        if local_bam.exists():
            logging.info(f"Inputs already available locally, skipping copy...")
            args.bam = local_bam
        # download from s3 if not
        else:
            cmd = f"cp {mountpoint}/{Path(args.bam).name}* {args.launch_dir}"
            try_run_command(cmd=cmd, cwd=args.launch_dir)
            args.bam = local_bam
            # if args.input_suffix == ".bam":
            #     cmd = f"aws s3 cp {args.bam}.bai {args.launch_dir}"
            #     try_run_command(cmd=cmd, cwd=args.launch_dir)
            # elif args.input_suffix == ".cram":
            #     cmd = f"aws s3 cp {args.bam}.crai {args.launch_dir}"
            #     try_run_command(cmd=cmd, cwd=args.launch_dir)

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


def try_run_command(cmd, cwd=os.getcwd(), return_stdout=False):
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
    # note: hardlink_to requires python 3.10+
    if not Path(f"{args.launch_dir}/{ref_fa_name}").exists():
        Path(f"{args.launch_dir}/{ref_fa_name}").hardlink_to(args.ref_fa)
    if not Path(f"{args.launch_dir}/{ref_fa_name}.fai").exists():
        Path(f"{args.launch_dir}/{ref_fa_name}.fai").hardlink_to(f"{args.ref_fa}.fai")
    nf_fa = f"/data/{ref_fa_name}"

    # input files: bam/cram and index
    # note: hardlinks are not needed because we'll call subprocess from launch_dir (see parse_args)
    bam_name = Path(args.bam).name
    if args.input_suffix == ".bam":
        # Path(f"{args.launch_dir}/{bam_name}").hardlink_to(args.bam)
        # Path(f"{args.launch_dir}/{bam_name}.bai").hardlink_to(f"{args.bam}.bai")
        nf_bam = f"/data/%s" % bam_name.replace(".bam", ".*{bam,bai}")
    elif args.input_suffix == ".cram":
        # Path(f"{args.launch_dir}/{bam_name}").hardlink_to(args.bam)
        # Path(f"{args.launch_dir}/{bam_name}.crai").hardlink_to(f"{args.bam}.crai")
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

    nf_config_path = f"{args.launch_dir}/nextflow.config"
    with open(nf_config_path, "w") as f:
        f.write(nf_config)


def run_stellarpgx(args):
    cmd = "docker run --privileged -v `pwd`:/data stellarpgx:1.2.5 nextflow run main.nf"
    cmd += f" -profile standard -c /data/nextflow.config --format compressed --build hg38 --gene cyp2d6"
    try_run_command(cmd=cmd, cwd=args.launch_dir)


def done(args):
    if not args.keep_tmp:
        logging.info("Deleting temporary files...")
        ref_fa_name = Path(args.ref_fa).name
        bam_name = Path(args.bam).name
        cmd = f"rm {ref_fa_name}* {bam_name}*"
        try_run_command(cmd=cmd, cwd=args.launch_dir)

    # done
    logging.info(f"DONE: {args.out_dir}")


if __name__ == "__main__":
    args = parse_args()
    prepare_stellarpgx_inputs(args)
    run_stellarpgx(args)
    done(args)