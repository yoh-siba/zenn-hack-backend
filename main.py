from fastapi import FastAPI

from src.services.firestore.create_word_and_meaning import save_word_to_firestore
from src.services.setup_word_and_meaning import translate_text
from src.services.word_service import request_words_api

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
        translated_data = translate_text(word_data)

        # Firestoreに保存
        save_word_to_firestore(translated_data)

        return translated_data
    except Exception as e:
        return {"error": str(e)}
