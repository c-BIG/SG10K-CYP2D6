FROM ubuntu:20.04

LABEL base_image="ubuntu:20.04"
LABEL version="1"
LABEL maintainer="Mar Gonzalez-Porta"
LABEL maintainer.email="mar_gonzalez_porta@gis.a-star.edu.sg"
LABEL software="aldy"
LABEL software.version="3.3"
LABEL about.summary="A quick and nifty tool for genotyping and phasing popular pharmacogenes"
LABEL about.home="https://github.com/0xTCG/aldy"
LABEL about.license="https://github.com/0xTCG/aldy/blob/master/LICENSE.rst"

# install dependencies
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get -y --no-install-recommends install git python3 python3-pip && \
    apt-get autoclean && \
    pip install dataclasses

# install aldy
RUN pip install aldy

# set default workdir
WORKDIR /data