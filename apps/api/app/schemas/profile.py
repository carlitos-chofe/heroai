from datetime import datetime
from typing import Optional, Any
import uuid
from pydantic import BaseModel, field_validator


class AvatarConfig(BaseModel):
    hair: str
    hair_color: str
    eye_color: str
    skin: str
    clothing: str


class PreferenceSummary(BaseModel):
    likes: list[str] = []
    avoid: list[str] = []
    last_reactions: list[dict] = []


class ProfileCreate(BaseModel):
    name: str
    age: int
    initial_interests: str
    avatar_config: AvatarConfig

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 4 or v > 12:
            raise ValueError("Age must be between 4 and 12")
        return v


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    initial_interests: Optional[str] = None
    avatar_config: Optional[AvatarConfig] = None

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 4 or v > 12):
            raise ValueError("Age must be between 4 and 12")
        return v


class ProfileResponse(BaseModel):
    id: uuid.UUID
    name: str
    age: int
    initial_interests: str
    avatar_config: dict
    preference_summary: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
