FROM centos:latest as builder

RUN yum install -y \
  libcurl libcurl-devel \
  openssl-devel \
  gcc \
  bzip2 bzip2-devel \
  xz xz-devel \
  make

ENV BCFTOOLSVER 1.9

RUN mkdir -p /opt/samtools \
  && cd /opt/samtools \
  && curl -LO https://github.com/samtools/bcftools/releases/download/${BCFTOOLSVER}/bcftools-${BCFTOOLSVER}.tar.bz2 \
  && tar -xjf bcftools*.tar.bz2 \
  && cd bcftools-* \
  && ./configure \
  && make


FROM centos:latest

RUN yum clean all \
        && rm -rf /var/cache/yum
RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm
RUN yum install -y python36u python36u-pip
RUN pip3.6 install boto3

WORKDIR /usr/local/bin/
COPY --from=builder /opt/samtools/bcftools-*/bcftools .

WORKDIR /opt/app
COPY bcftools.py .

WORKDIR /scratch
ENTRYPOINT [ "python3.6", "/opt/app/bcftools.py" ]