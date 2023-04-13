from dataclasses import dataclass, field
import re
from typing import Self


@dataclass(order=True)
class StarAllele:
    """
    Dataclass for star alleles. Use the "from_string"
    method to parse a star allele from a string.
    """

    sort_value: int
    raw: str
    parsed: str
    major: str
    minor: str
    copy_number: int
    variants: list[str] = field(default_factory=list)
    regex_pattern = r"\*\d+(?:[A-Z])?(?:\.\d+)?(?:\.ALDY)?(?:x\d+)?(?:\+rs\d+)*"

    @classmethod
    def from_string(cls, raw_star_allele: str) -> Self:
        if not cls.is_valid(raw_star_allele):
            raise ValueError(f"Invalid star allele string: {raw_star_allele}")

        major_pattern = "\*\d+"
        major_match = re.search(major_pattern, raw_star_allele)
        major = major_match.group(0)

        sort_value = int(re.search("\*(\d+)", major).group(1))

        minor_pattern = r"\*\d+([A-Z])?(\.\d+)?(\.ALDY)?"
        minor_match = re.search(minor_pattern, raw_star_allele)
        minor = minor_match.group(0)

        variants_pattern = r"\+(rs\d+)"
        variants = re.findall(variants_pattern, raw_star_allele)

        copy_number_pattern = r"x(\d+)"
        copy_number_match = re.search(copy_number_pattern, raw_star_allele)
        if copy_number_match:
            copy_number = int(copy_number_match.group(1))
        else:
            copy_number = 1

        parsed = major
        if copy_number > 1:
            parsed += f"x{copy_number}"

        return cls(
            sort_value, raw_star_allele, parsed, major, minor, copy_number, variants
        )

    @classmethod
    def is_valid(cls, raw_star_allele: str) -> bool:
        fullmatch = re.fullmatch(cls.regex_pattern, raw_star_allele)

        if fullmatch:
            return True
        else:
            return False

    def as_list(self):
        return [self.major] * self.copy_number

    def __str__(self):
        return self.raw


@dataclass(order=True)
class Haplotype:
    """
    Dataclass for storing CYP2D6 haplotype data. Use the from_string method to
    initialise the class from a string.
    """

    sort_value: int
    raw: str
    parsed: str
    star_alleles: list[StarAllele] = field(default_factory=list)
    separator = "+"

    @classmethod
    def from_string(cls, raw_haplotype: str) -> Self:
        star_alleles = [
            StarAllele.from_string(star_allele)
            for star_allele in re.findall(StarAllele.regex_pattern, raw_haplotype)
        ]
        parsed = cls.separator.join([sa.parsed for sa in sorted(star_alleles)])
        sort_value = min(star_alleles).sort_value

        return cls(sort_value, raw_haplotype, parsed, star_alleles)

    def __str__(self) -> str:
        return self.raw


@dataclass
class Diplotype:
    """
    Dataclass used to store CYP2D6 diplotype data. Use the from_string method to
    initialise from a string.
    """

    raw: str = field(compare=False, repr=False)
    parsed: str
    filt: str = field(default=None, compare=False)
    haplotypes: list = field(default_factory=list, repr=False, compare=False)
    star_alleles: list = field(default_factory=list, repr=False, compare=False)
    is_novel: bool = field(default=False)
    separator = "/"

    @classmethod
    def from_string(cls, raw_diplotype: str, filt: str = None) -> Self:
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
            raise ValueError(f"Invalid diplotype string: {raw_diplotype}")

        # Identify haplotypes and star alleles
        haplotypes = [
            Haplotype.from_string(haplotype)
            for haplotype in raw_diplotype.split(cls.separator)
        ]

        star_alleles = [
            star_allele
            for haplotype in haplotypes
            for star_allele in haplotype.star_alleles
        ]

        # Sort haplotypes and turn them into the final parsed string
        parsed = cls.separator.join(
            [haplotype.parsed for haplotype in sorted(haplotypes)]
        )

        return cls(
            raw=raw_diplotype,
            parsed=parsed,
            filt=filt,
            haplotypes=haplotypes,
            star_alleles=star_alleles,
        )

    @classmethod
    def no_call(cls) -> Self:
        """
        Creates an instance of Diplotype with "no_call" as the value of its
        "raw", "major" and "minor" attributes.
        """
        no_call_string = "no_call"
        return cls(raw=no_call_string, parsed=no_call_string)

    @classmethod
    def invalid(cls, raw_diplotype: str) -> Self:
        invalid_string = "invalid"
        return cls(raw=raw_diplotype, parsed=invalid_string)

    @classmethod
    def novel_allele(cls, raw_diplotype: str, filt: str = None) -> Self:
        """
        Same functionality as the "from_string" method, except with the "novel"
        property set to True.
        """

        diplotype = cls.from_string(raw_diplotype, filt)
        diplotype.is_novel = True
        return diplotype

    @staticmethod
    def is_valid(raw_diplotype: str) -> bool:
        """
        Attemtps to fully match the provided raw_diplotype string against a
        preset regex pattern. Returns True only if the whole string matches the
        pattern, otherwise returns False.
        """

        haplotype_pattern = (
            r"(?:\*\d+(?:[A-Z])?(?:x\d)?(?:\.\w*)?(?:(?:\+\w+)+)?(?:\+)?)+"
        )
        diplotype_pattern = f"{haplotype_pattern}/{haplotype_pattern}"
        match = re.fullmatch(diplotype_pattern, raw_diplotype)
        if match:
            return True
        else:
            return False
