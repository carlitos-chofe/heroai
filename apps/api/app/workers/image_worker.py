"""
Celery task: generate_story_images
Generates one image per panel using Gemini Flash Image,
saves to local disk, and updates the database.
"""
import io
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types
from celery import Task
from sqlmodel import Session, select
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import get_settings
from app.db.session import engine
from app.models.story import Story
from app.models.story_panel import StoryPanel
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=30),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _generate_image_bytes(prompt: str) -> bytes:
    """Call Gemini image model and return PNG bytes."""
    client = genai.Client(
        vertexai=True,
        project=settings.gcp_project_id,
        location=settings.gcp_location,
    )
    
    # Use generate_content for gemini multimodal models that output images
    response = client.models.generate_content(
        model=settings.google_image_model,
        contents=[prompt],
        config=types.GenerateContentConfig(
            temperature=1,
            response_modalities=["IMAGE"],
        ),
    )
    
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                return part.inline_data.data
                
    raise ValueError("No image was returned by the model")


def _save_image(story_id: str, panel_order: int, image_bytes: bytes) -> str:
    """
    Save image bytes to disk.
    Returns the public relative URL: /assets/stories/{story_id}/panel-{n}.png
    """
    base_dir = Path(settings.local_asset_dir)
    story_dir = base_dir / "stories" / story_id
    story_dir.mkdir(parents=True, exist_ok=True)

    filename = f"panel-{panel_order}.png"
    file_path = story_dir / filename

    with open(file_path, "wb") as f:
        f.write(image_bytes)

    return f"/assets/stories/{story_id}/{filename}"


@celery_app.task(name="app.workers.image_worker.generate_story_images", bind=True, max_retries=3)
def generate_story_images(self: Task, story_id: str) -> dict:
    logger.info(f"[image_worker] Starting for story_id={story_id}")

    with Session(engine) as session:
        story = session.get(Story, story_id)
        if not story:
            logger.error(f"[image_worker] Story {story_id} not found")
            return {"error": "story_not_found"}

        if story.status != "approved":
            logger.error(f"[image_worker] Story {story_id} not in 'approved' status (got '{story.status}')")
            return {"error": f"invalid_status: {story.status}"}

        # Transition to generating_images
        story.status = "generating_images"
        story.updated_at = datetime.now(timezone.utc)
        session.add(story)
        session.commit()

        panels = list(
            session.exec(
                select(StoryPanel)
                .where(StoryPanel.story_id == story.id)
                .order_by(StoryPanel.panel_order)
            ).all()
        )

        if len(panels) != 5:
            _mark_failed(session, story, f"Expected 5 panels, found {len(panels)}")
            return {"error": "wrong_panel_count"}

        failed_panels = []

        for panel in panels:
            try:
                logger.info(f"[image_worker] Generating image for story {story_id}, panel {panel.panel_order}")
                image_bytes = _generate_image_bytes(panel.image_prompt)
                image_url = _save_image(story_id, panel.panel_order, image_bytes)

                panel.image_url = image_url
                panel.generation_status = "generated"
                panel.updated_at = datetime.now(timezone.utc)
                session.add(panel)
                session.commit()

                logger.info(f"[image_worker] Panel {panel.panel_order} saved to {image_url}")

            except Exception as e:
                logger.exception(f"[image_worker] Failed panel {panel.panel_order} for story {story_id}: {e}")
                panel.generation_status = "failed"
                panel.updated_at = datetime.now(timezone.utc)
                session.add(panel)
                session.commit()
                failed_panels.append(panel.panel_order)

        # Refresh story before updating status
        session.refresh(story)

        if failed_panels:
            error_msg = f"Image generation failed for panels: {failed_panels}"
            _mark_failed(session, story, error_msg)
            logger.error(f"[image_worker] {error_msg} for story {story_id}")
            return {"error": error_msg}

        story.status = "completed"
        story.completed_at = datetime.now(timezone.utc)
        story.updated_at = datetime.now(timezone.utc)
        session.add(story)
        session.commit()

        logger.info(f"[image_worker] Story {story_id} → completed")
        return {"story_id": story_id, "status": "completed"}


def _mark_failed(session: Session, story: Story, message: str) -> None:
    story.status = "failed"
    story.error_message = message
    story.updated_at = datetime.now(timezone.utc)
    session.add(story)
    session.commit()
