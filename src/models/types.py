from typing import List, Optional
from enum import Enum
from dataclasses import dataclass

class PartOfSpeech(str, Enum):
    NOUN = "noun"
    VERB = "verb"
    ADVERB = "adverb"
    ADJECTIVE = "adjective"

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
class WordsAPIInstance:
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
class Translation:
    part_of_speech: PartOfSpeech
    meaning: str
    example_en: str
    example_ja: str

@dataclass
class WordInstance:
    word: str
    defs_and_examples: List[DefAndExample]

Translations = List[Translation] 