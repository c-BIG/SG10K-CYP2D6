from pathlib import Path
import pandas as pd
import cyp2d6
import json


class Cyp2d6CallerOutput:
    def __init__(self, file_path=None):
        if file_path is not None:
            self.path = Path(file_path).resolve()
            self.raw_data = self._load_raw_data()
        else:
            self.path = None
            self.raw_data = None
        self.diplotypes = []
        self.filter = None

    def _load_raw_data(self):
        if not self.path.is_file():
            raise IOError(f"Invalid file path: {self.path}")
        with self.path.open("r") as f:
            raw_data = f.read()
        return raw_data


class AldyOutput(Cyp2d6CallerOutput):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.df = self._make_aldy_df()
        self._get_diplotypes()

    def _make_aldy_df(self):
        lines = [line for line in self.raw_data.split("\n") if len(line) > 0]
        column_names = lines[0].replace("#", "").split("\t")

        ignore = []
        for i, line in enumerate(lines):
            if line.startswith("#"):
                ignore.append(i)

        df = pd.read_csv(self.path, sep="\t", skiprows=ignore, names=column_names)
        return df

    def _get_diplotypes(self):
        diplotypes = []
        solutions = set(self.df["Major"].unique())
        for solution in solutions:
            diplotypes.append(cyp2d6.Diplotype.from_raw(solution))
        self.diplotypes = diplotypes


class CyriusOutput(Cyp2d6CallerOutput):
    def __init__(self, file_path):
        super().__init__(file_path)

        self.json = json.loads(self.raw_data)
        self.sample_id = list(self.json)[0]
        if len(self.json) > 1:
            print(
                f"[WARNING] Cyrius input ({self.path}) contains more than one sample, defaulting to {self.sample_id}"
            )
        self.data = self.json[self.sample_id]
        self.filter = self.data["Filter"]
        self.genotypes = self.data["Genotype"].replace("_", "/").split(";")

        for genotype in self.genotypes:
            if genotype == "None":
                diplotype = cyp2d6.Diplotype.no_call(self.filter)
            else:
                diplotype = cyp2d6.Diplotype.from_raw(genotype, self.filter)
            self.diplotypes.append(diplotype)


class StellarpgxOutput(Cyp2d6CallerOutput):
    def __init__(self, file_path):
        super().__init__(file_path)

        lines = [line for line in self.raw_data.split("\n") if len(line) > 0]
        result = ""
        for i, line in enumerate(lines):
            if line.startswith("Result"):
                result = lines[i + 1].strip()

        if result == "no_call":
            diplotype = cyp2d6.Diplotype.no_call()
        else:
            diplotype = cyp2d6.Diplotype.from_raw(result)
        self.diplotypes.append(diplotype)


if __name__ == "__main__":

    cyrius = CyriusOutput(
        "/home/torojr/SG10K-CYP2D6/_data/pilot/WHB3860/cyrius/WHB3860.json"
    )
    aldy = AldyOutput("/home/torojr/SG10K-CYP2D6/_data/pilot/WHB3860/aldy/WHB3860.aldy")

    print(cyrius.diplotypes[0])
    print(aldy.diplotypes[0])
    print(cyrius.diplotypes[0] == aldy.diplotypes[0])
