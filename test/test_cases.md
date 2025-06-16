# テストケース一覧

## 1. GET `/user/{userId}`

### 正常系
- **エンドポイント**: `/user/{userId}`
- **パラメータ**: `userId=cergU7H1N7gRnzZmiZcC`
- **想定されるレスポンス**:
  ```json
  {
    "message": "User retrieved successfully",
    "user": {
      "userId": "cergU7H1N7gRnzZmiZcC",
      "email": "yamada@yamada.com",
      "userName": "山田",
      "flashcardIdList": ["U0R53LJvpZOCdvVDbUYF",
                "iota2j31aw9opZXXEQAy",
                "qTZ97Xx6lF3rldphGOBS",
                    "qiRQwQhwuokaclEG4c37",
                    "tlqZh0L3POx6cFzpBpo3"
      ]
    }
  }
  ```
- **想定されるステータスコード**: `200`

### 異常系
- **エンドポイント**: `/user/{userId}`
- **パラメータ**: `userId=invalid_id`
- **想定されるレスポンス**:
  ```json
  {
    "detail": "Invalid user ID"
  }
  ```
- **想定されるステータスコード**: `422`

---

## 2. POST `/user/setup`

### 正常系
- **エンドポイント**: `/user/setup`
- **リクエストボディ**:
  ```json
  {
    "userId": "sampleId",
    "email": "sample@sample.com",
    "userName": "山田"
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "message": "User setup successful"
  }
  ```
- **想定されるステータスコード**: `200`

### 異常系
- **エンドポイント**: `/user/setup`
- **リクエストボディ**:
  ```json
  {
    "userId": "",
    "email": "invalid_email",
    "userName": ""
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "detail": "Invalid request format"
  }
  ```
- **想定されるステータスコード**: `422`

---

## 3. PUT `/user/update`

### 正常系
- **エンドポイント**: `/user/update`
- **リクエストボディ**:
  ```json
  {
    "userId": "cergU7H1N7gRnzZmiZcC",
    "email": "yamada@yamada.com",
    "userName": "山田2"
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "message": "User update successful",
    "userId": "cergU7H1N7gRnzZmiZcC"
  }
  ```
- **想定されるステータスコード**: `200`

### 異常系
- **エンドポイント**: `/user/update`
- **リクエストボディ**:
  ```json
  {
    "userId": "",
    "email": "invalid_email",
    "userName": ""
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "detail": "Invalid request format"
  }
  ```
- **想定されるステータスコード**: `422`

---

## 4. GET `/flashcard/{userId}`

### 正常系
- **エンドポイント**: `/flashcard/{userId}`
- **パラメータ**: `userId=12345`
- **想定されるレスポンス**:
  ```json
  {
    "message": "Flashcards retrieved successfully",
    "flashcards": []
  }
  ```
- **レスポンス型**: `FlashcardResponseModel`
- **想定されるステータスコード**: `200`

### 異常系
- **エンドポイント**: `/flashcard/{userId}`
- **パラメータ**: `userId=invalid_id`
- **想定されるレスポンス**:
  ```json
  {
    "detail": "Invalid user ID"
  }
  ```
- **レスポンス型**: `None`
- **想定されるステータスコード**: `422`

---

## 5. PUT `/flashcard/update/checkFlag`

### 正常系
- **エンドポイント**: `/flashcard/update/checkFlag`
- **リクエストボディ**:
  ```json
  {
    "flashcardId": "U0R53LJvpZOCdvVDbUYF",
    "checkFlag": true
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "message": "Check flag updated successfully"
  }
  ```
- **想定されるステータスコード**: `200`

### 異常系
- **エンドポイント**: `/flashcard/update/checkFlag`
- **リクエストボディ**:
  ```json
  {
    "flashcardId": "",
    "checkFlag": "invalid_flag"
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "detail": "Invalid request format"
  }
  ```
- **想定されるステータスコード**: `422`

---

## 6. PUT `/flashcard/update/memo`

### 正常系
- **エンドポイント**: `/flashcard/update/memo`
- **リクエストボディ**:
  ```json
  {
    "flashcardId": "U0R53LJvpZOCdvVDbUYF",
    "memo": "更新されたメモ内容"
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "message": "Memo updated successfully"
  }
  ```
- **想定されるステータスコード**: `200`

### 異常系
- **エンドポイント**: `/flashcard/update/memo`
- **リクエストボディ**:
  ```json
  {
    "flashcardId": "",
    "memo": ""
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "detail": "Invalid request format"
  }
  ```
- **想定されるステータスコード**: `422`

---

## 7. PUT `/flashcard/update/usingMeaningIdList`

### 正常系
- **エンドポイント**: `/flashcard/update/usingMeaningIdList`
- **リクエストボディ**:
  ```json
  {
    "flashcardId": "U0R53LJvpZOCdvVDbUYF",
    "usingMeaningIdList": ["L35JDrI7sVIrkhxNulsE"]
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "message": "Using meaning ID list updated successfully"
  }
  ```
- **想定されるステータスコード**: `200`

### 異常系
- **エンドポイント**: `/flashcard/update/usingMeaningIdList`
- **リクエストボディ**:
  ```json
  {
    "flashcardId": "",
    "usingMeaningIdList": []
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "detail": "Invalid request format"
  }
  ```
- **想定されるステータスコード**: `422`

---

## 8. POST `/media/create`

### 正常系
- **エンドポイント**: `/media/create`
- **リクエストボディ**:
  ```json
  {
    "flashcardId": "created_flashcard_id",
    "oldMediaId": "67890",
    "meaningId": "54321",
    "generationType": "text-to-image",
    "templateId": "template_001",
    "userPrompt": "Generate an image of a cat",
    "allowGeneratingPerson": true,
    "inputMediaUrls": [
    ]
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "message": "Media created successfully",
    "media_id": "new_media_id"
  }
  ```
- **想定されるステータスコード**: `200`

### 異常系
- **エンドポイント**: `/media/create`
- **リクエストボディ**:
  ```json
  {
    "flashcardId": "",
    "oldMediaId": "",
    "meaningId": "",
    "generationType": "",
    "templateId": "",
    "userPrompt": "",
    "allowGeneratingPerson": false,
    "inputMediaUrls": []
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "detail": "Invalid request format"
  }
  ```
- **想定されるステータスコード**: `422`

---

## 9. POST `/comparison/{userId}`

### 正常系
- **エンドポイント**: `/comparison/{userId}`
- **パラメータ**: `userId=cergU7H1N7gRnzZmiZcC`
- **想定されるレスポンス**:
  ```json
  {
    "message": "Comparison data retrieved successfully",
    "medias": []
  }
  ```
- **想定されるステータスコード**: `200`

### 異常系
- **エンドポイント**: `/comparison/{userId}`
- **パラメータ**: `userId=invalid_id`
- **想定されるレスポンス**:
  ```json
  {
    "detail": "Invalid user ID"
  }
  ```
- **想定されるステータスコード**: `422`

---

## 10. POST `/comparison/update`

### 正常系
- **エンドポイント**: `/comparison/update`
- **リクエストボディ**:
  ```json
  {
    "flashcardId": "U0R53LJvpZOCdvVDbUYF",
    "comparisonId": "comparison_id",
    "oldMediaId": "67890",
    "newMediaId": "54321",
    "isSelectedNew": true
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "message": "Comparison updated successfully"
  }
  ```
- **想定されるステータスコード**: `200`

### 異常系
- **エンドポイント**: `/comparison/update`
- **リクエストボディ**:
  ```json
  {
    "flashcardId": "",
    "comparisonId": "",
    "oldMediaId": "",
    "newMediaId": "",
    "isSelectedNew": false
  }
  ```
- **想定されるレスポンス**:
  ```json
  {
    "detail": "Invalid request format"
  }
  ```
- **想定されるステータスコード**: `422`
