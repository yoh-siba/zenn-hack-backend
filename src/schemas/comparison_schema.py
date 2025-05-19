from dataclasses import dataclass
from datetime import datetime

@dataclass
class ComparisonSchema:
    comparisonId: str
    flashcardId: str
    oldMediaId: str
    newMediaId: str
    selected: str
    created_at: datetime = None
    updated_at: datetime = None

    def to_dict(self) -> dict:
        """ComparisonオブジェクトをFirestore用のdictに変換"""
        return {
            'comparisonId': self.comparisonId,
            'flashcardId': self.flashcardId,
            'oldMediaId': self.oldMediaId,
            'newMediaId': self.newMediaId,
            'selected': self.selected,
            'created_at': self.created_at or datetime.now(),
            'updated_at': self.updated_at or datetime.now()
        }

    @staticmethod
    def from_dict(data: dict) -> 'ComparisonSchema':
        """FirestoreのデータからComparisonオブジェクトを作成"""
        return ComparisonSchema(
            comparisonId=data.get('comparisonId'),
            flashcardId=data.get('flashcardId'),
            oldMediaId=data.get('oldMediaId'),
            newMediaId=data.get('newMediaId'),
            selected=data.get('selected'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        ) 