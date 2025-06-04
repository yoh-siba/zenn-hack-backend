from dataclasses import dataclass
from datetime import datetime

from dataclasses_json import LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PromptTemplateSchema:
    name: str
    description: str
    generation_type: str
    prompt_text: str
    created_at: datetime = None
    updated_at: datetime = None