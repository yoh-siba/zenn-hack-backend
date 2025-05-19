from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class MediaSchema:
    mediaId: str
    flashcardId: str
    meaningId: str
    mediaUrls: List[str]
    generationType: str
    templateId: Optional[str]
    userPrompt: str
    generatedPrompt: str
    inputMediaUrls: Optional[List[str]]
    promptTokens: int
    completionTokens: int
    totalTokens: int
    createdBy: str
    created_at: datetime = None
    updated_at: datetime = None

    def to_dict(self) -> dict:
        """MediaオブジェクトをFirestore用のdictに変換"""
        return {
            'mediaId': self.mediaId,
            'flashcardId': self.flashcardId,
            'meaningId': self.meaningId,
            'mediaUrls': self.mediaUrls,
            'generationType': self.generationType,
            'templateId': self.templateId,
            'userPrompt': self.userPrompt,
            'generatedPrompt': self.generatedPrompt,
            'inputMediaUrls': self.inputMediaUrls,
            'promptTokens': self.promptTokens,
            'completionTokens': self.completionTokens,
            'totalTokens': self.totalTokens,
            'createdBy': self.createdBy,
            'created_at': self.created_at or datetime.now(),
            'updated_at': self.updated_at or datetime.now()
        }

    @staticmethod
    def from_dict(data: dict) -> 'MediaSchema':
        """FirestoreのデータからMediaオブジェクトを作成"""
        return MediaSchema(
            mediaId=data.get('mediaId'),
            flashcardId=data.get('flashcardId'),
            meaningId=data.get('meaningId'),
            mediaUrls=data.get('mediaUrls', []),
            generationType=data.get('generationType'),
            templateId=data.get('templateId'),
            userPrompt=data.get('userPrompt'),
            generatedPrompt=data.get('generatedPrompt'),
            inputMediaUrls=data.get('inputMediaUrls'),
            promptTokens=data.get('promptTokens'),
            completionTokens=data.get('completionTokens'),
            totalTokens=data.get('totalTokens'),
            createdBy=data.get('createdBy'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        ) 