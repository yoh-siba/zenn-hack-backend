from dataclasses import dataclass, field
from datetime import datetime

from dataclasses_json import LetterCase, dataclass_json

from src.models.enums import PartOfSpeech, PartOfSpeechField


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MeaningSchema:
    pos: PartOfSpeech = field(metadata=PartOfSpeechField)
    definition: str
    pronunciation: str
    example_eng: str
    example_jpn: str
    rank: int
    created_at: datetime = None
    updated_at: datetime = None