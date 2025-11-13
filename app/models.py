from pydantic import BaseModel
from typing import List, Optional

class Fight(BaseModel):
    fight_id: str
    fighter1: str
    fighter2: str
    weight_class: str
    fighter1_record: Optional[str] = None
    fighter2_record: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None

class Card(BaseModel):
    fights: List[Fight]

class FightAnalysis(BaseModel):
    fight_id: str
    pick: str
    confidence: int  # percentage 0-100
    path_to_victory: str
    risk_flags: List[str]
    props: List[str]

class CardAnalysis(BaseModel):
    analyses: List[FightAnalysis]
