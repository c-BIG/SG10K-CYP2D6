# Running docker
# docker run -t -i -v /home/jupyter-yusuf/Consensus/novel_alleles/vep:/opt/vep/.vep ensemblorg/ensembl-vep


docker run -v /home/jupyter-yusuf/Consensus/novel_alleles/vep:/data -u $(id -u):$(id -g) ensemblorg/ensembl-vep \
  vep --database --force_overwrite \
	  --everything --protein --af_gnomade --af_gnomadg \
	  --assembly GRCh38 \
    --input_file novel_core_alleles.txt \
    --output_file vep_novel_core_alleles.txt


