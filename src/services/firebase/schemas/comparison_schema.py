from dataclasses import dataclass
from datetime import datetime


@dataclass
class ComparisonSchema:
    flashcard_id: str
    oldMedia_id: str
    new_media_id: str
    selected: str
    created_at: datetime = None
    updated_at: datetime = None

    def to_dict(self) -> dict:
        """ComparisonオブジェクトをFirestore用のdictに変換"""
        return {
            "flashcard_id": self.flashcard_id,
            "oldMedia_id": self.oldMedia_id,
            "new_media_id": self.new_media_id,
            "selected": self.selected,
            "created_at": self.created_at or datetime.now(),
            "updated_at": self.updated_at or datetime.now(),
        }

    @staticmethod
    def from_dict(data: dict) -> "ComparisonSchema":
        """FirestoreのデータからComparisonオブジェクトを作成"""
        return ComparisonSchema(
            flashcard_id=data.get("flashcard_id"),
            oldMedia_id=data.get("oldMedia_id"),
            new_media_id=data.get("new_media_id"),
            selected=data.get("selected"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
