from datetime import datetime, timezone
import uuid
from sqlmodel import SQLModel, Field


class StoryFeedback(SQLModel, table=True):
    __tablename__ = "story_feedback"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    story_id: uuid.UUID = Field(foreign_key="stories.id", index=True)
    child_profile_id: uuid.UUID = Field(foreign_key="child_profiles.id", index=True)
    panel_order: int  # 1-5
    reaction_type: str = Field(max_length=40)  # love|funny|scary
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
