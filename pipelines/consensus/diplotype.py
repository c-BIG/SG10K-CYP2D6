from dataclasses import dataclass, field, asdict
import collections
import re


@dataclass
class Haplotype:
    """
    Dataclass for storing CYP2D6 haplotype data. Use the from_string method to
    initialise the class from a single raw string.
    """

    raw: str = field(compare=False, repr=False)
    parsed: str
    star_alleles: collections.Counter = field(
        default_factory=collections.Counter, compare=False, repr=False
    )
    star_allele_sep = "+"


    @classmethod
    def from_string(cls, raw_haplotype):
        """
        Classmethod used to initialise a Haplotype instance. This method will
        attempt to sanitise the given string by removing any minor alleles and
        mutations. It will preserve copy numbers denoted by "x2" convention.
        """

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
            parsed=haplotype_string,
            star_alleles=star_alleles_counter,
        )


    @staticmethod
    def lowest_star_allele(haplotype):
        """
        Returns a haplotype object's star allele with the
        lowest numeric representation (useful for sorting):
        e.g. "*4" is lower than "*10"
        """

        # Find the star allele with the lowest numeric value
        star_allele_ints = [
            int(number) for number in re.findall("\*(\d+)", haplotype.parsed)
        ]
        return min(star_allele_ints)


@dataclass
class Diplotype:
    """
    Dataclass used to store CYP2D6 diplotype data. Use the from_string method to
    initialise from an unprocessed string.
    """

    raw: str = field(compare=False, repr=False)
    parsed: str
    filt: str = field(default=None, compare=False)
    haplotypes: list = field(default_factory=list, repr=False, compare=False)
    is_novel: bool = field(default=False)
    hap_sep = "/"


    @classmethod
    def from_string(cls, raw_diplotype, filt=None):
        """
        Creates a Diplotype object from a raw string. The raw diplotype string is 
        automatically split into haplotypes, which are themselves turned into 
        Haplotype objects and sanitised.
        """

        # no_call
        if raw_diplotype == "no_call":
            return cls.no_call()

        # Validate raw_diplotype string
        if not cls.is_valid(raw_diplotype):
            return cls(raw=raw_diplotype, parsed="invalid", filt=filt)

        # Identify haplotypes and sanitise them
        haplotypes = [
            Haplotype.from_string(hap) for hap in raw_diplotype.split(cls.hap_sep)
        ]

        # Sort haplotypes and turn them into the final diplotype string
        haplotypes.sort(key=Haplotype.lowest_star_allele)
        haplotype_strings = [haplotype.parsed for haplotype in haplotypes]
        diplotype_string = cls.hap_sep.join(haplotype_strings)
        return cls(
            raw=raw_diplotype, parsed=diplotype_string, filt=filt, haplotypes=haplotypes
        )


    @classmethod
    def no_call(cls):
        """
        Creates an instance of Diplotype with "no_call" as the value of its "raw"
        and "string" attributes.
        """

        return cls(raw="no_call", parsed="no_call", filt=None, haplotypes=[])


    @classmethod
    def novel_allele(cls, raw_diplotype, filt=None):
        """
        Same functionality as the "from_string" method, except with the "novel"
        property set to True.
        """

        diplotype = cls.from_string(raw_diplotype, filt)
        diplotype.is_novel = True
        return diplotype


    @staticmethod
    def is_valid(raw_diplotype):
        """
        Attemtps to fully match the provided raw_diplotype string against the
        following pattern: "\*\d+.*?/\*\d+.*?$"
        Returns True only if the whole string matches the pattern, otherwise
        returns False.
        """

        haplotype_pattern = r"(?:\*\d+(?:[A-Z])?(?:x\d)?(?:\.\w*)?(?:(?:\+\w+)+)?(?:\+)?)+"
        diplotype_pattern = f"{haplotype_pattern}/{haplotype_pattern}"
        match = re.fullmatch(diplotype_pattern, raw_diplotype)
        if match:
            return True
        else:
            return False
