from pathlib import Path
import json
import logging
from diplotype import Diplotype
import pandas as pd
import sys


class Cyp2d6CallerOutput:
    def __init__(self, diplotype):
        self.diplotype = diplotype

    def as_dict(self):
        pass

    @staticmethod
    def _parse_diplotype(diplotype_string, filt=None, context=""):
        logging.info(f'Parsing string "{diplotype_string}" (filt={filt})')
        if Diplotype.is_valid(diplotype_string):
            return Diplotype.from_string(diplotype_string, filt)
        elif diplotype_string.lower() == "no_call":
            return Diplotype.no_call()
        else:
            
            logging.warning(f"[{context}]" + f"Invalid diplotype string: \"{diplotype_string}\", returning \"no_call\"")
            return Diplotype.no_call()

    @classmethod
    def cyrius(cls, cyrius_json):
        logging.info("Extracting Cyrius output")
        file_path = Path(cyrius_json).resolve()

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        with file_path.open("r") as f:
            data = f.read()

        cyrius_json = json.loads(data)
        samples = list(cyrius_json.keys())
        if len(samples) > 1:
            logging.warning(
                f"{len(samples)} sample(s) found in Cyrius json, only one sample will be processed"
            )

        sample = samples[0]
        genotype = cyrius_json[sample]["Genotype"]
        filt = cyrius_json[sample]["Filter"]
        logging.debug(f'Sample name: "{sample}"')
        logging.debug(f'Genotype: "{genotype}"')
        logging.debug(f'Filt: "{filt}"')

        if genotype is None:
            genotype = "no_call"
        
        diplotype = cls._parse_diplotype(genotype, filt, context="cyrius")

        return cls(diplotype)

    @classmethod
    def aldy(cls, aldy_tsv):
        logging.info("Extracting Aldy output")
        file_path = Path(aldy_tsv).resolve()
        if not file_path.exists():
            raise FileNotFoundError(file_path)

        if file_path.stat().st_size == 0:
            diplotype = Diplotype.no_call()
            return cls(diplotype)

        with file_path.open("r") as f:
            rows_to_skip = []
            column_names = []
            for i, line in enumerate(f):
                if line.startswith("#"):
                    rows_to_skip.append(i)
                if line.startswith("#Sample"):
                    line = line.replace("#", "")
                    column_names = [col.strip() for col in line.split()]
                    

        df = pd.read_csv(file_path, sep="\t", names=column_names, skiprows=rows_to_skip)
        unique_genotypes = df["Major"].unique()
        if len(unique_genotypes) > 0:
            if len(unique_genotypes) > 1:
                logging.warning(
                    f"More than one genotype found in Aldy output, only first solution will be processed"
                )
            diplotype = cls._parse_diplotype(unique_genotypes[0], context="aldy")
        else:
            diplotype = Diplotype.no_call()
        return cls(diplotype)

    @classmethod
    def stellarpgx(cls, stellarpgx_alleles_file):
        logging.info("Extracting StellarPGx output")
        file_path = Path(stellarpgx_alleles_file).resolve()
        if not file_path.exists():
            raise FileNotFoundError(file_path)

        with file_path.open("r") as f:
            lines = [line.strip() for line in f.readlines() if len(line) > 0]

        result = None
        for i, line in enumerate(lines):
            if line.startswith("Result"):
                result = lines[i + 1].strip()

        if result:
            diplotype = cls._parse_diplotype(result, context="stellarpgx")
        else:
            diplotype = Diplotype.no_call()

        return cls(diplotype)
