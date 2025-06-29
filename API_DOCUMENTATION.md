# API Documentation

## 概要
英単語学習アプリケーションのREST API仕様書です。このAPIはユーザー管理、フラッシュカード機能、メディア生成、語彙データ管理を提供します。

## ベースURL
- 開発環境: `http://localhost:8000`
- 本番環境: `https://your-cloud-run-service-url`

## 認証
現在は認証は実装されていません。

---

## User Management APIs

### 1. GET /user/{userId}
ユーザー情報を取得します。

**パラメータ:**
- `userId` (string): ユーザーID

**レスポンス:**
```json
{
  "message": "User retrieved successfully",
  "user": {
    "userId": "cergU7H1N7gRnzZmiZcC",
    "email": "yamada@yamada.com", 
    "userName": "山田",
    "flashcardIdList": [
      "U0R53LJvpZOCdvVDbUYF",
      "iota2j31aw9opZXXEQAy"
    ]
  }
}
```

**エラーレスポンス:**
- `500`: サーバーエラー または ユーザーが存在しない

### 2. POST /user/setup
新規ユーザーを登録します。

**リクエストボディ:**
```json
{
  "userId": "12345",
  "email": "yamada@yamada.com",
  "userName": "山田"
}
```

**レスポンス:**
```json
{
  "message": "User setup successful"
}
```

**エラーレスポンス:**
- `422`: 不正なリクエスト形式
- `500`: サーバーエラー

### 3. PUT /user/update
ユーザー情報を更新します。

**リクエストボディ:**
```json
{
  "userId": "cergU7H1N7gRnzZmiZcC",
  "email": "yamada@yamada.com",
  "userName": "山田2"
}
```

**レスポンス:**
```json
{
  "message": "User update successful",
  "userId": "cergU7H1N7gRnzZmiZcC"
}
```

**エラーレスポンス:**
- `422`: 不正なリクエスト形式
- `500`: サーバーエラー

### 4. DELETE /user/{userId}
ユーザーを削除します。

**パラメータ:**
- `userId` (string): 削除するユーザーID

**レスポンス:**
```json
{
  "message": "User delete successful"
}
```

**エラーレスポンス:**
- `422`: 不正なリクエスト形式
- `500`: サーバーエラー

---

## Flashcard Management APIs

### 5. GET /flashcard/{userId}
ユーザーのフラッシュカード一覧を取得します。

**パラメータ:**
- `userId` (string): ユーザーID

**レスポンス:**
```json
{
  "message": "Flashcards retrieved successfully",
  "flashcards": [
    {
      "flashcardId": "U0R53LJvpZOCdvVDbUYF",
      "wordId": "word123",
      "word": "example",
      "checkFlag": false,
      "memo": "学習メモ",
      "usingMeaningIdList": ["meaning1", "meaning2"]
    }
  ]
}
```

**エラーレスポンス:**
- `500`: サーバーエラー

### 6. PUT /flashcard/update/checkFlag
フラッシュカードのチェックフラグを更新します。

**リクエストボディ:**
```json
{
  "flashcardId": "U0R53LJvpZOCdvVDbUYF",
  "checkFlag": true
}
```

**レスポンス:**
```json
{
  "message": "Check flag updated successfully"
}
```

**エラーレスポンス:**
- `422`: 不正なリクエスト形式
- `400`: 更新エラー
- `500`: サーバーエラー

### 7. PUT /flashcard/update/memo
フラッシュカードのメモを更新します。

**リクエストボディ:**
```json
{
  "flashcardId": "U0R53LJvpZOCdvVDbUYF",
  "memo": "更新されたメモ内容"
}
```

**レスポンス:**
```json
{
  "message": "Flashcard memo update successful"
}
```

**エラーレスポンス:**
- `422`: 不正なリクエスト形式
- `400`: 更新エラー
- `500`: サーバーエラー

### 8. PUT /flashcard/update/usingMeaningIdList
フラッシュカードで使用する意味IDリストを更新します。

**リクエストボディ:**
```json
{
  "flashcardId": "U0R53LJvpZOCdvVDbUYF",
  "usingMeaningIdList": ["L35JDrI7sVIrkhxNulsE"]
}
```

**レスポンス:**
```json
{
  "message": "Using meaning ID list updated successfully"
}
```

**エラーレスポンス:**
- `422`: 不正なリクエスト形式
- `400`: 更新エラー
- `500`: サーバーエラー

---

## Media Generation APIs

### 9. POST /media/create
フラッシュカード用のメディア（画像）を生成します。

**リクエストボディ:**
```json
{
  "flashcardId": "12345",
  "oldMediaId": "67890",
  "meaningId": "54321",
  "pos": "noun",
  "word": "cat",
  "translation": "猫",
  "exampleJpn": "猫がマットの上に座っていました。",
  "explanation": "しばしば犬と対比される小型の哺乳類で、一般的にペットとして飼われる。",
  "coreMeaning": "無ければnull",
  "generationType": "text-to-image",
  "templateId": "template_001",
  "userPrompt": "あなたは画像生成AIでイラストを生成するための～",
  "otherSettings": ["猫の種類は三毛猫にしてください。"],
  "allowGeneratingPerson": true,
  "inputMediaUrls": ["http://example.com/image1.jpg"]
}
```

**レスポンス:**
```json
{
  "message": "Flashcard comparison ID updated successfully",
  "comparisonId": "comparison_123",
  "newMediaId": "media_456",
  "newMediaUrls": [
    "https://storage.googleapis.com/bucket/generated_image_1.jpg",
    "https://storage.googleapis.com/bucket/generated_image_2.jpg"
  ]
}
```

**エラーレスポンス:**
- `422`: 不正なリクエスト形式
- `500`: サーバーエラー

---

## Comparison APIs

### 10. POST /comparison/{userId}
ユーザーの未比較メディア一覧を取得します。

**パラメータ:**
- `userId` (string): ユーザーID

**レスポンス:**
```json
{
  "message": "Not compared medias retrieved successfully",
  "comparisons": [
    {
      "comparisonId": "comparison_123",
      "flashcardId": "flashcard_456",
      "oldMediaId": "media_old",
      "newMediaId": "media_new",
      "oldMediaUrls": ["https://example.com/old.jpg"],
      "newMediaUrls": ["https://example.com/new.jpg"],
      "word": "example",
      "meaning": "例"
    }
  ]
}
```

**エラーレスポンス:**
- `422`: 不正なリクエスト形式
- `500`: サーバーエラー

### 11. PUT /comparison/update
メディア比較結果を送信します。

**リクエストボディ:**
```json
{
  "flashcardId": "12345",
  "comparisonId": "comparison_123",
  "oldMediaId": "54321",
  "newMediaId": "67890",
  "isSelectedNew": true
}
```

**レスポンス:**
```json
{
  "message": "Flashcard comparison ID updated successfully"
}
```

**エラーレスポンス:**
- `422`: 不正なリクエスト形式
- `500`: サーバーエラー

---

## Vocabulary Data APIs

### 12. GET /meaning/{wordId}
単語の全ての意味を取得します。

**パラメータ:**
- `wordId` (string): 単語ID

**レスポンス:**
```json
{
  "message": "Meanings retrieved successfully",
  "meanings": [
    {
      "meaningId": "meaning_123",
      "pos": "noun",
      "definition": "a small domesticated carnivorous mammal",
      "translation": "猫",
      "exampleEng": "The cat sat on the mat.",
      "exampleJpn": "猫がマットの上に座った。",
      "explanation": "一般的にペットとして飼われる小型の哺乳類"
    }
  ]
}
```

**エラーレスポンス:**
- `404`: 意味が見つからない
- `500`: サーバーエラー

---

## Template Management APIs

### 13. GET /template
プロンプトテンプレート一覧を取得します。

**レスポンス:**
```json
{
  "message": "User templates retrieved successfully",
  "templates": [
    {
      "templateId": "template_123",
      "generationType": "text-to-image",
      "target": "例文",
      "preText": "Generate an image of a cat",
      "createdAt": "2023-01-01T00:00:00",
      "updatedAt": "2023-01-01T00:00:00"
    }
  ]
}
```

**エラーレスポンス:**
- `422`: 不正なリクエスト形式
- `500`: サーバーエラー

### 14. POST /template/create
新しいプロンプトテンプレートを作成します。

**リクエストボディ:**
```json
{
  "generationType": "text-to-image",
  "target": "例文",
  "preText": "Generate an image of a cat"
}
```

**レスポンス:**
```json
{
  "message": "Template created successfully",
  "templateId": "template_456"
}
```

**エラーレスポンス:**
- `422`: 不正なリクエスト形式
- `500`: サーバーエラー

### 15. PUT /template/update
プロンプトテンプレートを更新します。

**リクエストボディ:**
```json
{
  "templateId": "template_123",
  "generationType": "text-to-image",
  "target": "例文",
  "preText": "Generate an image of a cat"
}
```

**レスポンス:**
```json
{
  "message": "Template updated successfully"
}
```

**エラーレスポンス:**
- `422`: 不正なリクエスト形式
- `500`: サーバーエラー

---

## その他のエンドポイント

### GET /
ヘルスチェック用エンドポイント

**レスポンス:**
```json
{
  "message": "Hello World"
}
```

### POST /apply/add_meaning
単語の意味追加申請（未実装）

**レスポンス:**
```json
{
  "detail": "このAPIはまだ実装されていません。"
}
```

### POST /apply/modify_meaning
単語の意味修正申請（未実装）

**レスポンス:**
```json
{
  "detail": "このAPIはまだ実装されていません。"
}
```

---

## エラーハンドリング

### 共通エラーレスポンス形式
```json
{
  "detail": "エラーメッセージ"
}
```

### HTTPステータスコード
- `200`: 成功
- `400`: リクエストエラー
- `404`: リソースが見つからない
- `422`: バリデーションエラー
- `500`: サーバー内部エラー

---

## データ型定義

### ユーザー情報
```typescript
interface User {
  userId: string
  email: string
  userName: string
  flashcardIdList: string[]
}
```

### フラッシュカード
```typescript
interface Flashcard {
  flashcardId: string
  wordId: string
  word: string
  checkFlag: boolean
  memo: string
  usingMeaningIdList: string[]
}
```

### 意味情報
```typescript
interface Meaning {
  meaningId: string
  pos: string
  definition: string
  translation: string
  exampleEng: string
  exampleJpn: string
  explanation: string
}
```

### テンプレート
```typescript
interface Template {
  templateId: string
  generationType: string
  target: string
  preText: string
  createdAt: string
  updatedAt: string
}
```