import argparse
from pathlib import Path
import cyp2d6_callers as cypc


def get_args():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-v", "--verbose", action="store_true")
    argument_parser.add_argument(
        "-c", "--cyrius-file", required=True, help='Path to Cyrius ".json" output file'
    )
    argument_parser.add_argument(
        "-a", "--aldy-file", required=True, help='Path to Aldy ".aldy" output file'
    )
    argument_parser.add_argument(
        "-s", "--stellarpgx-file", help='Path to StellarPGx ".alleles" output file'
    )

    args = argument_parser.parse_args()
    return args


def caller_consensus(
    caller_a: cypc.Cyp2d6CallerOutput,
    caller_b: cypc.Cyp2d6CallerOutput,
    caller_c: cypc.Cyp2d6CallerOutput = None,
    verbose=False,
):
    consensus_filter = "FAIL"
    consensus_diplotype = "no_call"

    if caller_a.filter == "PASS":
        if len(caller_a.diplotypes) == 1 and len(caller_b.diplotypes) == 1:
            diplotype_a = caller_a.diplotypes[0]
            diplotype_b = caller_b.diplotypes[0]
            if caller_c:
                diplotype_c = caller_c.diplotypes[0]

            if diplotype_a == diplotype_b:
                consensus_filter = "PASS"
                consensus_diplotype = diplotype_a.string
            elif caller_c:
                if diplotype_a == diplotype_c:
                    consensus_filter = "PASS"
                    consensus_diplotype = diplotype_a.string
                elif diplotype_b == diplotype_c:
                    consensus_filter = "PASS"
                    consensus_diplotype = diplotype_b.string
    elif caller_a.filter == "None":
        if caller_c:
            diplotype_b = caller_b.diplotypes[0]
            diplotype_c = caller_c.diplotypes[0]
            if diplotype_b != "no_call" and diplotype_c != "no_call":
                if diplotype_b == diplotype_c:
                    consensus_filter = "PASS"
                    consensus_diplotype = diplotype_b.string

    if verbose:
        print("Cyrius:", caller_a.diplotypes)
        print("Aldy:", caller_b.diplotypes)
        if caller_c:
            print("StellarPGx:", caller_c.diplotypes)

    return consensus_filter, consensus_diplotype


def main():
    args = get_args()
    cyrius_path = Path(args.cyrius_file).resolve()
    aldy_path = Path(args.aldy_file).resolve()
    if args.stellarpgx_file:
        stellarpgx_path = Path(args.stellarpgx_file).resolve()

    # Import file
    cyrius = cypc.CyriusOutput(cyrius_path)
    aldy = cypc.AldyOutput(aldy_path)
    if args.stellarpgx_file:
        stellarpgx = cypc.StellarpgxOutput(stellarpgx_path)

    # Consensus
    if args.stellarpgx_file:
        consensus = caller_consensus(cyrius, aldy, stellarpgx, verbose=args.verbose)
    else:
        consensus = caller_consensus(cyrius, aldy, verbose=args.verbose)

    print(consensus)


if __name__ == "__main__":
    main()
