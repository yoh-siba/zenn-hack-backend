from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import LetterCase, dataclass_json
from pydantic import BaseModel

from src.models.enums import PartOfSpeech
from src.services.firebase.schemas.meaning_schema import MeaningSchema
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
class ModifiedOtherSettingsByGemini:
    generated_other_settings: str
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
    user_id: str
    email: str
    user_name: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UpdateUserRequest:
    user_id: str
    email: str
    user_name: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AddUsingFlashcardRequest:
    user_id: str
    flashcard_id: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UpdateFlagRequest:
    flashcard_id: str
    check_flag: bool


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UpdateMemoRequest:
    flashcard_id: str
    memo: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CreateMediaRequest:
    flashcard_id: str
    old_media_id: Optional[str]
    meaning_id: str
    pos: PartOfSpeech
    word: str
    translation: str
    example_jpn: str
    explanation: str
    core_meaning: Optional[str]
    generation_type: str
    template_id: str
    user_prompt: str
    other_settings: Optional[list[str]]
    allow_generating_person: bool
    input_media_urls: Optional[List[str]]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GetNotComparedMediaResponse:
    comparison_id: str
    flashcard_id: str
    new_media_id: str
    new_media_urls: list[str]


@dataclass
class NotComparedMediaResponseModel:
    comparisonId: str
    flashcardId: str
    newMediaId: str
    newMediaUrls: list[str]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CompareMediasRequest:
    flashcard_id: str
    comparison_id: str
    old_media_id: Optional[str]
    new_media_id: str
    is_selected_new: bool


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CreateTemplateRequest:
    generation_type: str
    target: str
    pre_text: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UpdateTemplateRequest:
    template_id: str
    generation_type: str
    target: str
    pre_text: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UpdateUsingMeaningsRequest:
    flashcard_id: str
    using_meaning_id_list: List[str]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApplyAddMeaningRequest:
    word_id: str
    translation: str
    pronunciation: str
    comment: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApplyModifyMeaningRequest:
    word_id: str
    meaning_id: str
    translation: str
    pronunciation: str
    comment: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UserResponse:
    user_id: str
    email: str
    user_name: str
    flashcard_id_list: List[str]


@dataclass
class UserResponseModel(BaseModel):
    userId: str
    email: str
    userName: str
    flashcardIdList: list[str]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class WordResponse:
    word_id: str
    word: str
    core_meaning: str
    explanation: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MeaningResponse:
    meaning_id: str
    pos: str
    translation: str
    pronunciation: str
    example_eng: str
    example_jpn: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MediaResponse:
    media_id: str
    meaning_id: str
    media_urls: List[str]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FlashcardResponse:
    flashcard_id: str
    word: WordResponse
    meanings: List[MeaningResponse]
    media: MediaResponse
    memo: str
    version: int
    check_flag: bool = False


@dataclass
class WordResponseModel(BaseModel):
    wordId: str
    word: str
    coreMeaning: str
    explanation: str


@dataclass
class MeaningResponseModel(BaseModel):
    meaningId: str
    pos: str
    translation: str
    pronunciation: str
    exampleEng: str
    exampleJpn: str


@dataclass
class MediaResponseModel(BaseModel):
    mediaId: str
    meaningId: str
    mediaUrls: List[str]


@dataclass
class FlashcardResponseModel(BaseModel):
    flashcardId: str
    word: WordResponseModel
    meanings: List[MeaningResponseModel]
    media: MediaResponseModel
    memo: str
    version: int
    checkFlag: bool = False


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TemplatesResponse:
    template_id: str
    generation_type: str
    target: str
    pre_text: str


@dataclass
class TemplatesResponseModel:
    templateId: str
    generationType: str
    target: str
    preText: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CreateTemplateResponse:
    template_id: str


@dataclass
class CreateTemplateResponseModel:
    templateId: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class WordForExtensionResponse:
    message: str
    flashcard_id: str
    word: WordResponse
    meanings: List[MeaningResponse]
    media: MediaResponse


@dataclass
class WordForExtensionResponseModel(BaseModel):
    message: str
    flashcardId: str
    word: WordResponseModel
    meanings: List[MeaningResponseModel]
    media: MediaResponseModel
