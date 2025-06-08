from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from dataclasses_json import LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FlashcardSchema:
    word_id: str
    using_meaning_id_list: List[str]
    memo: str
    media_id_list: List[str]
    current_media_id: str
    comparison_id: Optional[str]
    created_by: str
    version: int
    check_flag: bool
    created_at: datetime = None
    updated_at: datetime = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FlashcardSchemaWithId:
    flashcard_id: str
    word_id: str
    using_meaning_id_list: List[str]
    memo: str
    media_id_list: List[str]
    current_media_id: str
    comparison_id: Optional[str]
    created_by: str
    version: int
    check_flag: bool
    created_at: datetime = None
    updated_at: datetime = None