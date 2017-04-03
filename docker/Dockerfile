FROM ubuntu:14.04

RUN apt-get update && \
  apt-get install -y \
  build-essential \
  checkinstall \
  git \
  libatlas-base-dev \
  libreadline-gplv2-dev \
  libncursesw5-dev \
  libssl-dev \
  libsqlite3-dev \
  libgdbm-dev \
  libc6-dev \
  libbz2-dev \
  tk-dev \
  wget

RUN cd /usr/src && \
  wget https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tgz && \
  tar xzf Python-2.7.13.tgz && \
  cd Python-2.7.13 && \
  ./configure && \
  make install

RUN cd /usr/src && \
  wget https://bootstrap.pypa.io/get-pip.py && \
  python get-pip.py

RUN apt-get install -y libopenblas-dev && cd /usr/src && \
  git clone --recursive https://github.com/dmlc/mxnet && \
  cd mxnet && \
  cp make/config.mk . && \
  echo "USE_BLAS=openblas" >> config.mk && \
  echo "USE_DIST_KVSTORE=1" >> config.mk && \
  echo "USE_OPENCV=0" >> config.mk && \
  make -j$(nproc)

RUN pip install \
  pyyaml \
  numpy

RUN cd /usr/src/mxnet/python && \
  python setup.py install
