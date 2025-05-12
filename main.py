from fastapi import FastAPI
from services.word_service import request_words_api
from services.translation_service import translate_and_prioritize
from services.firestore_service import save_to_firestore
from models.types import Definitions

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/word/{word}")
async def process_word(word: str):
    try:
        # 単語の検索
        word_data = request_words_api(word)
        
        # 定義と例文のペアを作成
        definitions = []
        for result in word_data.get('results', []):
            if 'definition' in result and 'examples' in result and result['examples']:
                definitions.append({
                    'definition': result['definition'],
                    'example': result['examples'][0]
                })
        
        # 翻訳と優先順位付け
        translations = translate_and_prioritize(definitions)
        
        # Firestoreに保存
        save_to_firestore(translations, word)
        
        return {
            "status": "success",
            "word": word,
            "translations": translations
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }