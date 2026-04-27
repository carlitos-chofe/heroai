"""
Celery task: generate_story_script
Generates the 5-panel story script using Gemini 2.5 Pro,
applies linguistic validation, and persists the result.
"""
import json
import logging
import re
from datetime import datetime, timezone

from google import genai
from celery import Task
from sqlmodel import Session, select
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import get_settings
from app.db.session import engine
from app.models.child_profile import ChildProfile
from app.models.story import Story
from app.models.story_panel import StoryPanel
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


def _age_rules(age: int) -> str:
    if 4 <= age <= 6:
        return (
            "- Short, direct sentences (max 12 words each).\n"
            "- Dialogues: max 8 words per line.\n"
            "- Avoid complex subordinate clauses, irony, sarcasm, or ambiguity.\n"
        )
    elif 7 <= age <= 9:
        return (
            "- Clear narration with basic vocabulary (max 18 words per sentence).\n"
            "- Dialogues: max 12 words per line.\n"
            "- Simple cause-and-effect explanations are allowed.\n"
        )
    else:  # 10-12
        return (
            "- Clear narration with slightly richer vocabulary (max 25 words per sentence).\n"
            "- Dialogues: max 18 words per line.\n"
            "- Brief conceptual explanations with some detail are allowed.\n"
        )


def _language_rules(language_target: str) -> str:
    if language_target == "es":
        return "- Write ALL text in Spanish. Do not use English except for unavoidable proper nouns.\n"
    elif language_target == "en":
        return "- Write ALL text in English. Do not use Spanish except for unavoidable proper nouns.\n"
    else:  # mixed_es_en
        return (
            "- Write narration mainly in Spanish.\n"
            "- Dialogues may naturally mix in simple English words or phrases for pedagogical effect.\n"
            "- Do not use confusing Spanglish or incorrect grammar structures.\n"
        )


def _build_script_prompt(
    story: Story,
    profile: ChildProfile,
) -> str:
    pref = profile.preference_summary or {}
    likes = pref.get("likes", [])
    avoid = pref.get("avoid", [])

    pref_section = ""
    if likes:
        pref_section += f"- This child enjoys: {', '.join(likes)}\n"
    if avoid:
        pref_section += f"- Avoid these themes: {', '.join(avoid)}\n"

    return f"""You are an expert children's story writer creating an educational comic script.

CHILD PROFILE:
- Name: {profile.name}
- Age: {profile.age} years old
- Interests: {profile.initial_interests}
- Avatar: {json.dumps(profile.avatar_config)}
{pref_section}

STORY LANGUAGE: {story.language_target}

LANGUAGE RULES:
{_language_rules(story.language_target)}
AGE-APPROPRIATE WRITING RULES:
{_age_rules(profile.age)}
GENERAL RULES:
- No spelling mistakes. No grammar errors. Consistent punctuation.
- No aggressive slang or confusing expressions.
- Maintain a positive, safe tone for children.
- The protagonist must be named exactly: {profile.name}
- The story must be educational and based on the source content below.
- Exactly 5 panels, forming a coherent story arc.
- Each panel needs: a visual scene description (for the illustrator), narrative text, and dialogue.
- The image_prompt field must describe ONLY the visual scene. NO TEXT, NO LETTERING, NO SPEECH BUBBLES, NO CAPTIONS in the image.

SOURCE EDUCATIONAL CONTENT:
{story.source_content}

OUTPUT FORMAT (strict JSON, no markdown, no extra text):
{{
  "suggested_title": "string",
  "panels": [
    {{
      "page_number": 1,
      "description": "Visual scene description for the illustrator (no text in image)",
      "narrative": "Narrative text shown to the reader (not in the image)",
      "dialogue": "Dialogue shown to the reader (not in the image)"
    }}
  ]
}}

Produce exactly 5 panels. Return only the JSON object."""


def _build_validation_prompt(
    script_json: dict,
    language_target: str,
    age: int,
) -> str:
    return f"""You are a linguistic quality checker for children's educational content.

Review the following story script and fix any issues:
1. Verify all text matches language_target: "{language_target}"
2. Fix any spelling or punctuation errors
3. Ensure age-appropriateness for a {age}-year-old child
4. Check there are no educational contradictions between panels
5. Ensure consistent grammar throughout

Return the CORRECTED script in the EXACT same JSON format. If no fixes needed, return the original.
Return ONLY the JSON object, no markdown, no extra text.

SCRIPT TO REVIEW:
{json.dumps(script_json, ensure_ascii=False, indent=2)}"""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _call_gemini_text(prompt: str) -> str:
    client = genai.Client(
        vertexai=True,
        project=settings.gcp_project_id,
        location=settings.gcp_location,
    )
    response = client.models.generate_content(
        model=settings.google_text_model,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=4096,
        ),
    )
    return response.text


def _parse_script_json(raw: str) -> dict:
    """Extract and parse JSON from model response."""
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model returned invalid JSON: {e}\nRaw: {raw[:500]}")


def _validate_script(data: dict) -> None:
    if "panels" not in data or len(data["panels"]) != 5:
        raise ValueError(f"Expected exactly 5 panels, got {len(data.get('panels', []))}")
    required_fields = {"page_number", "description", "narrative", "dialogue"}
    for i, panel in enumerate(data["panels"], 1):
        missing = required_fields - set(panel.keys())
        if missing:
            raise ValueError(f"Panel {i} missing fields: {missing}")


@celery_app.task(name="app.workers.script_worker.generate_story_script", bind=True, max_retries=3)
def generate_story_script(self: Task, story_id: str) -> dict:
    logger.info(f"[script_worker] Starting for story_id={story_id}")

    with Session(engine) as session:
        story = session.get(Story, story_id)
        if not story:
            logger.error(f"[script_worker] Story {story_id} not found")
            return {"error": "story_not_found"}

        profile = session.get(ChildProfile, story.child_profile_id)
        if not profile:
            logger.error(f"[script_worker] Profile not found for story {story_id}")
            _mark_failed(session, story, "Child profile not found")
            return {"error": "profile_not_found"}

        # Transition to scripting
        story.status = "scripting"
        story.updated_at = datetime.now(timezone.utc)
        session.add(story)
        session.commit()

        try:
            # Step 1: Generate script
            logger.info(f"[script_worker] Calling Gemini text model for story {story_id}")
            prompt = _build_script_prompt(story, profile)
            raw_response = _call_gemini_text(prompt)
            script_data = _parse_script_json(raw_response)
            _validate_script(script_data)

            # Step 2: Linguistic validation pass
            logger.info(f"[script_worker] Running linguistic validation for story {story_id}")
            validation_attempts = 0
            max_validation_attempts = 2

            while validation_attempts <= max_validation_attempts:
                try:
                    val_prompt = _build_validation_prompt(
                        script_data, story.language_target, profile.age
                    )
                    val_response = _call_gemini_text(val_prompt)
                    validated_data = _parse_script_json(val_response)
                    _validate_script(validated_data)
                    script_data = validated_data
                    break
                except Exception as e:
                    validation_attempts += 1
                    logger.warning(f"[script_worker] Validation attempt {validation_attempts} failed: {e}")
                    if validation_attempts > max_validation_attempts:
                        logger.warning("[script_worker] Validation failed, using original script")
                        break

            # Step 3: Persist panels
            title = script_data.get("suggested_title", "Mi Historia")

            for panel_data in script_data["panels"]:
                page_num = panel_data["page_number"]
                # Build image prompt (no text instruction)
                image_prompt = (
                    f"Children's book illustration. "
                    f"Style: professional, colorful, child-friendly. "
                    f"Character: {profile.name}, {profile.age} years old, "
                    f"{profile.avatar_config.get('hair', '')} {profile.avatar_config.get('hair_color', '')} hair, "
                    f"{profile.avatar_config.get('eye_color', '')} eyes, "
                    f"{profile.avatar_config.get('skin', '')} skin tone, "
                    f"wearing {profile.avatar_config.get('clothing', '')}. "
                    f"Scene: {panel_data['description']}. "
                    f"NO TEXT. NO LETTERING. NO SPEECH BUBBLES. NO CAPTIONS. NO WORDS IN IMAGE."
                )

                panel = StoryPanel(
                    story_id=story.id,
                    panel_order=page_num,
                    image_prompt=image_prompt,
                    scene_description=panel_data["description"],
                    narrative_text=panel_data["narrative"],
                    dialogue=json.dumps(panel_data["dialogue"], ensure_ascii=False) if isinstance(panel_data["dialogue"], (dict, list)) else str(panel_data["dialogue"]),
                    generation_status="pending",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                session.add(panel)

            story.title = title
            story.status = "script_ready"
            story.script_generated_at = datetime.now(timezone.utc)
            story.updated_at = datetime.now(timezone.utc)
            session.add(story)
            session.commit()

            logger.info(f"[script_worker] Completed story {story_id} → script_ready")
            return {"story_id": story_id, "status": "script_ready"}

        except Exception as e:
            logger.exception(f"[script_worker] Failed for story {story_id}: {e}")
            session.refresh(story)
            _mark_failed(session, story, str(e))
            return {"error": str(e)}


def _mark_failed(session: Session, story: Story, message: str) -> None:
    story.status = "failed"
    story.error_message = message
    story.updated_at = datetime.now(timezone.utc)
    session.add(story)
    session.commit()
