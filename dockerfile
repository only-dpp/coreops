<<<<<<< HEAD
FROM python:3.11-slim

WORKDIR /code
RUN pip install --no-cache-dir -U pip

# Copia metadados
COPY pyproject.toml /code/pyproject.toml

# Copia somente o pacote
COPY app /code/app

# Instala (cacheado)
RUN pip install --no-cache-dir -e .

# Agora copia o resto (README, alembic.ini etc.)
=======
FROM python:3.11-slim

WORKDIR /code
RUN pip install --no-cache-dir -U pip

# Copia metadados
COPY pyproject.toml /code/pyproject.toml

# Copia somente o pacote
COPY app /code/app

# Instala (cacheado)
RUN pip install --no-cache-dir -e .

# Agora copia o resto (README, alembic.ini etc.)
>>>>>>> 21599b0b39eba37876fc43d9838497fbe2974000
COPY . /code