import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.auth import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.story import (
    FeedbackCreate,
    FeedbackResponse,
    StoryApproveResponse,
    StoryCreate,
    StoryCreatedResponse,
    StoryDetailResponse,
    StoryListItem,
    StoryScriptResponse,
    StoryStatusResponse,
    PanelResponse,
    ScriptPanelResponse,
)
from app.services.feedback_service import create_feedback
from app.services.story_service import (
    approve_story,
    regenerate_script,
    create_story,
    get_story,
    get_story_panels,
    get_story_script,
    get_story_status,
    list_stories,
    delete_story,
    retry_story,
)
from app.workers.celery_app import celery_app

router = APIRouter(prefix="/stories", tags=["stories"])


@router.post("", response_model=StoryCreatedResponse, status_code=status.HTTP_202_ACCEPTED)
def post_story(
    data: StoryCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    story = create_story(session, user, data)
    # Enqueue script generation
    celery_app.send_task(
        "app.workers.script_worker.generate_story_script",
        kwargs={"story_id": str(story.id)},
    )
    return {"story_id": story.id, "status": story.status}


@router.get("", response_model=list[StoryListItem])
def get_stories(
    profile_id: Optional[uuid.UUID] = Query(default=None),
    story_status: Optional[str] = Query(default=None, alias="status"),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return list_stories(session, user, profile_id, story_status)


@router.get("/{story_id}", response_model=StoryDetailResponse)
def get_story_detail(
    story_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    story = get_story(session, user, story_id)
    panels = get_story_panels(session, story_id)
    return StoryDetailResponse(
        id=story.id,
        child_profile_id=story.child_profile_id,
        title=story.title,
        status=story.status,
        language_target=story.language_target,
        error_message=story.error_message,
        created_at=story.created_at,
        completed_at=story.completed_at,
        panels=[
            PanelResponse(
                panel_order=p.panel_order,
                scene_description=p.scene_description,
                narrative_text=p.narrative_text,
                dialogue=p.dialogue,
                image_url=p.image_url,
            )
            for p in panels
        ],
    )


@router.get("/{story_id}/status", response_model=StoryStatusResponse)
def get_status(
    story_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return get_story_status(session, user, story_id)


@router.get("/{story_id}/script", response_model=StoryScriptResponse)
def get_script(
    story_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    result = get_story_script(session, user, story_id)
    return StoryScriptResponse(
        story_id=result["story_id"],
        title=result["title"],
        language_target=result["language_target"],
        panels=[
            ScriptPanelResponse(
                panel_order=p.panel_order,
                scene_description=p.scene_description,
                narrative_text=p.narrative_text,
                dialogue=p.dialogue,
            )
            for p in result["panels"]
        ],
    )


@router.post("/{story_id}/approve", response_model=StoryApproveResponse, status_code=status.HTTP_202_ACCEPTED)
def approve(
    story_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    story = approve_story(session, user, story_id)
    # Enqueue image generation
    celery_app.send_task(
        "app.workers.image_worker.generate_story_images",
        kwargs={"story_id": str(story.id)},
    )
    return {"story_id": story.id, "status": story.status}


@router.post("/{story_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def post_feedback(
    story_id: uuid.UUID,
    data: FeedbackCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return create_feedback(session, user, story_id, data)


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.post("/{story_id}/regenerate-script", status_code=status.HTTP_202_ACCEPTED)
def regenerate_story_script_route(
    story_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    story = regenerate_script(session, user, story_id)
    celery_app.send_task(
        "app.workers.script_worker.generate_story_script",
        kwargs={"story_id": str(story.id)},
    )
    return {"story_id": story.id, "status": story.status}

@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_story_endpoint(
    story_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    delete_story(session, user, story_id)
    return None

@router.post("/{story_id}/retry", status_code=status.HTTP_202_ACCEPTED)
def retry_failed_story(
    story_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    story = retry_story(session, user, story_id)
    
    if story.status == "pending":
        # Enqueue script generation
        celery_app.send_task(
            "app.workers.script_worker.generate_story_script",
            kwargs={"story_id": str(story.id)},
        )
    elif story.status == "approved":
        # Enqueue image generation
        celery_app.send_task(
            "app.workers.image_worker.generate_story_images",
            kwargs={"story_id": str(story.id)},
        )
        
    return {"story_id": story.id, "status": story.status}
