from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class FlashcardSchema:
    flashcardId: str
    wordId: str
    usingMeaningIdList: List[str]
    memo: str
    mediaIdList: List[str]
    currentMediaId: str
    comparisonId: Optional[str]
    createdBy: str
    version: int
    checkFlag: bool
    created_at: datetime = None
    updated_at: datetime = None

    def to_dict(self) -> dict:
        """FlashcardオブジェクトをFirestore用のdictに変換"""
        return {
            'flashcardId': self.flashcardId,
            'wordId': self.wordId,
            'usingMeaningIdList': self.usingMeaningIdList,
            'memo': self.memo,
            'mediaIdList': self.mediaIdList,
            'currentMediaId': self.currentMediaId,
            'comparisonId': self.comparisonId,
            'createdBy': self.createdBy,
            'version': self.version,
            'checkFlag': self.checkFlag,
            'created_at': self.created_at or datetime.now(),
            'updated_at': self.updated_at or datetime.now()
        }

    @staticmethod
    def from_dict(data: dict) -> 'FlashcardSchema':
        """FirestoreのデータからFlashcardオブジェクトを作成"""
        return FlashcardSchema(
            flashcardId=data.get('flashcardId'),
            wordId=data.get('wordId'),
            usingMeaningIdList=data.get('usingMeaningIdList', []),
            memo=data.get('memo'),
            mediaIdList=data.get('mediaIdList', []),
            currentMediaId=data.get('currentMediaId'),
            comparisonId=data.get('comparisonId'),
            createdBy=data.get('createdBy'),
            version=data.get('version'),
            checkFlag=data.get('checkFlag'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        ) 