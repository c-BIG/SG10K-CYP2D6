from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
import json
import pandas as pd


class OutputParser(Protocol):
    @staticmethod
    def parse_file(file_path: Path) -> list[dict]:
        pass


class CyriusOutputParser:
    @staticmethod
    def parse_file(file_path: Path) -> list[dict]:
        with file_path.open("r") as f:
            parsed_json = json.load(f)

        sample_id = list(parsed_json)[0]
        sample_data = parsed_json[sample_id]

        return sample_data


class StellarpgxOutputParser:
    @staticmethod
    def parse_file(file_path: Path) -> list[dict]:
        with file_path.open("r") as f:
            lines = [line.strip() for line in f.readlines()]

        data = {}
        for i, line in enumerate(lines):
            if len(line) > 0:
                if "=" in line:
                    key, value = [item.strip() for item in line.split("=")]
                    key = key.lower().replace(" ", "_")
                elif line.endswith(":"):
                    key = line[:-1].lower().replace(" ", "_")
                    value = lines[i + 1]
                else:
                    continue
                data[key] = value

        for key, value in data.items():
            if key == "sample_core_variants":
                core_variants = value.split(";")
                data[key] = core_variants
            elif key == "candidate_alleles":
                data[key] = [
                    item.replace("[", "").replace("]", "").replace("'", "")
                    for item in value.split(",")
                ]
            elif key == "initially_computed_cn":
                data[key] = int(value)
            elif key == "activity_score":
                try:
                    data[key] = float(value)
                except Exception:
                    pass

        return data


class AldyOutputParser:
    @staticmethod
    def parse_file(file_path: Path) -> list[dict]:
        with file_path.open("r") as f:
            lines = [line.strip() for line in f.readlines()]

        names = []
        rows = []
        for i, line in enumerate(lines):
            if i == 0:
                for name in line.split():
                    name = name.strip().replace("#", "")
                    names.append(name)
            elif line.startswith("#"):
                continue
            else:
                split_line = [item.strip() for item in line.split()]
                row = dict(zip(names, split_line))
                rows.append(row)

        data = {}
        if rows:
            df = pd.DataFrame(rows)

            data["genotype"] = list(df["Major"].unique())
            data["copy_number"] = df["Copy"].nunique()

        return data


@dataclass
class Cyp2d6Output:
    file_path: Path
    caller: str
    sample_id: str
    data: dict = field(default_factory=dict, init=False)
    parser: OutputParser = field(init=False)

    def __post_init__(self) -> None:
        if self.caller == "cyrius":
            self.parser = CyriusOutputParser
        elif self.caller == "stellarpgx":
            self.parser = StellarpgxOutputParser
        elif self.caller == "aldy":
            self.parser = AldyOutputParser
        else:
            raise ValueError(f"Unsupported parser {self.caller}")
        self.data = self.parser.parse_file(self.file_path)
