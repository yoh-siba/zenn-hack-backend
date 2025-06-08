from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import LetterCase, dataclass_json

from src.models.enums import PartOfSpeech
from src.services.firebase.schemas.meaning_schema import MeaningSchema
from src.services.firebase.schemas.media_schema import MediaSchema
from src.services.firebase.schemas.word_schema import WordSchema


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

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TranslationByGemini:
    pos: PartOfSpeech
    definition_jpn: str
    definition_eng: str
    pronunciation: str
    example_eng: str
    example_jpn: str
    rank: int


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ExplanationByGemini:
    explanation: str
    core_meaning: Optional[str]

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PromptForImagenByGemini:
    generated_prompt: str
    prompt_token_count: int
    candidates_token_count: int
    total_token_count: int


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TokenInfo:
    prompt_token_count: int
    candidates_token_count: int
    total_token_count: int


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class SetUpUserRequest:
    email: str
    display_name: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UpdateUserRequest:
    user_id: str
    email: str
    display_name: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UpdateFlagRequest:
    flashcard_id: str
    change_flag: bool


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UpdateMemoRequest:
    flashcard_id: str
    memo: str
    
@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UpdateUsingMeaningsRequest:
    flashcard_id: str
    using_meaning_id_list: List[str]

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApplyAddMeaningRequest:
    word_id: str
    definition: str
    pronunciation: str
    comment: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApplyModifyMeaningRequest:
    word_id: str
    meaning_id: str
    definition: str
    pronunciation: str
    comment: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FlashcardResponse:
    flashcard_id: str
    word: str
    meanings: List[MeaningSchema]
    media: MediaSchema
    memo: str
    version: int
    check_flag: bool = False