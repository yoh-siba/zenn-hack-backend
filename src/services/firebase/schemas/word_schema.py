from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from dataclasses_json import LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class WordSchema:
    word: str
    meaning_id_list: List[str]
    core_meaning: Optional[str]
    explanation: str
    created_at: datetime = None
    updated_at: datetime = None