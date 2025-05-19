# 英単語学習アプリケーション

このプロジェクトは、Words API を使用して英単語の情報を取得し、GPT で翻訳を行い、Firestore に保存するアプリケーションです。

## 環境構築

### 1. Poetry のインストール

```bash
# Windowsの場合（PowerShell）:
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# macOSの場合:
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. プロジェクトのセットアップ

```bash
# 依存パッケージのインストール
poetry install

# 仮想環境の作成と有効化
poetry env use python
poetry env activate
```

### 3. 環境変数の設定

`.env`ファイルを作成し、以下の環境変数を設定してください：

```env
WORDS_API_KEY=your_words_api_key
OPENAI_API_KEY=your_openai_api_key
GOOGLE_APPLICATION_CREDENTIALS=path_to_your_firestore_credentials.json
```

## 使用方法

### API サーバーの起動

```bash
# 仮想環境内で実行
poetry run uvicorn main:app --reload
```

### テストの実行

Words API のテストを実行する場合：

```bash
# デフォルトの単語（example）でテスト
poetry run python test/test_words_api.py

# 特定の単語でテスト
poetry run python test/test_words_api.py run
```

## プロジェクト構造

```
.
├── config/
│   └── settings.py      # 環境変数と設定
├── models/
│   └── types.py         # 型定義
├── services/
│   ├── word_service.py      # Words API関連
│   ├── translation_service.py    # GPT翻訳関連
│   └── firestore_service.py # Firestore関連
├── test/
│   └── test_words_api.py    # Words APIテスト
├── main.py              # FastAPIアプリケーション
├── pyproject.toml       # Poetry設定ファイル
├── poetry.lock         # 依存関係のロックファイル
└── README.md           # このファイル
```

## API エンドポイント

- `GET /`: ヘルスチェック
- `GET /word/{word}`: 指定した単語の情報を取得し、翻訳して保存

## 注意事項

- Words API の API キーが必要です
- OpenAI API の API キーが必要です
- Google Cloud Platform の認証情報が必要です
