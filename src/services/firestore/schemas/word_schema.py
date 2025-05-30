from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class WordSchema:
    word: str
    meaning_id_list: List[str]
    core_meaning: Optional[str]
    explanation: str
    created_at: datetime = None
    updated_at: datetime = None

    def to_dict(self) -> dict:
        """WordオブジェクトをFirestore用のdictに変換"""
        return {
            "word": self.word,
            "meaning_id_list": self.meaning_id_list,
            "core_meaning": self.core_meaning,
            "explanation": self.explanation,
            "created_at": self.created_at or datetime.now(),
            "updated_at": self.updated_at or datetime.now(),
        }

    @staticmethod
    def from_dict(data: dict) -> "WordSchema":
        """Firestoreのデータからwordオブジェクトを作成"""

        return WordSchema(
            word=data.get("word"),
            meaning_id_list=data.get("meaning_id_list"),
            core_meaning=data.get("core_meaning"),
            explanation=data.get("explanation"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
