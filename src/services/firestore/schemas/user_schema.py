from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class UserSchema:
    email: str
    display_name: str
    flashcard_id_list: List[str]
    created_at: datetime = None
    updated_at: datetime = None

    def to_dict(self) -> dict:
        """UserオブジェクトをFirestore用のdictに変換"""
        return {
            "email": self.email,
            "display_name": self.display_name,
            "flashcard_id_list": self.flashcard_id_list,
            "created_at": self.created_at or datetime.now(),
            "updated_at": self.updated_at or datetime.now(),
        }

    @staticmethod
    def from_dict(data: dict) -> "UserSchema":
        """FirestoreのデータからUserオブジェクトを作成"""
        return UserSchema(
            email=data.get("email"),
            display_name=data.get("display_name"),
            flashcard_id_list=data.get("flashcard_id_list", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
