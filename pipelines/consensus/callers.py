from pathlib import Path
import json
import logging
from diplotype import Diplotype
import pandas as pd


class Cyp2d6CallerOutput:

    def __init__(self, file_path, caller, sample_name=None, diplotypes=[]):
        self.file_path = Path(file_path).resolve()
        self.caller = caller
        self.sample_name = sample_name
        self.diplotypes = diplotypes


    @classmethod
    def cyrius(cls, file_path, sample_name=None):
        logging.info("Extracting Cyrius output")
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        data = file_path.read_text()

        cyrius_dict = json.loads(data)
        samples = list(cyrius_dict.keys())
        if len(samples) > 1:
            logging.warning(
                f"{len(samples)} sample(s) found in Cyrius json, only one sample will be processed"
            )
        if not sample_name:
            sample_name = samples[0]
        sample_dict = cyrius_dict[sample_name]
        genotype = sample_dict["Genotype"]
        filt = sample_dict["Filter"]
        logging.debug(f'Sample Name: "{sample_name}"')
        logging.debug(f'Genotype: "{genotype}"')
        logging.debug(f'Filt: "{filt}"')

        genotypes = []
        diplotypes = []
        if genotype is None:
            diplotypes.append(Diplotype.no_call())
        elif ";" in genotype:
            logging.warning(f"More than one genotype found in Cyrius output {file_path}")
            genotypes = [gt.replace("_", "/") for gt in genotype.split(";")]
        else:
            genotypes.append(genotype)
        
        for genotype in genotypes:
            if Diplotype.is_valid(genotype):
                diplotypes.append(Diplotype.from_string(genotype, filt=filt))
            else:
                diplotypes.append(Diplotype.invalid(genotype))

        return cls(file_path, caller="cyrius", sample_name=sample_name, diplotypes=diplotypes)


    @classmethod
    def aldy(cls, file_path, sample_name=None):
        logging.info("Extracting Aldy output")
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(file_path)

        diplotypes = []
        if file_path.stat().st_size == 0:
            diplotypes.append(Diplotype.no_call())
        else:
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

            genotypes = df["Major"].dropna().unique()

            if len(genotypes) == 0:
                diplotypes.append(Diplotype.no_call())
            elif len(genotypes) > 1:
                logging.warning(f"More than one genotype found in Aldy output {file_path}")
            
            for genotype in genotypes:
                if Diplotype.is_valid(genotype):
                    if "+rs" in genotype:
                        diplotypes.append(Diplotype.novel_allele(genotype))
                    else:
                        diplotypes.append(Diplotype.from_string(genotype))
                else:
                    diplotypes.append(Diplotype.invalid(genotype))

            if not sample_name:
                sample_name = df["Sample"].dropna().unique()[0]

        return cls(file_path, caller="aldy", sample_name=sample_name, diplotypes=diplotypes)


    @classmethod
    def stellarpgx(cls, file_path, sample_name=None):
        logging.info("Extracting StellarPGx output")
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(file_path)

        with file_path.open("r") as f:
            lines = [line.strip() for line in f.readlines() if len(line) > 0]

        result = None
        likely_background_alleles = None
        novel = False
        for i, line in enumerate(lines):
            if "novel allele" in line:
                novel = True

            if line.startswith("Result"):
                if "novel allele" not in lines[i + 1]:
                    result = lines[i + 1].strip()
            elif line.startswith("Likely background alleles"):
                likely_background_alleles = lines[i + 1].strip().replace("[", "").replace("]", "")

        if result:
            if result.lower() == "no_call":
                diplotype = Diplotype.no_call()
            elif Diplotype.is_valid(result):
                diplotype = Diplotype.from_string(result)
            else:
                diplotype = Diplotype.invalid(result)
        elif likely_background_alleles and novel:
            diplotype = Diplotype.novel_allele(likely_background_alleles)
        else:
            diplotype = Diplotype.no_call()

        return cls(file_path, caller="stellarpgx", sample_name=sample_name, diplotypes=[diplotype])

