from datetime import datetime, timezone
from typing import Optional, Any
import uuid
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class ChildProfile(SQLModel, table=True):
    __tablename__ = "child_profiles"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=120)
    age: int
    initial_interests: str
    avatar_config: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )
    preference_summary: dict = Field(
        default_factory=lambda: {"likes": [], "avoid": [], "last_reactions": []},
        sa_column=Column(JSONB, nullable=False, server_default='{}'),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
