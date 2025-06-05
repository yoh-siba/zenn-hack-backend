FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root

COPY . /app
CMD ["sh", "-c", "poetry run uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
