FROM python:3.6

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    DATA_LOCATION=/data/

COPY pyproject.toml .
RUN pip install --no-cache-dir poetry && \
    poetry install --no-dev

COPY . .

RUN cd /app/data && \
    mkdir /data && \
    tar -xzf trees_cologne_2017.jsonl.tar.gz  && \
    mv trees_cologne_2017.jsonl /data/trees_cologne_2017.jsonl
    

EXPOSE 80

CMD ["poetry", "run", "python", "-m", "cologne_treemap_api.api"]
