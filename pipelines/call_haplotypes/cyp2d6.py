from dataclasses import dataclass, field
import collections
import re


@dataclass
class Haplotype:
    raw: str = field(compare=False, repr=False)
    string: str
    star_alleles: collections.Counter = field(
        default_factory=collections.Counter, compare=False, repr=False
    )
    star_allele_sep = "+"

    @classmethod
    def from_raw(cls, raw_haplotype):
        # Split "*1+*36" into ["*1", "*36"]
        # This also drops any mutations such as "rs1065852"
        split_raw_star_alleles = [
            sa for sa in raw_haplotype.split(cls.star_allele_sep) if sa.startswith("*")
        ]

        # Extract any pre-annotated copy numbers as a tuple: "*36x2" -> ("*36", 2)
        copy_number_tuples = []
        for item in split_raw_star_alleles:
            copy_number = 1
            match = re.search("x(\d+)", item)
            if match:
                copy_number = int(match.group(1))
            copy_number_tuples.append((item, copy_number))

        # Remove minor alleles and sort:
        # "*4.021" -> "*4"
        # "*4C" -> "*4"
        unsorted_star_alleles = []
        for raw_star_allele, copy_number in copy_number_tuples:
            star_allele = re.search("\*\d+", raw_star_allele).group(0)
            for i in range(copy_number):
                unsorted_star_alleles.append(star_allele)

        sorted_star_alleles = sorted(
            unsorted_star_alleles, key=lambda x: int(re.sub("\*", "", x))
        )

        # Consolidate sorted star alleles into counter
        star_alleles_counter = collections.Counter(sorted_star_alleles)

        # Create haplotype string from star alleles counter
        star_allele_strings = []
        for star_allele in star_alleles_counter:
            if star_alleles_counter[star_allele] > 1:
                star_allele_strings.append(
                    f"{star_allele}x{star_alleles_counter[star_allele]}"
                )
            else:
                star_allele_strings.append(f"{star_allele}")

        haplotype_string = "+".join(star_allele_strings)

        return cls(
            raw=raw_haplotype,
            string=haplotype_string,
            star_alleles=star_alleles_counter,
        )

    @staticmethod
    def lowest_star_allele(haplotype):
        star_allele_ints = [
            int(number) for number in re.findall("\*(\d+)", haplotype.string)
        ]
        return min(star_allele_ints)


@dataclass
class Diplotype:
    raw: str = field(compare=False, repr=False)
    string: str
    filt: str = field(default=None, compare=False)
    haplotypes: list = field(default_factory=list, repr=False, compare=False)
    hap_sep = "/"

    @classmethod
    def from_raw(cls, raw_diplotype, filt=None):
        if not cls.is_valid(raw_diplotype):
            raise ValueError(f"Invalid diplotype string: {raw_diplotype}")

        haplotypes = [
            Haplotype.from_raw(hap) for hap in raw_diplotype.split(cls.hap_sep)
        ]
        haplotypes.sort(key=Haplotype.lowest_star_allele)
        haplotype_strings = [haplotype.string for haplotype in haplotypes]
        diplotype_string = cls.hap_sep.join(haplotype_strings)
        return cls(
            raw=raw_diplotype, string=diplotype_string, filt=filt, haplotypes=haplotypes
        )

    @classmethod
    def no_call(cls, filt=None):
        return cls(raw="no_call", string="no_call", filt=filt, haplotypes=[])

    @staticmethod
    def is_valid(raw_diplotype):
        pattern = "\*\d+.*?/\*\d+.*?$"
        match = re.fullmatch(pattern, raw_diplotype)
        if match:
            return True
        else:
            return False


if __name__ == "__main__":

    with open("/home/torojr/SG10K-CYP2D6/_data/test.txt", "r") as f:
        test_diplotypes = [line.strip() for line in f.readlines()]

    for test_diplotype in test_diplotypes:
        if test_diplotype != "None":
            try:
                d = Diplotype.from_raw(test_diplotype)
            except Exception as e:
                print("[ERROR]", test_diplotype, "->", e)

            print(d.haplotypes)
