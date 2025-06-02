from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class MediaSchema:
    flashcard_id: str
    meaning_id: str
    media_urls: List[str]
    generation_type: str
    template_id: Optional[str]
    userPrompt: str
    generated_prompt: str
    input_media_urls: Optional[List[str]]
    prompt_token_count: int
    candidates_token_count: int
    total_token_count: int
    created_by: str
    created_at: datetime = None
    updated_at: datetime = None

    def to_dict(self) -> dict:
        """MediaオブジェクトをFirestore用のdictに変換"""
        return {
            "flashcard_id": self.flashcard_id,
            "meaning_id": self.meaning_id,
            "media_urls": self.media_urls,
            "generation_type": self.generation_type,
            "template_id": self.template_id,
            "userPrompt": self.userPrompt,
            "generated_prompt": self.generated_prompt,
            "input_media_urls": self.input_media_urls,
            "prompt_token_count": self.prompt_token_count,
            "candidates_token_count": self.candidates_token_count,
            "total_token_count": self.total_token_count,
            "created_by": self.created_by,
            "created_at": self.created_at or datetime.now(),
            "updated_at": self.updated_at or datetime.now(),
        }

    @staticmethod
    def from_dict(data: dict) -> "MediaSchema":
        """FirestoreのデータからMediaオブジェクトを作成"""
        return MediaSchema(
            flashcard_id=data.get("flashcard_id"),
            meaning_id=data.get("meaning_id"),
            media_urls=data.get("media_urls", []),
            generation_type=data.get("generation_type"),
            template_id=data.get("template_id"),
            userPrompt=data.get("userPrompt"),
            generated_prompt=data.get("generated_prompt"),
            input_media_urls=data.get("input_media_urls"),
            prompt_token_count=data.get("prompt_token_count"),
            candidates_token_count=data.get("candidates_token_count"),
            total_token_count=data.get("total_token_count"),
            created_by=data.get("created_by"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
