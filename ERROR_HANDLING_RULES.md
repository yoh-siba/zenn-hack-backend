# エラー処理ルール

## 概要

このドキュメントは、プロジェクト全体のエラー処理を推奨パターン2（例外ベース）に統一するためのルールと実装ガイドラインを定義します。

## 1. エラー処理の基本方針

### 1.1 例外ベースのエラー処理を採用

```python
# 推奨パターン2: 例外ベース
class ServiceException(Exception):
    def __init__(self, message: str, error_type: str = "general"):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
```

### 1.2 レイヤー別の責務

| レイヤー | 責務 | エラー処理方法 |
|---------|------|---------------|
| **API層** (main.py) | HTTPステータスコードの決定 | `ServiceException` → `HTTPException` |
| **サービス層** (src/services/) | ビジネスロジック | `ServiceException` をraise |
| **Firebase層** (src/services/firebase/) | データアクセス | `ServiceException` をraise |
| **外部API層** (Google AI等) | 外部連携 | `ServiceException` をraise |

## 2. エラータイプの定義

### 2.1 標準エラータイプ

| エラータイプ | HTTPステータス | 説明 | 使用例 |
|-------------|---------------|------|--------|
| `not_found` | 404 | リソースが見つからない | ユーザー、単語、フラッシュカード等 |
| `validation` | 400 | バリデーションエラー | 必須項目不足、形式不正 |
| `permission` | 403 | 権限エラー | アクセス権限なし |
| `conflict` | 409 | 競合エラー | 既存データとの重複 |
| `external_api` | 502 | 外部APIエラー | Google AI API、Firebase等 |
| `general` | 500 | 一般的な内部エラー | その他の予期しないエラー |

### 2.2 エラータイプの使用例

```python
# ユーザーが見つからない場合
raise ServiceException("指定されたユーザーは存在しません", "not_found")

# メールアドレスが既に登録されている場合
raise ServiceException("このメールアドレスは既に登録されています", "conflict")

# 外部APIエラーの場合
raise ServiceException("Google AI APIとの通信に失敗しました", "external_api")
```

## 3. 各層での実装ルール

### 3.1 API層 (main.py)

**実装例**
```python
@app.get("/user/{userId}")
async def get_user_endpoint(userId: str):
    try:
        user = await get_user_service(userId)
        return {"message": "Success", "user": user.to_dict()}
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ステータスコードマッピング
ERROR_TYPE_TO_HTTP_STATUS = {
    "not_found": 404,
    "validation": 400,
    "permission": 403,
    "conflict": 409,
    "external_api": 502,
    "general": 500,
}
```

### 3.2 サービス層
**実装例**
```python
async def get_user_service(user_id: str) -> UserSchema:
    """
    ユーザー情報を取得する
    
    Args:
        user_id: ユーザーID
        
    Returns:
        UserSchema: ユーザー情報
        
    Raises:
        ServiceException: ユーザーが見つからない場合、または処理に失敗した場合
    """
    try:
        user = await firestore_read_user(user_id)
        if not user:
            raise ServiceException("指定されたユーザーは存在しません", "not_found")
        return user
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(f"ユーザー取得処理中にエラーが発生しました: {str(e)}", "general")
```

### 3.3 Firebase層

**実装例**
```python
async def firestore_read_user(user_id: str) -> Optional[UserSchema]:
    """
    Firestoreからユーザー情報を取得する
    
    Args:
        user_id: ユーザーID
        
    Returns:
        Optional[UserSchema]: ユーザー情報（存在しない場合はNone）
        
    Raises:
        ServiceException: Firestoreアクセスエラーの場合
    """
    try:
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return UserSchema.from_dict(doc.to_dict())
        return None
    except Exception as e:
        raise ServiceException(f"Firestoreアクセスエラー: {str(e)}", "external_api")
```

## 4. 現在のエラー処理から新方式への移行

### 4.1 現在の問題点

#### A. パターンの不整合
- **問題**: `Tuple[bool, Optional[str], ...]` と `HTTPException` が混在
- **影響**: コードの可読性低下、保守性の悪化

#### B. 汎用エラーメッセージ
- **問題**: 「単語のセットアップ中にエラーが発生しました」が8つの関数で共通使用
- **影響**: デバッグ時にエラー原因の特定が困難

#### C. エラー分類の不足
- **問題**: HTTPステータスコード500が多用され、適切な分類ができていない
- **影響**: フロントエンドでの適切なエラーハンドリングが困難

### 4.2 移行対象関数（優先度順）

#### 【高優先度】HTTPException混在で不整合
1. `src/services/get_not_compared_media_list.py` - `get_not_compared_media_list`
2. `src/services/get_word_for_extension.py` - `get_word_for_extension`  
3. `src/services/setup_media.py` - `setup_media`
4. `src/services/compare_medias.py` - `compare_medias`

#### 【中優先度】Tupleパターンだが汎用エラーメッセージ
5. `src/services/add_using_flashcard.py` - `add_using_flashcard`
6. `src/services/generate_and_store_image.py` - `generate_and_store_image`
7. `src/services/get_flashcard_list.py` - `get_flashcard_list`
8. `src/services/setup_default_flashcard.py` - `setup_default_flashcard`

#### 【低優先度】一貫性はあるが改善の余地
9. Firebase関連の全関数（41個）
10. Google AI関連の関数（5個）

## 5. 移行手順

### 5.1 Step 1: ServiceExceptionクラスの作成

```python
# src/exceptions/service_exception.py
class ServiceException(Exception):
    def __init__(self, message: str, error_type: str = "general"):
        super().__init__(message)
        self.message = message
        self.error_type = error_type

# src/exceptions/__init__.py
from .service_exception import ServiceException
```

### 5.2 Step 2: 高優先度関数の修正

各関数を以下の手順で修正：

1. **戻り値型の変更**
   ```python
   # 変更前
   async def get_flashcard_list(user_id: str) -> Tuple[bool, Optional[str], Optional[FlashcardResponse]]:
   
   # 変更後  
   async def get_flashcard_list(user_id: str) -> list[FlashcardResponse]:
   ```

2. **エラーハンドリングの変更**
   ```python
   # 変更前
   if error:
       return False, error, None
   
   # 変更後
   if error:
       raise ServiceException(error, "external_api")
   ```

3. **呼び出し側の修正**
   ```python
   # main.py内での呼び出し
   try:
       flashcards = await get_flashcard_list(user_id)
       return {"flashcards": [f.to_dict() for f in flashcards]}
   except ServiceException as se:
       status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
       raise HTTPException(status_code=status_code, detail=se.message)
   ```

### 5.3 Step 3: エラーメッセージの個別化

汎用メッセージを各関数固有のメッセージに変更：

```python
# 変更前（汎用）
"単語のセットアップ中にエラーが発生しました: {str(e)}"

# 変更後（関数固有）
"フラッシュカード一覧の取得中にエラーが発生しました: {str(e)}"  # get_flashcard_list
"未比較メディア一覧の取得中にエラーが発生しました: {str(e)}"      # get_not_compared_media_list
"単語詳細情報の取得中にエラーが発生しました: {str(e)}"            # get_word_for_extension
```

## 6. テストとバリデーション

### 6.1 移行後のテスト項目

1. **正常系テスト**
   - 各関数が正しい戻り値を返すことを確認
   
2. **異常系テスト**
   - 適切な`ServiceException`がraiseされることを確認
   - エラータイプが正しく設定されることを確認
   
3. **HTTPステータスコードテスト**
   - API層で適切なHTTPステータスコードが返されることを確認

### 6.2 移行チェックリスト

- [ ] ServiceExceptionクラスが定義されている
- [ ] 高優先度関数が例外ベースに変更されている
- [ ] main.pyの呼び出し側が修正されている
- [ ] エラーメッセージが関数固有になっている
- [ ] 適切なHTTPステータスコードが返されている
- [ ] 既存のテストが通る
- [ ] 新しいエラーハンドリングのテストが追加されている

## 7. 実装例

### 7.1 修正前後の比較例

#### 修正前 (get_flashcard_list.py)
```python
async def get_flashcard_list(user_id: str) -> Tuple[bool, Optional[str], Optional[FlashcardResponse]]:
    try:
        user_instance, error = await read_user_doc(user_id)
        if error:
            return False, error, None
        if not user_instance:
            return False, "ユーザーが見つかりません", None
        # ... 処理 ...
        return True, None, flashcard_responses
    except Exception as e:
        error_message = f"単語のセットアップ中にエラーが発生しました: {str(e)}"
        return False, error_message, None
```

#### 修正後 (get_flashcard_list.py)
```python
async def get_flashcard_list(user_id: str) -> list[FlashcardResponse]:
    try:
        user_instance = await read_user_doc(user_id)
        if not user_instance:
            raise ServiceException("指定されたユーザーは存在しません", "not_found")
        # ... 処理 ...
        return flashcard_responses
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(f"フラッシュカード一覧の取得中にエラーが発生しました: {str(e)}", "general")
```

#### 修正後 (main.py)
```python
@app.get("/flashcard/{userId}")
async def get_flashcards_endpoint(userId: str):
    try:
        flashcards = await get_flashcard_list(userId)
        return {
            "message": "Flashcards retrieved successfully",
            "flashcards": [flashcard.to_dict() for flashcard in flashcards],
        }
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 8. 今後の保守・拡張指針

### 8.1 新機能開発時の注意点

1. **例外ベースの採用**: 新規関数は必ず例外ベースで実装
2. **適切なエラータイプ**: 状況に応じて適切なエラータイプを選択
3. **具体的なエラーメッセージ**: 汎用的なメッセージは避け、具体的な内容を記載

### 8.2 エラーログの統一

```python
import logging

logger = logging.getLogger(__name__)

try:
    # 処理
    pass
except Exception as e:
    logger.error(f"フラッシュカード取得エラー: user_id={user_id}, error={str(e)}")
    raise ServiceException(f"フラッシュカード一覧の取得中にエラーが発生しました: {str(e)}", "general")
```

### 8.3 モニタリング・アラート

エラータイプ別の監視を実装し、以下の指標を追跡：
- `not_found`エラーの頻度（データ整合性の問題を検出）
- `external_api`エラーの頻度（外部サービスの問題を検出）
- `general`エラーの頻度（予期しないエラーの検出）

## 9. 関連ファイル

- `src/models/exceptions/service_exception.py` - ServiceExceptionクラス定義
- `main.py` - API層でのエラーハンドリング
- `src/services/` - 各サービス関数
- `src/services/firebase/unit/` - Firebase関連関数
- `ERROR_HANDLING_RULES.md` - このドキュメント（ルール定義）

---

このルールに従って、段階的にエラー処理を統一し、保守性とデバッグ性を向上させていきます。