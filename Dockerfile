FROM python:3.12-slim


WORKDIR /app

# poetryのインストール
RUN curl -sSL https://install.python-poetry.org | python3
ENV PATH /root/.local/bin  # ここ追加
COPY pyproject.toml* poetry.lock* ./

RUN poetry config virtualenvs.in-project true
RUN poetry install --no-dev

COPY src/ /app

# entrypoint
ENTRYPOINT ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]