from datetime import datetime

from src.services.google_ai.unit.request_gemini import request_gemini_json
from src.models.types import TranslationByGemini
from src.services.firestore.schemas.meaning_schema import MeaningSchema


# TODO: ImageGen用のプロンプトを作成するためのAPIリクエストを行う


def generate_translation(_content:str) -> list[MeaningSchema]:
    
    try:
        response = request_gemini_json(_contents=_content, _schema=list[TranslationByGemini])
        if response is None:
            raise ValueError("Response is None")
        if not isinstance(response, list):
            raise ValueError("Response is not a list")
        if len(response) == 0:
            raise ValueError("Response list is empty")
        result = []
        for item in response:
            if not isinstance(item, TranslationByGemini):
                raise ValueError("Item is not of type TranslationByGemini")
            meaning = MeaningSchema(
                pos=item.pos,
                definition=item.definition,
                pronunciation=item.pronunciation,
                example_eng=item.example_eng,
                example_jpn=item.example_jpn,
                rank=item.rank,
                created_at= datetime.now(),
                updated_at=datetime.now(),
            )   
            result.append(meaning)
        return result
    except Exception as e:
        print(e)
        raise ValueError("翻訳の生成に失敗しました") from e