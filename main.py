import json

from fastapi import Body, FastAPI, HTTPException
from pydantic import ValidationError

from src.models.types import NewUser, UpdateFlagRequest, UpdateMemoRequest
from src.services.firebase.create_word_and_meaning import create_word_and_meaning
from src.services.firebase.unit.firestore_flashcard import (
    read_flashcard_doc,
    read_flashcard_docs,
    update_flashcard_doc,
)
from src.services.firebase.unit.firestore_meaning import read_meaning_docs
from src.services.firebase.unit.firestore_user import read_user_doc
from src.services.firebase.unit.firestore_word import read_word_doc
from src.services.setup_flashcard import setup_flashcard
from src.services.setup_user import setup_user
from src.services.words_api import request_words_api

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/word/{word}")
async def get_word(word: str):
    try:
        # Words APIから単語情報を取得
        word_data = request_words_api(word)

        # 翻訳を実行
        translated_data = setup_flashcard(word_data)

        # Firestoreに保存
        create_word_and_meaning(translated_data)

        return translated_data
    except Exception as e:
        return {"error": str(e)}
    
# ユーザー登録API
@app.post("/setup/user")
async def setup_user_endpoint(_user: dict = Body(...)):
    try:
        print(f"\nユーザーのセットアップを開始: {_user}")
        user = NewUser.from_json(json.dumps(_user))
        print(f"Parsed user: {user}")
        success, error, user_id = await setup_user(user)
        if success:
            return {"message": "User setup successful", "userId": user_id}
        else:
            raise HTTPException(status_code=400, detail=error)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✓フラッシュカード一覧取得API
@app.get("/flashcard/{userId}")
async def get_flashcards(userId: str):
    try:
        user_id = userId
        user_instance, error = await read_user_doc(user_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not user_instance:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        # 登録単語が0の場合はフロント側で処理（エラーではない）
        if len(user_instance.flashcard_id_list) == 0:
            return []
        flashcards, error = await read_flashcard_docs(user_instance.flashcard_id_list)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not flashcards:
            raise HTTPException(status_code=404, detail="このユーザーのフラッシュカードが見つかりません")
        print(f"flashcards: {flashcards}")
        return {
            "message": "Flashcards retrieved successfully",
            "flashcards": [flashcard.to_dict() for flashcard in flashcards]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✓フラグ更新API
@app.put("/flashcard/update/checkFlag")
async def update_check_flag_endpoint(_request: dict = Body(...),):
    try:
        # リクエストボディの型を確認
        update_flag_request = UpdateFlagRequest.from_dict(_request)
        flashcard_instance, error = await read_flashcard_doc(flashcard_id=update_flag_request.flashcard_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not flashcard_instance:
            raise HTTPException(status_code=404, detail="フラッシュカードが見つかりません")
        # フラッシュカードの更新
        flashcard_instance.check_flag = update_flag_request.check_flag
        flashcard_instance.updated_at = update_flag_request.flashcard_instance.updated_at
        success, error = await update_flashcard_doc(
            flashcard_id=update_flag_request.flashcard_id,
            flashcard_instance=flashcard_instance
        )
        if success:
            return {"message": "Flashcard update successful"}
        else:
            raise HTTPException(status_code=400, detail=error)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# メモ更新API
@app.put("/flashcard/update/memo")
async def update_flashcard_memo_endpoint(_request: dict = Body(...)):
    try:
        update_memo_request = UpdateMemoRequest.from_dict(_request)
        flashcard_instance, error = await read_flashcard_doc(flashcard_id=update_memo_request.flashcard_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not flashcard_instance:
            raise HTTPException(status_code=404, detail="フラッシュカードが見つかりません")
        # フラッシュカードのメモを更新
        flashcard_instance.memo = update_memo_request.flashcard_instance.memo
        flashcard_instance.updated_at = update_memo_request.flashcard_instance.updated_at
        success, error = await update_flashcard_doc(
            flashcard_id=update_memo_request.flashcard_id,
            flashcard_instance=flashcard_instance
        )
        if success:
            return {"message": "Flashcard memo update successful"}
        else:
            raise HTTPException(status_code=400, detail=error)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 意味取得API
@app.get("/meaning/{wordId}")
async def get_meanings(wordId: str):
    try:
        word_id = wordId
        word_instance, error = await read_word_doc(word_id =word_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if len(word_instance.meaning_id_list) == 0:
            raise HTTPException(status_code=404, detail="この単語には意味が登録されていません。")
        meanings, error = await read_meaning_docs(meaning_ids=word_instance.meaning_id_list)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not meanings:
            raise HTTPException(status_code=404, detail="意味が見つかりません")
        return {
            "message": "Meanings retrieved successfully",
            "meanings": [meaning.to_dict() for meaning in meanings]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))