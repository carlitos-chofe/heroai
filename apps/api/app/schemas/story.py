from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, field_validator


VALID_LANGUAGE_TARGETS = {"es", "en", "mixed_es_en"}
VALID_STATUSES = {
    "pending", "scripting", "script_ready",
    "approved", "generating_images", "completed", "failed",
}
VALID_REACTIONS = {"love", "funny", "scary"}
SCRIPT_READABLE_STATUSES = {"script_ready", "approved", "generating_images", "completed"}


class StoryCreate(BaseModel):
    profile_id: uuid.UUID
    content: str
    language_target: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if len(v) < 200:
            raise ValueError("Content must be at least 200 characters")
        if len(v) > 20000:
            raise ValueError("Content must not exceed 20000 characters")
        return v

    @field_validator("language_target")
    @classmethod
    def validate_language(cls, v: str) -> str:
        if v not in VALID_LANGUAGE_TARGETS:
            raise ValueError(f"language_target must be one of {VALID_LANGUAGE_TARGETS}")
        return v


class StoryCreatedResponse(BaseModel):
    story_id: uuid.UUID
    status: str


class StoryListItem(BaseModel):
    id: uuid.UUID
    child_profile_id: uuid.UUID
    title: Optional[str]
    status: str
    language_target: str
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PanelResponse(BaseModel):
    panel_order: int
    scene_description: str
    narrative_text: str
    dialogue: str
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}


class StoryDetailResponse(BaseModel):
    id: uuid.UUID
    child_profile_id: uuid.UUID
    title: Optional[str]
    status: str
    language_target: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    panels: list[PanelResponse] = []

    model_config = {"from_attributes": True}


class StoryStatusResponse(BaseModel):
    story_id: uuid.UUID
    status: str
    generated_panels: int
    total_panels: int
    error_message: Optional[str]


class ScriptPanelResponse(BaseModel):
    panel_order: int
    scene_description: str
    narrative_text: str
    dialogue: str

    model_config = {"from_attributes": True}


class StoryScriptResponse(BaseModel):
    story_id: uuid.UUID
    title: Optional[str]
    language_target: str
    panels: list[ScriptPanelResponse]


class StoryApproveResponse(BaseModel):
    story_id: uuid.UUID
    status: str


class FeedbackCreate(BaseModel):
    panel_order: int
    reaction_type: str

    @field_validator("panel_order")
    @classmethod
    def validate_panel(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("panel_order must be between 1 and 5")
        return v

    @field_validator("reaction_type")
    @classmethod
    def validate_reaction(cls, v: str) -> str:
        if v not in VALID_REACTIONS:
            raise ValueError(f"reaction_type must be one of {VALID_REACTIONS}")
        return v


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    story_id: uuid.UUID
    child_profile_id: uuid.UUID
    panel_order: int
    reaction_type: str
    created_at: datetime

    model_config = {"from_attributes": True}
