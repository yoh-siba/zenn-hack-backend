from fastapi import FastAPI, HTTPException

from src.models.types import NewUser, NewUserRequest
from src.services.firebase.create_word_and_meaning import create_word_and_meaning
from src.services.firebase.unit.firestore_flashcard import read_flashcard_docs
from src.services.firebase.unit.firestore_user import read_user_doc
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
    
@app.post("/setup/user")
async def setup_user_endpoint(_user: NewUserRequest):
    try:
        user = NewUser(**_user.model_dump(by_alias=False))
        success, error, user_id = await setup_user(user)
        if success:
            return {"message": "User setup successful", "userId": user_id}
        else:
            raise HTTPException(status_code=400, detail=error)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/flashcards/{userId}")
async def get_flashcards(userId: str):
    try:
        # ユーザーのフラッシュカードを取得
        user_id = userId
        user_instance, error = await read_user_doc(user_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not user_instance:
            raise HTTPException(status_code=404, detail="User not found")
        # user_instance.flashcard_id_listの配列の長さが 0 の場合はフラッシュカードがない
        if len(user_instance.flashcard_id_list) == 0:
            raise HTTPException(status_code=404, detail="User has no registered flashcards")
        flashcards, error = await read_flashcard_docs(user_instance.flashcard_id_list)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not flashcards:
            raise HTTPException(status_code=404, detail="No flashcards found for this user")
        return [fc.model_dump(by_alias=True) for fc in flashcards]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    