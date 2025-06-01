from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class FlashcardSchema:
    word_id: str
    using_meaning_list: List[str]
    memo: str
    media_id_list: List[str]
    current_media_id: str
    comparison_id: Optional[str]
    created_by: str
    version: int
    check_flag: bool
    created_at: datetime = None
    updated_at: datetime = None

    def to_dict(self) -> dict:
        """FlashcardオブジェクトをFirestore用のdictに変換"""
        return {
            "word_id": self.word_id,
            "using_meaning_list": self.using_meaning_list,
            "memo": self.memo,
            "media_id_list": self.media_id_list,
            "current_media_id": self.current_media_id,
            "comparison_id": self.comparison_id,
            "created_by": self.created_by,
            "version": self.version,
            "check_flag": self.check_flag,
            "created_at": self.created_at or datetime.now(),
            "updated_at": self.updated_at or datetime.now(),
        }

    @staticmethod
    def from_dict(data: dict) -> "FlashcardSchema":
        """FirestoreのデータからFlashcardオブジェクトを作成"""
        return FlashcardSchema(
            word_id=data.get("word_id"),
            using_meaning_list=data.get("using_meaning_list", []),
            memo=data.get("memo"),
            media_id_list=data.get("media_id_list", []),
            current_media_id=data.get("current_media_id"),
            comparison_id=data.get("comparison_id"),
            created_by=data.get("created_by"),
            version=data.get("version"),
            check_flag=data.get("check_flag"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
