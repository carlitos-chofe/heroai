from datetime import datetime, timezone
from typing import Optional
import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.child_profile import ChildProfile
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate


def list_profiles(session: Session, user: User) -> list[ChildProfile]:
    return list(
        session.exec(
            select(ChildProfile).where(ChildProfile.user_id == user.id)
        ).all()
    )


def create_profile(
    session: Session, user: User, data: ProfileCreate
) -> ChildProfile:
    profile = ChildProfile(
        user_id=user.id,
        name=data.name,
        age=data.age,
        initial_interests=data.initial_interests,
        avatar_config=data.avatar_config.model_dump(),
        preference_summary={"likes": [], "avoid": [], "last_reactions": []},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def update_profile(
    session: Session,
    user: User,
    profile_id: uuid.UUID,
    data: ProfileUpdate,
) -> ChildProfile:
    profile = session.get(ChildProfile, profile_id)
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

    if data.name is not None:
        profile.name = data.name
    if data.age is not None:
        profile.age = data.age
    if data.initial_interests is not None:
        profile.initial_interests = data.initial_interests
    if data.avatar_config is not None:
        profile.avatar_config = data.avatar_config.model_dump()

    profile.updated_at = datetime.now(timezone.utc)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def get_profile_for_user(
    session: Session, user: User, profile_id: uuid.UUID
) -> ChildProfile:
    profile = session.get(ChildProfile, profile_id)
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
    return profile
