# ベースイメージ
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なシステムパッケージをインストール
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Poetryのインストール
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# プロジェクトファイルをコピー
COPY pyproject.toml poetry.lock ./

# 依存関係をインストール
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# アプリケーションコードをコピー
COPY . .

# ポートを公開
EXPOSE 8000

# FastAPIアプリケーションを起動
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

