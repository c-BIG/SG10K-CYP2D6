# SG10K CYP2D6 Aggregate Diplotypes v1
This diplotype table has been created from 1525 samples (30x) from the SG10K dataset:

- SG-Chinese: 1154
- SG-Indian: 166
- SG-Malay: 203
- Other: 2

## Callers
Diplotypes were generated from the outputs of three CYP2D6 callers: Cyrius, Aldy and StellarPGx.

### Parsing caller outputs
The raw output from the callers is parsed and cleaned with the following steps:
1. Check that the reported genotypes are valid CYP2D6 diplotypes by comparison against a regex pattern.
2. Split diplotypes by "/" to obtain haplotypes, e.g: `*1+*36+rsrs1065852/*36+*10` is split into `*1+*36+rsrs1065852` and `*36+*10`
3. Split haplotypes by "+" and select items which start with "*", e.g: `*1+*36+rs1065852` identifies `*1` and `*36` as star alleles
4. Remove minor alleles, e.g: `*4.021` becomes `*4`, `*4C` becomes `*4`
5. Sort star alleles within each haplotype in ascending order, e.g: `*36+*10` becomes `*10+*36`

Copy numbers are preserved and reported as "x#" for each star allele if needed: `*36+*36` becomes `*36x2` and `*10x2` remains `*10x2`. 

Some real examples:
- `*1/*36+*10` becomes `*1/*10+*36`
- `*36.ALDY+*10/*36.ALDY+*10` becomes `*10+*36/*10+*36`
- `*10+rs28371703+*65/*63+*63+*74+rs1135840` becomes `*10+*65/*63x2+*74`

### Diplotype call consensus
Sometimes callers report different diplotypes for the same sample. For this reason, it was necessary to systematically discard samples for which the diplotype call was uncertain. An algorithm was used to report call consensus with the following logic:
1. Do all three diplotypes match? -> Report matching diplotype
2. Do two of the three diplotypes match? -> Report matching diplotype
3. Do two of the three diplotypes report "no_call"? -> Report "no_call"

Any other call combinations are reported to have no consensus (`None` type in Python). This dataset only includes diplotypes for which there was consensus.

*Note: there are plans to improve the consensus algorithm in the future to rescue more complex caller output combinations and diplotypes*


## Columns
- `genetic_ancestry` data driven ancestry derived from SG10K SNP data (PCA k-means, k=3) representing ancestry groups: "C" = "Chinese"; "I" = "Indian"; "M" = "Malay"; "O" = "Other".

- `diplotype_count` diplotype count within the ancestry group

- `diplotype_frequency` diplotype frequency within the ancestry group

- `haplotypes` array of haplotypes derived from the diplotype column (copy numbers are preserved)

- `haplotype_count` array of haplotype counts within the ancestry group

- `haplotype_frequency` array of haplotype frequencies within the ancestry group

- `star_alleles` array of star alleles derived from diplotype (copy numbers are preserved)

- `star_allele_count` array of star allele counts within the ancestry group

- `star_allele_frequency` array of star allele frequencies within the ancestry group

All `count` and `frequency` columns are computed based on the ancestry group of each diplotype, haplotype and star allele, e.g: the diplotype frequency of "*1/*1" for "C" is `number of "*1/*1" diplotypes seen in "C" / total number of "C" diplotypes`.

# Changelog
## v2
- Haplotypes and star allele counts/frequencies were being reported incorrectly. The issue was a missing multiplication of the values by the diplotype count, which has now been fixed.
- Exported dataset in JSON format as well as original TSV file