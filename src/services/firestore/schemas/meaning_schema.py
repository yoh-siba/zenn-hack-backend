from dataclasses import dataclass
from datetime import datetime
from src.models.enums import PartOfSpeech



@dataclass
class MeaningSchema:
    pos: PartOfSpeech
    definition: str
    pronunciation: str
    example_eng: str 
    example_jpn: str 
    rank: int
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict:
        """MeaningオブジェクトをFirestore用のdictに変換"""
        return {
            'pos': self.pos.value,
            'definition': self.definition,
            'pronunciation': self.pronunciation,
            'example_eng': self.example_eng,
            'example_jpn': self.example_jpn,
            'rank': self.rank,
            'created_at': self.created_at or datetime.now(),
            'updated_at': self.updated_at or datetime.now()
        }

    @staticmethod
    def from_dict(data: dict) -> 'MeaningSchema':
        """Firestoreのデータからmeaningオブジェクトを作成"""
        pos_value = data.get('pos')
        pos = PartOfSpeech(pos_value) if pos_value else None
        
        return MeaningSchema(
            pos=pos,
            definition=data.get('definition'),
            pronunciation=data.get('pronunciation'),
            example_eng=data.get('example_eng'),
            example_jpn=data.get('example_jpn'),
            rank=data.get('rank'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
