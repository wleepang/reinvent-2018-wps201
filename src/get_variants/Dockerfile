FROM python:3.7

WORKDIR /usr/src/app

COPY python/requirements.txt .
RUN cat requirements.txt | xargs -n 1 pip install --no-cache-dir

COPY python/. .

ENTRYPOINT ["python", "./get_variants.py"]
CMD ["python", "./get_variants.py"]

