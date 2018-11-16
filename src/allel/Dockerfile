FROM python:3.7-slim as build

RUN apt-get update
RUN apt-get install -y gcc g++

WORKDIR /usr/src/app

RUN python -m venv ./venv

COPY requirements.txt .
RUN cat requirements.txt | xargs -n 1 ./venv/bin/pip install --no-cache-dir


FROM python:3.7-slim as production

WORKDIR /opt
COPY --from=build /usr/src/app/venv /opt/venv
COPY get_variants.py .

ENTRYPOINT [ "/opt/venv/bin/python", "get_variants.py" ]