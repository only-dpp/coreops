FROM python:3.12-slim

WORKDIR /code
RUN pip install --no-cache-dir -U pip

COPY pyproject.toml /code/pyproject.toml

COPY app /code/app

RUN pip install --no-cache-dir -e .

COPY . /code