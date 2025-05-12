from typing import List, Dict, Any, TypedDict, Optional

class WordResult(TypedDict):
    definition: str
    partOfSpeech: str
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

class Definition(TypedDict):
    definition: str
    example: str

class Translation(TypedDict):
    part_of_speech: str
    meaning: str
    example_en: str
    example_ja: str

Definitions = List[Definition]
Translations = List[Translation] 