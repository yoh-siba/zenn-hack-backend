from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class MeaningSchema:
    meaningId: str
    pos: str  
    definition: str
    pronunciation: str
    example_eng: str 
    example_jpn: str 
    rank: int
    created_at: datetime
    updated_at: datetime

@dataclass
class WordSchema:
    wordId: str 
    word: str  
    meaning_list: List[MeaningSchema]  
    core_meaning: str
    explanation: str
    created_at: datetime = None 
    updated_at: datetime = None 

    def to_dict(self) -> dict:
        """WordオブジェクトをFirestore用のdictに変換"""
        return {
            'wordId': self.wordId,
            'word': self.word,
            'meaning_list': [
                {
                    'meaningId': m.meaningId,
                    'pos': m.pos,
                    'definition': m.definition,
                    'pronunciation': m.pronunciation,
                    'example_eng': m.example_eng,
                    'example_jpn': m.example_jpn,
                    'rank': m.rank,
                    'created_at': m.created_at,
                    'updated_at': m.updated_at
                } for m in self.meaning_list
            ],
            'core_meaning': self.core_meaning,
            'explanation': self.explanation,
            'created_at': self.created_at or datetime.now(),
            'updated_at': self.updated_at or datetime.now()
        }

    @staticmethod
    def from_dict(data: dict) -> 'WordSchema':
        """Firestoreのデータからwordオブジェクトを作成"""
        meanings = [
            MeaningSchema(
                meaningId=m['meaningId'],
                pos=m['pos'],
                definition=m['definition'],
                pronunciation=m['pronunciation'],
                example_eng=m['example_eng'],
                example_jpn=m['example_jpn'],
                rank=m['rank'],
                created_at=m['created_at'],
                updated_at=m['updated_at']
            ) for m in data.get('meaning_list', [])
        ]
        
        return WordSchema(
            wordId=data.get('wordId'),
            word=data.get('word'),
            meaning_list=meanings,
            core_meaning=data.get('core_meaning'),
            explanation=data.get('explanation'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        ) 