from dataclasses import dataclass
from datetime import datetime

from dataclasses_json import LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PromptTemplateSchema:
    generation_type: str
    target: str
    pre_text: str
    created_at: datetime = None
    updated_at: datetime = None
