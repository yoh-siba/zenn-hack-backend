from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from dataclasses_json import LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MediaSchema:
    flashcard_id: str
    meaning_id: str
    media_urls: List[str]
    generation_type: str
    template_id: Optional[str]
    user_prompt: str
    generated_prompt: str
    input_media_urls: Optional[List[str]]
    prompt_token_count: int
    candidates_token_count: int
    total_token_count: int
    created_by: str
    created_at: datetime = None
    updated_at: datetime = None