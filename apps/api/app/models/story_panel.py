from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlmodel import SQLModel, Field


class StoryPanel(SQLModel, table=True):
    __tablename__ = "story_panels"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    story_id: uuid.UUID = Field(foreign_key="stories.id", index=True)
    panel_order: int  # 1-5
    image_prompt: str
    scene_description: str
    narrative_text: str
    dialogue: str
    image_url: Optional[str] = Field(default=None)
    generation_status: str = Field(default="pending", max_length=40)  # pending|generated|failed
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
