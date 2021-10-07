FROM ubuntu:20.04

LABEL base_image="ubuntu:20.04"
LABEL version="1.0"
LABEL maintainer="Mar Gonzalez-Porta"
LABEL maintainer.email="mar_gonzalez_porta@gis.a-star.edu.sg"

# install dependencies
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get -y --no-install-recommends install git python3 python3-pip && \
    apt-get autoclean && \
    pip install dataclasses pysam numpy scipy statsmodels

# install the aws cli
RUN pip install awscli

# install aldy
RUN pip install aldy

# install cyrius
RUN git clone https://github.com/Illumina/Cyrius.git && \
    chmod +x /Cyrius/star_caller.py
ENV PATH="$PATH:/Cyrius"

# set default workdir
WORKDIR /data