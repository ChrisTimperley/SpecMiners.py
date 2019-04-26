FROM ubuntu:16.04

RUN apt-get update \
 && apt-get install -y \
      cmake \
      python \
      g++ \
      mercurial \
      libboost-all-dev \
      libgtest-dev \
      wget \
 && apt-get clean \
 && cd /usr/src/gtest \
 && mkdir build \
 && cmake CMakeLists.txt \
 && make \
 && cp *.a /usr/lib \
 && rm -rf /var/lib/apt/lists/* /tmp/*

ENV SPOT_VERSION 1.2.5
ENV SPOT_HOME /opt/spot
RUN cd /tmp \
 && wget -nv "http://www.lrde.epita.fr/dload/spot/spot-${SPOT_VERSION}.tar.gz" \
 && tar -xzf "spot-${SPOT_VERSION}.tar.gz" \
 && mkdir -p $(dirname "${SPOT_HOME}") \
 && mv "spot-${SPOT_VERSION}" "${SPOT_HOME}" \
 && cd "${SPOT_HOME}" \
 && ./configure \
 && make \
 && make install \
 && rm -rf /tmp/*

ENV TEXADA_HOME /opt/texada
ENV PATH "${TEXADA_HOME}:${PATH}"
ENV TEXADA_REVISION 625ba2d
RUN mkdir -p "${TEXADA_HOME}" \
 && hg clone https://bitbucket.org/bestchai/texada "${TEXADA_HOME}" \
 && cd "${TEXADA_HOME}" \
 && hg update -r "${TEXADA_REVISION}" \
 && cp uservars.mk.example uservars.mk \
 && sed -i "/^SPOT_INCL:=/c\SPOT_INCL:=${SPOT_HOME}/src/" uservars.mk \
 && make \
 && ./texadatest
