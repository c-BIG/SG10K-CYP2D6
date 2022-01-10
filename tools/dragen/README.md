# DRAGEN germline

|  Item | Details |
|---|---|
|  Description | Perform alignment and variant calling on germline WGS data. |
| Official documentation | https://sapac.illumina.com/products/by-type/informatics-products/dragen-bio-it-platform.html |
| License | Paid - see documentation |

**Launch instructions**

Note: The GIS team are launching DRAGEN as a workflow from the [Illumina Connected Analytics](https://sapac.illumina.com/products/by-type/informatics-products/connected-analytics.html) platform (ICA). We're providing the launch settings for reference below.

```bash
# launch settings
/opt/edico/bin/dragen \
    --lic-server `cat "$(inputs.license.path)"` \
    -f \
    -r /ephemeral/ref \
    --fastq-list "$(runtime.outdir)/fastq_list.csv" \
    --output-file-prefix "$(inputs.outprefix)" \
    --output-directory "." \
    --intermediate-results-dir /ephemeral/intermediate \
    --output-format CRAM \
    --enable-sort true \
    --enable-duplicate-marking true \
    --enable-map-align true \
    --enable-map-align-output true \
    --enable-variant-caller true \
    --enable-vcf-compression true \
    --vc-emit-ref-confidence GVCF \
    --vc-enable-vcf-output true \
    --vc-enable-joint-detection true \
    --enable-metrics-json true \
    --gc-metrics-enable true \
    --qc-coverage-region-1 "$(inputs.autosomes.path)" \
    --qc-coverage-reports-1 overall_mean_cov hist contig_mean_cov cov_report callability \
    --qc-coverage-filters-1 'mapq<11,bq<0' \
    --enable-sv true \
    --enable-cnv true \
    --cnv-enable-self-normalization true \
    --cnv-segmentation-mode slm \
    --auto-detect-sample-sex true \
    --vc-enable-roh true \
    --enable-cyp2d6 true \
    --repeat-genotype-enable true \
    --repeat-genotype-specs /opt/edico/repeat-specs/experimental/smn-catalog.hg38.json \
    --qc-cross-cont-vcf /opt/edico/config/sample_cross_contamination_resource_hg38.vcf.gz
```
