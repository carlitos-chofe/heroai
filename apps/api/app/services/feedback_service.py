from datetime import datetime, timezone
import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.child_profile import ChildProfile
from app.models.story import Story
from app.models.story_feedback import StoryFeedback
from app.models.user import User
from app.schemas.story import FeedbackCreate


def create_feedback(
    session: Session,
    user: User,
    story_id: uuid.UUID,
    data: FeedbackCreate,
) -> StoryFeedback:
    story = session.get(Story, story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "resource_not_found", "message": "Story not found"},
        )

    # Verify ownership
    profile = session.get(ChildProfile, story.child_profile_id)
    if not profile or profile.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "forbidden", "message": "Access denied"},
        )

    if story.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "invalid_state_transition",
                "message": "Feedback can only be registered on completed stories",
            },
        )

    feedback = StoryFeedback(
        story_id=story_id,
        child_profile_id=story.child_profile_id,
        panel_order=data.panel_order,
        reaction_type=data.reaction_type,
        created_at=datetime.now(timezone.utc),
    )
    session.add(feedback)
    session.commit()
    session.refresh(feedback)

    # Recalculate preference_summary for the profile
    _recalculate_preference_summary(session, profile)

    return feedback


def _recalculate_preference_summary(
    session: Session, profile: ChildProfile
) -> None:
    """
    Simple heuristic:
    - likes: reaction_types 'love' or 'funny' → positivo
    - avoid: reaction_type 'scary' → negativo
    - last_reactions: last 10 reactions
    """
    all_feedback = list(
        session.exec(
            select(StoryFeedback)
            .where(StoryFeedback.child_profile_id == profile.id)
            .order_by(StoryFeedback.created_at.desc())
        ).all()
    )

    loves = sum(1 for f in all_feedback if f.reaction_type in ("love", "funny"))
    scary = sum(1 for f in all_feedback if f.reaction_type == "scary")

    likes: list[str] = []
    avoid: list[str] = []

    if loves > 0:
        likes = ["fun adventures", "friendly characters"]
    if scary > 2:
        avoid = ["scary scenes", "dark themes"]

    last_reactions = [
        {"panel_order": f.panel_order, "reaction_type": f.reaction_type}
        for f in all_feedback[:10]
    ]

    profile.preference_summary = {
        "likes": likes,
        "avoid": avoid,
        "last_reactions": last_reactions,
    }
    profile.updated_at = datetime.now(timezone.utc)
    session.add(profile)
    session.commit()
