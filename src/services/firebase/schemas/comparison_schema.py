from dataclasses import dataclass
from datetime import datetime

from dataclasses_json import LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ComparisonSchema:
    flashcard_id: str
    oldMedia_id: str
    new_media_id: str
    selected: str
    created_at: datetime = None
    updated_at: datetime = None
