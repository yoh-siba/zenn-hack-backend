from dataclasses import dataclass

from dataclasses_json import LetterCase, dataclass_json

from src.services.firebase.schemas.meaning_schema import MeaningSchema
from src.services.firebase.schemas.word_schema import WordSchema


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TranslationSchema:
    word: WordSchema
    meaning: MeaningSchema

    def __init__(self, word: WordSchema, meaning: MeaningSchema):
        self.word = word
        self.meaning = meaning