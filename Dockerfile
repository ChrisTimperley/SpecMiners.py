FROM ubuntu:16.04

# install basic deps + gtest
RUN apt-get update \
 && apt-get install -y \
      cmake \
      python \
      g++ \
      git \
      libboost-all-dev \
      libgtest-dev \
      wget \
 && apt-get clean \
 && cd /usr/src/gtest \
 && mkdir build \
 && cmake CMakeLists.txt \
 && make install \
 && rm -rf /var/lib/apt/lists/* /tmp/*

# install Spot
RUN cd /tmp \
 && wget http://spot.lip6.fr/dl/spot-1.2.5.tar.gz \
 && tar -xzf spot-1.2.5.tar.gz \
 && cd spot-1.2.5 \
 && ./configure \
 && make \
 && make check \
 && make install \
 && rm -rf /tmp/*

# install Texada from source
ENV TEXADA_HOME /opt/texada
ENV PATH "${TEXADA_HOME}:${PATH}"
ENV TEXADA_REVISION 625ba2d
RUN mkdir -p "${TEXADA_HOME}" \
 && git clone https://bitbucket.org/bestchai/texada "${TEXADA_HOME}" \
 && cd "${TEXADA_HOME}" \
 && git checkout "${TEXADA_REVISION}" \
 && cp uservars.mk.example uservars.mk \
 && sed -i "/^SPOT_INCL:=/c\SPOT_INCL:=${PWD%/*}/spot-1.2.5/src/" uservars.mk \
 && make \
 && ./texadatest
