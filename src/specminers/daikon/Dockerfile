FROM ubuntu:16.04
RUN apt-get update \
 && apt-get install -y \
      wget \
      software-properties-common \
 && add-apt-repository ppa:openjdk-r/ppa \
 && apt-get update \
 && apt-get install -y \
      openjdk-8-jdk \
      git \
      subversion \
      perl \
      libdbi-perl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
ENV DAIKON_VERSION 5.7.2
ENV DAIKONDIR /opt/daikon
ENV CLASSPATH /opt/daikon/daikon.jar
ENV JAVA_HOME /usr/lib/jvm/java
RUN cd /opt \
 && wget -nv "http://plse.cs.washington.edu/daikon/download/daikon-${DAIKON_VERSION}.tar.gz" \
 && tar zxf "daikon-${DAIKON_VERSION}.tar.gz" \
 && mv "daikon-${DAIKON_VERSION}" /opt/daikon \
 && rm *.tar.gz
