from dataclasses import dataclass

from src.services.firebase.schemas.meaning_schema import MeaningSchema
from src.services.firebase.schemas.word_schema import WordSchema


@dataclass
class TranslationSchema:
    word: WordSchema
    meaning: MeaningSchema

    def __init__(self, word: WordSchema, meaning: MeaningSchema):
        self.word = word
        self.meaning = meaning

    def to_dict(self) -> dict:
        """TranslationオブジェクトをFirestore用のdictに変換"""
        return {"word": self.word.to_dict(), "meaning": self.meaning.to_dict()}

    @staticmethod
    def from_dict(data: dict) -> "TranslationSchema":
        """FirestoreのデータからTranslationオブジェクトを作成"""
        return TranslationSchema(
            word=WordSchema.from_dict(data.get("word")),
            meaning=MeaningSchema.from_dict(data.get("meaning")),
        )
