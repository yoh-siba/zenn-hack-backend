from datetime import datetime
from typing import List

from dataclasses_json import LetterCase, dataclass_json
from pydantic.dataclasses import dataclass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UserSchema:
    email: str
    display_name: str
    flashcard_id_list: List[str]
    created_at: datetime = None
    updated_at: datetime = None