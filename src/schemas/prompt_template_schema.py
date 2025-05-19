from dataclasses import dataclass
from datetime import datetime

@dataclass
class PromptTemplateSchema:
    templateId: str
    name: str
    description: str
    generationType: str
    promptText: str
    created_at: datetime = None
    updated_at: datetime = None

    def to_dict(self) -> dict:
        """PromptTemplateオブジェクトをFirestore用のdictに変換"""
        return {
            'templateId': self.templateId,
            'name': self.name,
            'description': self.description,
            'generationType': self.generationType,
            'promptText': self.promptText,
            'created_at': self.created_at or datetime.now(),
            'updated_at': self.updated_at or datetime.now()
        }

    @staticmethod
    def from_dict(data: dict) -> 'PromptTemplateSchema':
        """FirestoreのデータからPromptTemplateオブジェクトを作成"""
        return PromptTemplateSchema(
            templateId=data.get('templateId'),
            name=data.get('name'),
            description=data.get('description'),
            generationType=data.get('generationType'),
            promptText=data.get('promptText'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        ) 