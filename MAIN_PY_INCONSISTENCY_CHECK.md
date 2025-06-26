# main.pyの例外ベース変更に伴う不整合チェック手順

## 概要

src/services/内の関数を例外ベースのエラー処理（ServiceException）に変更したことで、main.pyでの値の受け取り方に不整合が発生しています。この文書では、問題を特定し修正するための手順をまとめます。

## 1. 現状の不整合パターン

### A. 変換済み（例外ベース）の関数
以下の関数は既にServiceExceptionを使用する例外ベースに変換済み：

- `add_using_flashcard` → `None`を返却、エラー時はServiceException
- `setup_media` → `Tuple[str, str, list[str]]`を返却、エラー時はServiceException
- `get_not_compared_media_list` → `list[GetNotComparedMediaResponse]`を返却、エラー時はServiceException
- `compare_medias` → `None`を返却、エラー時はServiceException  
- `get_word_for_extension` → `WordForExtensionResponse`を返却、エラー時はServiceException

### B. 未変換（Tupleベース）の関数
以下の関数はまだ`(success, error, data)`のTupleパターンを使用：

- `setup_user` → `(bool, str)`を返却
- `get_flashcard_list` → `(bool, Optional[str], Optional[FlashcardResponse])`を返却
- Firebase unit関数群（firestore_*モジュール）の大部分

## 2. main.pyでの具体的な不整合箇所

### 🚨 緊急修正が必要（実行時エラーの可能性）

#### `setup_user_endpoint` (118-128行目)
```python
# 現在のコード（問題あり）
success, error = await setup_user(user)
if success:
    return {"message": "User setup successful"}
else:
    raise HTTPException(status_code=500, detail=error)
```

**問題**: `setup_user`が例外ベースに変更されているが、Tupleのアンパックを試行

**修正方法**:
```python
try:
    await setup_user(user)
    return {"message": "User setup successful"}
except ServiceException as se:
    status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
    raise HTTPException(status_code=status_code, detail=se.message)
```

### ⚠️ 確認が必要（現時点では動作するが一貫性なし）

#### `get_flashcards_endpoint` (228-242行目)
```python
# 現在のコード
success, error, flashcard_responses = await get_flashcard_list(user_id)
if not success:
    if error == "ユーザーが見つかりません":
        raise HTTPException(status_code=404, detail=error)
    else:
        raise HTTPException(status_code=500, detail=error)
```

**問題**: `get_flashcard_list`がまだTupleパターンだが、一貫性のため例外ベースに変更すべき

#### Firebase unit関数を使用している箇所
- `update_check_flag_endpoint` (254-271行目)
- `update_flashcard_memo_endpoint` (279-300行目)  
- `update_using_meaning_id_list_endpoint` (308-330行目)
- `get_meanings_endpoint` (459-481行目)
- `get_template_endpoint` (495-508行目)
- `create_template_endpoint` (532-560行目)
- `update_template_endpoint` (573-611行目)

## 3. チェック手順

### Step 1: 緊急修正（実行時エラー回避）

1. **`setup_user_endpoint`の修正**
   ```bash
   # 該当箇所の確認
   grep -n "success, error = await setup_user" src/main.py
   ```

2. **他の変換済み関数の呼び出し確認**
   ```bash
   # 変換済み関数の呼び出しパターンをチェック
   grep -n "success.*await.*add_using_flashcard\|setup_media\|get_not_compared_media_list\|compare_medias\|get_word_for_extension" main.py
   ```

### Step 2: 一貫性チェック

1. **Tupleパターンの検索**
   ```bash
   # main.py内でTupleアンパックしている箇所を全て検索
   grep -n "success.*error.*await" main.py
   grep -n ".*,.*error.*await" main.py
   ```

2. **ServiceExceptionハンドリングの確認**
   ```bash
   # ServiceExceptionを正しく捕捉している箇所を確認
   grep -n "except ServiceException" main.py
   ```

### Step 3: 残存関数の変換優先度決定

#### 高優先度（main.pyで直接使用）
- [ ] `setup_user` → 例外ベースに変更
- [ ] `get_flashcard_list` → 例外ベースに変更

#### 中優先度（間接的に使用）
- [ ] `read_user_doc`
- [ ] `update_user_doc` 
- [ ] `delete_user_doc`
- [ ] `update_flashcard_doc_on_check_flag`
- [ ] `update_flashcard_doc_on_memo`
- [ ] `update_flashcard_doc_on_using_meaning_id_list`

#### 低優先度（管理機能）
- [ ] `read_word_doc`
- [ ] `read_meaning_docs`
- [ ] `read_prompt_template_docs`
- [ ] `create_prompt_template_doc`
- [ ] `update_prompt_template_doc`

## 4. 修正テンプレート

### 変換前（Tupleパターン）
```python
success, error = await some_function(params)
if success:
    return {"message": "Success"}
else:
    raise HTTPException(status_code=500, detail=error)
```

### 変換後（例外ベース）
```python
try:
    await some_function(params)
    return {"message": "Success"}
except ServiceException as se:
    status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
    raise HTTPException(status_code=status_code, detail=se.message)
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

### データ返却がある場合
```python
try:
    result = await some_function(params)
    return {"message": "Success", "data": result}
except ServiceException as se:
    status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
    raise HTTPException(status_code=status_code, detail=se.message)
```

## 5. 検証手順

### 修正後の動作確認
```bash
# テストの実行
python -m pytest test/test_main.py -v

# 特定のエンドポイントの動作確認
curl -X POST http://localhost:8000/user/setup \
  -H "Content-Type: application/json" \
  -d '{"userId": "test", "email": "test@test.com", "userName": "テスト"}'
```

### エラーハンドリングの確認
```bash
# 無効なデータでのテスト
curl -X POST http://localhost:8000/user/setup \
  -H "Content-Type: application/json" \
  -d '{"userId": "", "email": "invalid", "userName": ""}'
```

## 6. 完了チェックリスト

- [ ] Step 1: 緊急修正完了（実行時エラー解消）
- [ ] Step 2: 全てのTupleパターン特定完了
- [ ] Step 3: 優先度順に関数変換完了
- [ ] Step 4: main.pyの全エンドポイント修正完了
- [ ] Step 5: テスト実行・動作確認完了
- [ ] Step 6: エラーハンドリングテスト完了

## 7. その他の対応対象ファイル（codebase全体の残存Tupleパターン）

### 🔴 完全未変換（高優先度）

#### `src/services/get_flashcard_list.py`
- **状態**: Tupleパターンのまま
- **関数**: `get_flashcard_list(user_id: str)` 
- **戻り値**: `Tuple[bool, Optional[str], Optional[FlashcardResponse]]`
- **問題箇所**: 15, 28, 30, 36, 38, 43, 45, 48, 50, 51, 53, 64, 68行目
- **修正内容**: 完全な例外ベース変換が必要

### 🟡 部分変換済み（依存関係の修正が必要）

#### `src/services/add_using_flashcard.py`
- **状態**: メイン関数は変換済み、依存関数がTupleパターン
- **問題箇所**: 
  - 24, 29行目: `copy_flashcard_doc()`, `update_user_doc_add_using_flashcard()`のTuple呼び出し
  - 55, 56行目: `__main__`セクションのTupleアンパック
- **修正内容**: 依存関数の変換と`__main__`セクション修正

#### `src/services/compare_medias.py`
- **状態**: メイン関数は変換済み、Firebase unit関数がTupleパターン
- **問題箇所**: 
  - 26, 35行目: Firebase unit関数のTuple呼び出し
  - 33, 39行目: `if not success:`パターン
- **修正内容**: Firebase unit関数の戻り値処理修正

#### `src/services/generate_and_store_image.py`
- **状態**: メイン関数は変換済み、一部依存関数がTupleパターン
- **問題箇所**:
  - 45行目: `create_image_url_from_image()`のTuple呼び出し
  - 49行目: `if not success:`パターン
  - 71-84行目: `__main__`セクションのTupleアンパック
- **修正内容**: 依存関数の変換と`__main__`セクション修正

#### `src/services/get_not_compared_media_list.py`
- **状態**: メイン関数は変換済み、Firebase unit関数がTupleパターン
- **問題箇所**:
  - 26, 34, 46, 49行目: Firebase unit関数のTuple呼び出し
  - 27, 35, 47, 50行目: `if error:`パターン
- **修正内容**: Firebase unit関数の戻り値処理修正

#### `src/services/get_word_for_extension.py`
- **状態**: メイン関数は変換済み、Firebase unit関数がTupleパターン
- **問題箇所**:
  - 30, 33, 38, 41行目: Firebase unit関数のTuple呼び出し
  - 31, 34, 39, 42行目: `if error:`パターン
- **修正内容**: Firebase unit関数の戻り値処理修正

#### `src/services/setup_default_flashcard.py`
- **状態**: メイン関数は変換済み、多数の依存関数がTupleパターン
- **問題箇所**:
  - 101, 104行目: `create_word_and_meaning()`のTuple呼び出し
  - 137, 141行目: `create_image_url_from_image()`のTuple呼び出し
  - 165, 166行目: `create_media_doc()`のTuple呼び出し
  - 183, 184行目: `create_flashcard_doc()`のTuple呼び出し
  - 205, 208行目: `update_media_doc()`のTuple呼び出し
- **修正内容**: 多数の依存関数の戻り値処理修正

### 🟢 テストファイル（低優先度）

#### `test/firestore/firestore_prompt_template.py`
- **問題箇所**: 13, 14行目
- **修正内容**: テストコードの例外ハンドリング対応

#### `test/firestore/firestore_user.py`
- **問題箇所**: 45, 60, 79, 92行目
- **修正内容**: テストコードの例外ハンドリング対応

#### `test/firestore/firestore_comparison.py`
- **問題箇所**: 51, 68, 86, 101行目
- **修正内容**: テストコードの例外ハンドリング対応

### ✅ 変換完了済み（確認済み）
- `src/services/firebase/unit/firestore_flashcard.py`
- `src/services/firebase/unit/firestore_media.py`
- `src/services/firebase/unit/firestore_word.py`
- `src/services/firebase/unit/cloud_storage_image.py`

## 8. 全体的な変換戦略

### Phase 1: 緊急修正（実行時エラー防止） ✅ 完了
1. ✅ `main.py`の`setup_user_endpoint`修正
2. ✅ `get_flashcard_list.py`の完全変換

### Phase 2: 依存関数の変換 ✅ 完了
1. ✅ 未変換のFirebase unit関数の変換
2. ✅ `copy_flashcard_doc()`, `update_user_doc_add_using_flashcard()`等の変換

### Phase 3: サービス層の依存関係修正 ✅ 完了
1. ✅ 部分変換済みファイルの依存関数呼び出し修正
2. ✅ `__main__`セクションの修正

### Phase 4: テストコード対応 ✅ 完了
1. ✅ 全テストファイルの例外ハンドリング対応
2. ✅ テスト実行・動作確認

### **🚨 Phase 5: 追加発見された残存Tupleパターン対応**

#### 高優先度（関数シグネチャ変更が必要）
1. **`src/services/setup_media.py`**
   - **問題**: 関数シグネチャが`Tuple[str, str, list[str]]`のまま
   - **対応**: 戻り値型を適切なクラスに変更
   - **影響度**: High（main.pyで直接使用）

2. **`src/services/google_ai/unit/request_gemini.py`**
   - **問題**: `request_gemini_json()`が`Tuple[BaseModel, TokenInfo]`を返す
   - **対応**: 戻り値型を適切なクラスに変更
   - **影響度**: Medium

#### 中優先度（関数呼び出し修正が必要）
3. **`src/services/create_word_and_meaning.py`**
   - **問題**: 28, 36, 45行目でTupleアンパック使用
   - **対応**: Firebase unit関数呼び出しを例外ベースに修正
   - **影響度**: High（他のサービスから使用される）

4. **`src/services/setup_default_flashcard.py`**
   - **問題**: 101, 137, 165, 183, 205行目で広範囲にTupleアンパック使用
   - **対応**: 全ての依存関数呼び出しを例外ベースに修正
   - **影響度**: Medium

5. **`src/services/generate_and_store_image.py`**
   - **問題**: 45行目で`create_image_url_from_image`のTupleアンパック
   - **対応**: 関数呼び出しを例外ベースに修正
   - **影響度**: Medium

6. **`src/services/add_using_flashcard.py`**
   - **問題**: 24, 29行目でTupleアンパック使用
   - **対応**: Firebase unit関数呼び出しを例外ベースに修正
   - **影響度**: Medium

7. **`src/services/setup_user.py`**
   - **問題**: 42行目で`create_user_doc`のTupleアンパック
   - **対応**: 関数呼び出しを例外ベースに修正
   - **影響度**: High

#### 低優先度（クリーンアップ）
8. **Print文の削除**
   - `setup_media.py` (155行目)
   - `setup_default_flashcard.py` (69, 94, 99, 106, 125, 169, 187行目)
   - **対応**: デバッグ用print文をログまたは削除

### 更新された変換優先度マトリックス

| ファイル | 優先度 | 影響度 | 工数 | 理由 | 状態 |
|---------|--------|--------|------|------|------|
| `main.py` (setup_user_endpoint) | 🔥 | High | Small | 実行時エラーの可能性 | ✅ 完了 |
| `get_flashcard_list.py` | 🔥 | High | Medium | main.pyで直接使用 | ✅ 完了 |
| Firebase unit 残存関数 | ⚠️ | Medium | Large | 多数の依存関係あり | ✅ 完了 |
| 部分変換済みサービス層 | ⚠️ | Medium | Medium | 一貫性のため | ✅ 完了 |
| テストファイル | ℹ️ | Low | Small | 開発時のみ影響 | ✅ 完了 |

### **🚨 Phase 5: 追加対応が必要なファイル**

| ファイル | 優先度 | 影響度 | 工数 | 理由 | 状態 |
|---------|--------|--------|------|------|------|
| `setup_media.py` | 🔥 | High | Medium | main.pyで直接使用、シグネチャ変更必要 | ❌ 未対応 |
| `create_word_and_meaning.py` | 🔥 | High | Small | 広く使用される、Tupleアンパック残存 | ❌ 未対応 |
| `setup_user.py` | 🔥 | High | Small | main.pyで直接使用、Tupleアンパック残存 | ❌ 未対応 |
| `setup_default_flashcard.py` | ⚠️ | Medium | Large | 広範囲にTupleパターン使用 | ❌ 未対応 |
| `add_using_flashcard.py` | ⚠️ | Medium | Small | Tupleアンパック残存 | ❌ 未対応 |
| `generate_and_store_image.py` | ⚠️ | Medium | Small | Tupleアンパック残存 | ❌ 未対応 |
| `request_gemini.py` | ℹ️ | Medium | Medium | 戻り値シグネチャ変更必要 | ❌ 未対応 |
| Print文削除 | ℹ️ | Low | Small | クリーンアップ | ❌ 未対応 |

## 9. Phase 5: 詳細な修正手順

### 🔥 緊急修正（実行時エラー防止）

#### 1. `setup_media.py` 修正手順
```bash
# 現在の問題のある関数シグネチャ
async def setup_media(...) -> Tuple[str, str, list[str]]:

# 修正後の推奨パターン
async def setup_media(...) -> SetupMediaResponse:
    # SetupMediaResponseクラスを新規作成
    # comparison_id, media_id, media_urls を含む
```

#### 2. `create_word_and_meaning.py` 修正手順
```bash
# 問題箇所の修正パターン
# 修正前:
success, error, word_id = await create_word_doc(word_instance)
if not success:
    raise ServiceException(f"単語の作成に失敗しました: {error}", "external_api")

# 修正後:
word_id = await create_word_doc(word_instance)
```

#### 3. `setup_user.py` 修正手順
```bash
# 問題箇所: 42行目
# 修正前:
success, error_message = await create_user_doc(user_id=_user.user_id, user_instance=user_instance)
if not success:
    raise ServiceException(f"ユーザーの作成に失敗しました: {error_message}", "external_api")

# 修正後:
await create_user_doc(user_id=_user.user_id, user_instance=user_instance)
```

### ⚠️ 中優先度修正

#### 4. `setup_default_flashcard.py` 修正箇所
- Line 101: `create_word_and_meaning` → 例外ベース呼び出し
- Line 137: `create_image_url_from_image` → 例外ベース呼び出し
- Line 165: `create_media_doc` → 例外ベース呼び出し
- Line 183: `create_flashcard_doc` → 例外ベース呼び出し
- Line 205: `update_media_doc` → 例外ベース呼び出し

#### 5. `add_using_flashcard.py` 修正箇所
- Line 24: `copy_flashcard_doc` → 例外ベース呼び出し
- Line 29: `update_user_doc_add_using_flashcard` → 例外ベース呼び出し

#### 6. `generate_and_store_image.py` 修正箇所
- Line 45: `create_image_url_from_image` → 例外ベース呼び出し

### ℹ️ 低優先度修正

#### 7. `request_gemini.py` 修正手順
```bash
# 現在の関数シグネチャ
async def request_gemini_json(...) -> Tuple[BaseModel, TokenInfo]:

# 修正後の推奨パターン
async def request_gemini_json(...) -> GeminiResponse:
    # GeminiResponseクラスを新規作成
    # parsed_response, token_info を含む
```

#### 8. Print文削除
- `setup_media.py`: Line 155
- `setup_default_flashcard.py`: Lines 69, 94, 99, 106, 125, 169, 187

### 🧪 Phase 5 完了チェックリスト

- [ ] `setup_media.py` - 関数シグネチャ変更とmain.py修正
- [ ] `create_word_and_meaning.py` - Tupleアンパック削除
- [ ] `setup_user.py` - Tupleアンパック削除
- [ ] `setup_default_flashcard.py` - 全Tupleアンパック削除
- [ ] `add_using_flashcard.py` - Tupleアンパック削除
- [ ] `generate_and_store_image.py` - Tupleアンパック削除
- [ ] `request_gemini.py` - 関数シグネチャ変更
- [ ] Print文削除 - デバッグ出力のクリーンアップ
- [ ] 全APIエンドポイントのテスト実行
- [ ] エラーハンドリングの一貫性確認

## 注意事項

1. **段階的な修正**: 一度に全てを変更せず、高優先度から順番に修正
2. **テストの実行**: 各修正後に関連テストを実行
3. **エラーメッセージの一貫性**: ERROR_HANDLING_RULES.mdに従った適切なエラータイプを使用
4. **ログの確認**: 修正後にログでエラーハンドリングが正しく動作しているか確認
5. **依存関係の把握**: 修正順序を間違えると多数のファイルに影響するため注意

この手順に従って修正することで、例外ベースのエラー処理への移行を安全かつ確実に完了できます。