from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlmodel import SQLModel, Field


class Story(SQLModel, table=True):
    __tablename__ = "stories"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    child_profile_id: uuid.UUID = Field(foreign_key="child_profiles.id", index=True)
    source_content: str
    language_target: str = Field(max_length=20)  # es | en | mixed_es_en
    title: Optional[str] = Field(default=None, max_length=255)
    status: str = Field(max_length=40, index=True)  # pending|scripting|script_ready|approved|generating_images|completed|failed
    error_message: Optional[str] = Field(default=None)
    script_generated_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
