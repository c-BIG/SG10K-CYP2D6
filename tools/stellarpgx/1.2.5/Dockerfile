# set up base image with singularity
# adapted from singularity-in-docker (https://github.com/kaczmarj/singularity-in-docker/blob/master/Dockerfile)
FROM golang:alpine3.14 as builder

WORKDIR $GOPATH/src/github.com/sylabs

RUN apk add --no-cache gawk gcc git libc-dev linux-headers libressl-dev libuuid libseccomp-dev make util-linux-dev

ARG SINGULARITY_COMMITISH="master"

RUN git clone https://github.com/sylabs/singularity.git \
    && cd singularity \
    && git checkout "$SINGULARITY_COMMITISH" \
    && ./mconfig -p /usr/local/singularity \
    && cd builddir \
    && make \
    && make install

FROM alpine:3.14

COPY --from=builder /usr/local/singularity /usr/local/singularity

ENV PATH="/usr/local/singularity/bin:$PATH" \
    SINGULARITY_TMPDIR="/tmp-singularity"

RUN apk add --no-cache ca-certificates libseccomp squashfs-tools tzdata \
    && mkdir -p $SINGULARITY_TMPDIR \
    && cp /usr/share/zoneinfo/UTC /etc/localtime \
    && apk del tzdata \
    && rm -rf /tmp/* /var/cache/apk/*

# install additional dependencies
RUN apk --update --no-cache add git python3 curl bash openjdk11

RUN mkdir /nextflow && cd /nextflow && \
    curl -fsSL get.nextflow.io | bash
ENV PATH="$PATH:/nextflow"

# install StellarPGx
RUN git clone https://github.com/SBIMB/StellarPGx.git

# set default workdir
WORKDIR /StellarPGx

# image info
LABEL base_image="alpine:3.14"
LABEL version="1"
LABEL maintainer="Mar Gonzalez-Porta"
LABEL maintainer.email="mar_gonzalez_porta@gis.a-star.edu.sg"
LABEL software="StellarPGx"
LABEL software.version="1.2.5"
LABEL about.summary="Calling star alleles in highly polymorphic pharmacogenes by leveraging genome graph-based variant detection"
LABEL about.home="https://github.com/SBIMB/StellarPGx"
LABEL about.license="MIT License"