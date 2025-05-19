from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class MeaningSchema:
    meaning_id: str
    pos: str  
    definition: str
    pronunciation: str
    example_eng: str 
    example_jpn: str 
    rank: int
    created_at: datetime
    updated_at: datetime
