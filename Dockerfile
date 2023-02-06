FROM python:3.9-slim AS base_build

ARG ENV
ENV ENV=${ENV} \
  # poetry:
  POETRY_VERSION=1.1.13 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  PATH="$PATH:/root/.local/bin"

# System deps:
RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
  curl \
  git \
  build-essential \
  # Installing `poetry` package manager:
  # https://github.com/python-poetry/poetry
  && curl -sSL https://install.python-poetry.org | python - \
  && poetry --version \
  # Removing build-time-only dependencies:
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

RUN mkdir /code
WORKDIR /code/

# Copy only requirements, to cache them in docker layer
COPY ./poetry.lock ./pyproject.toml /code/

# Project initialization:
RUN poetry version \
  && poetry install

COPY . /code/

CMD ["uvicorn", "src.main:app", "--reload", "--port", "8080", "--host", "0.0.0.0"]