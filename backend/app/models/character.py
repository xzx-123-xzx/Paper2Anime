from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class CharacterAppearance(BaseModel):
    age_estimate: str
    gender: str
    height: str
    build: str
    hair_style: str
    hair_color: str
    eye_color: str
    skin_tone: str
    clothing_style: str
    distinguishing_features: List[str] = []

class CharacterPersonality(BaseModel):
    temperament: str
    speaking_style: str
    mannerisms: List[str] = []

class Character(BaseModel):
    character_id: str
    project_id: str
    name: str
    role: str  # protagonist, antagonist, supporting, minor
    description: str
    appearance: CharacterAppearance
    personality: Optional[CharacterPersonality] = None
    image_urls: Dict[str, str] = {}  # front, side, back, expression
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
