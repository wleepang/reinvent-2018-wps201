FROM bcftools AS source

RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm
RUN yum install -y python36u python36u-pip
RUN pip3.6 install boto3

WORKDIR /opt/app
COPY bcftools.py .

WORKDIR /scratch
ENTRYPOINT [ "python3.6", "/opt/app/bcftools.py" ]