FROM ubuntu:16.04
RUN apt-get update \
 && apt-get install -y \
      wget \
      software-properties-common \
 && add-apt-repository ppa:openjdk-r/ppa \
 && apt-get update \
 && apt-get install -y \
      openjdk-7-jdk \
      git \
      subversion \
      perl \
      libdbi-perl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
RUN cd /opt \
 && wget -nv http://plse.cs.washington.edu/daikon/download/daikon-5.7.2.tar.gz \
 && tar zxf daikon-5.7.2.tar.gz \
 && mv daikon-5.7.2 /opt/daikon \
 && rm *.tar.gz
