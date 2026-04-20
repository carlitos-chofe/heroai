import uuid
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.auth import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.profile_service import (
    create_profile,
    list_profiles,
    update_profile,
)

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("", response_model=list[ProfileResponse])
def get_profiles(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return list_profiles(session, user)


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def post_profile(
    data: ProfileCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return create_profile(session, user, data)


@router.patch("/{profile_id}", response_model=ProfileResponse)
def patch_profile(
    profile_id: uuid.UUID,
    data: ProfileUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return update_profile(session, user, profile_id, data)
