FROM ubuntu:20.04

LABEL base_image="ubuntu:20.04"
LABEL version="1"
LABEL maintainer="Mar Gonzalez-Porta"
LABEL maintainer.email="mar_gonzalez_porta@gis.a-star.edu.sg"
LABEL software="Cyrius"
LABEL software.version="1.1.1"
LABEL about.summary="WGS-based CYP2D6 genotyper"
LABEL about.home="https://github.com/Illumina/Cyrius"
LABEL about.license="SPDX:Apache-2.0"

# install dependencies
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get -y --no-install-recommends install git python3 python3-pip && \
    apt-get autoclean && \
    pip install pysam numpy scipy statsmodels

# install cyrius
RUN git clone https://github.com/Illumina/Cyrius.git && \
    chmod +x /Cyrius/star_caller.py

# add cyrius to path
ENV PATH="$PATH:/Cyrius"

# set default workdir
WORKDIR /data