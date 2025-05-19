from typing import List, Dict, Any, TypedDict, Optional
from enum import Enum

class PartOfSpeech(str, Enum):
    NOUN = "noun"
    VERB = "verb"
    ADVERB = "adverb"
    ADJECTIVE = "adjective"

class WordResult(TypedDict):
    definition: str
    partOfSpeech: PartOfSpeech
    synonyms: List[str]
    typeOf: List[str]
    hasTypes: Optional[List[str]]
    derivation: Optional[List[str]]
    examples: Optional[List[str]]

class Syllables(TypedDict):
    count: int
    list: List[str]

class Pronunciation(TypedDict):
    all: str

class WordData(TypedDict):
    word: str
    results: List[WordResult]
    syllables: Syllables
    pronunciation: Pronunciation
    frequency: float

class DefAndExample(TypedDict):
    part_of_speech: PartOfSpeech
    definition: str
    example: str

class Translation(TypedDict):
    part_of_speech: PartOfSpeech
    meaning: str
    example_en: str
    example_ja: str

class WordInstance(TypedDict):
    word: str
    defs_and_examples: List[DefAndExample]

Translations = List[Translation] 