from dataclasses import dataclass
from datetime import datetime


@dataclass
class PromptTemplateSchema:
    name: str
    description: str
    generation_type: str
    prompt_text: str
    created_at: datetime = None
    updated_at: datetime = None

    def to_dict(self) -> dict:
        """PromptTemplateオブジェクトをFirestore用のdictに変換"""
        return {
            "name": self.name,
            "description": self.description,
            "generation_type": self.generation_type,
            "prompt_text": self.prompt_text,
            "created_at": self.created_at or datetime.now(),
            "updated_at": self.updated_at or datetime.now(),
        }

    @staticmethod
    def from_dict(data: dict) -> "PromptTemplateSchema":
        """FirestoreのデータからPromptTemplateオブジェクトを作成"""
        return PromptTemplateSchema(
            name=data.get("name"),
            description=data.get("description"),
            generation_type=data.get("generation_type"),
            prompt_text=data.get("prompt_text"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
