import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.config import get_settings
from app.models.child_profile import ChildProfile
from app.models.story import Story
from app.models.story_panel import StoryPanel
from app.models.story_feedback import StoryFeedback
from app.models.user import User
from app.schemas.story import (
    StoryCreate,
    SCRIPT_READABLE_STATUSES,
)


def _assert_story_ownership(story: Story, user: User, session: Session) -> None:
    profile = session.get(ChildProfile, story.child_profile_id)
    if not profile or profile.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "forbidden", "message": "Access denied"},
        )


def create_story(
    session: Session,
    user: User,
    data: StoryCreate,
) -> Story:
    # Verify profile ownership
    profile = session.get(ChildProfile, data.profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "resource_not_found", "message": "Profile not found"},
        )
    if profile.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "forbidden", "message": "Access denied"},
        )

    story = Story(
        child_profile_id=data.profile_id,
        source_content=data.content,
        language_target=data.language_target,
        status="pending",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session.add(story)
    session.commit()
    session.refresh(story)
    return story


def list_stories(
    session: Session,
    user: User,
    profile_id: Optional[uuid.UUID] = None,
    story_status: Optional[str] = None,
) -> list[Story]:
    # Get all profile IDs belonging to this user
    profiles = session.exec(
        select(ChildProfile).where(ChildProfile.user_id == user.id)
    ).all()
    profile_ids = {p.id for p in profiles}

    query = select(Story).where(Story.child_profile_id.in_(profile_ids))
    if profile_id:
        query = query.where(Story.child_profile_id == profile_id)
    if story_status:
        query = query.where(Story.status == story_status)

    return list(session.exec(query.order_by(Story.created_at.desc())).all())


def get_story(session: Session, user: User, story_id: uuid.UUID) -> Story:
    story = session.get(Story, story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "resource_not_found", "message": "Story not found"},
        )
    _assert_story_ownership(story, user, session)
    return story


def get_story_panels(session: Session, story_id: uuid.UUID) -> list[StoryPanel]:
    return list(
        session.exec(
            select(StoryPanel)
            .where(StoryPanel.story_id == story_id)
            .order_by(StoryPanel.panel_order)
        ).all()
    )


def get_story_status(
    session: Session, user: User, story_id: uuid.UUID
) -> dict:
    story = get_story(session, user, story_id)
    panels = get_story_panels(session, story_id)
    generated = sum(1 for p in panels if p.generation_status == "generated")
    return {
        "story_id": story.id,
        "status": story.status,
        "generated_panels": generated,
        "total_panels": 5,
        "error_message": story.error_message,
    }


def get_story_script(session: Session, user: User, story_id: uuid.UUID) -> dict:
    story = get_story(session, user, story_id)
    if story.status not in SCRIPT_READABLE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "invalid_state_transition",
                "message": f"Script not available in status '{story.status}'",
            },
        )
    panels = get_story_panels(session, story_id)
    return {
        "story_id": story.id,
        "title": story.title,
        "language_target": story.language_target,
        "panels": panels,
    }


def approve_story(session: Session, user: User, story_id: uuid.UUID) -> Story:
    story = get_story(session, user, story_id)
    if story.status != "script_ready":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "invalid_state_transition",
                "message": f"Cannot approve story in status '{story.status}'",
            },
        )
    story.status = "approved"
    story.updated_at = datetime.now(timezone.utc)
    session.add(story)
    session.commit()
    session.refresh(story)
    return story


def delete_story(session: Session, user: User, story_id: uuid.UUID) -> None:
    story = get_story(session, user, story_id)
    
    # 0. Delete feedback (if any)
    feedback_entries = session.exec(
        select(StoryFeedback).where(StoryFeedback.story_id == story_id)
    ).all()
    for feedback in feedback_entries:
        session.delete(feedback)

    # 1. Delete panels
    panels = get_story_panels(session, story_id)
    for panel in panels:
        session.delete(panel)

    # 2. Delete story record
    session.delete(story)
    session.commit()

    # 3. Delete physical files if they exist
    settings = get_settings()
    base_dir = Path(settings.local_asset_dir)
    story_dir = base_dir / "stories" / str(story.id)
    
    if story_dir.exists() and story_dir.is_dir():
        try:
            shutil.rmtree(story_dir)
        except Exception as e:
            # We log it, but don't fail the API request since DB records are already gone
            print(f"Error deleting physical files for story {story.id}: {e}")

def regenerate_script(session: Session, user: User, story_id: uuid.UUID) -> Story:
    story = get_story(session, user, story_id)
    if story.status != "script_ready":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "invalid_state_transition",
                "message": f"Cannot regenerate script for story in status '{story.status}'",
            },
        )
    
    # Delete existing panels
    panels = get_story_panels(session, story_id)
    for panel in panels:
        session.delete(panel)
        
    story.status = "pending"
    story.script_generated_at = None
    story.error_message = None
    
    session.add(story)
    session.commit()
    session.refresh(story)
    return story

def retry_story(session: Session, user: User, story_id: uuid.UUID) -> Story:
    story = get_story(session, user, story_id)
    
    if story.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "invalid_state_transition", "message": f"Can only retry failed stories. Current status: '{story.status}'"}
        )
    
    # Determine the phase where it failed.
    # If script_generated_at is not set, it failed during script generation.
    if not story.script_generated_at:
        # Reset to pending to start over
        story.status = "pending"
        # Cleanup any orphan panels that might have been created
        panels = get_story_panels(session, story_id)
        for panel in panels:
            session.delete(panel)
    else:
        # Script was generated, so it failed during image generation
        story.status = "approved"
        # Reset generation_status of failed panels to pending
        panels = get_story_panels(session, story_id)
        for panel in panels:
            if panel.generation_status == "failed":
                panel.generation_status = "pending"
                session.add(panel)
    
    story.error_message = None
    story.updated_at = datetime.now(timezone.utc)
    session.add(story)
    session.commit()
    session.refresh(story)
    return story
