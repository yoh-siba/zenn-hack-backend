from dataclasses import dataclass
from typing import List, Optional

from src.models.enums import PartOfSpeech
from src.services.firestore.schemas.meaning_schema import MeaningSchema
from src.services.firestore.schemas.word_schema import WordSchema


@dataclass
class WordResult:
    definition: str
    partOfSpeech: PartOfSpeech
    synonyms: List[str]
    typeOf: List[str]
    hasTypes: Optional[List[str]] = None
    derivation: Optional[List[str]] = None
    examples: Optional[List[str]] = None


@dataclass
class Syllables:
    count: int
    list: List[str]


@dataclass
class Pronunciation:
    all: str


@dataclass
class WordsAPIResponse:
    word: str
    results: List[WordResult]
    syllables: Syllables
    pronunciation: Pronunciation
    frequency: float


@dataclass
class DefAndExample:
    part_of_speech: PartOfSpeech
    definition: str
    example: str


@dataclass
class WordAndMeanings:
    word: WordSchema
    meanings: List[MeaningSchema]


@dataclass
class TranslationByGemini:
    pos: PartOfSpeech
    definition_jpn: str
    definition_eng: str
    pronunciation: str
    example_eng: str
    example_jpn: str
    rank: int

    def to_dict(self) -> dict:
        """TranslationMeaningオブジェクトをdictに変換"""
        return {
            "pos": self.pos,
            "definition_jpn": self.definition_jpn,
            "definition_eng": self.definition_eng,
            "pronunciation": self.pronunciation,
            "example_eng": self.example_eng,
            "example_jpn": self.example_jpn,
            "rank": self.rank,
        }


@dataclass
class ExplanationByGemini:
    explanation: str
    core_meaning: Optional[str]

    def to_dict(self) -> dict:
        return {
            "explanation": self.explanation,
            "core_meaning": self.core_meaning if self.core_meaning else "",
        }


@dataclass
class PromptForImagenByGemini:
    generated_prompt: str

    def to_dict(self) -> dict:
        return {
            "generated_prompt": self.generated_prompt,
        }
