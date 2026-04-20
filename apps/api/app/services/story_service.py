from datetime import datetime, timezone
from typing import Optional
import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.child_profile import ChildProfile
from app.models.story import Story
from app.models.story_panel import StoryPanel
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
