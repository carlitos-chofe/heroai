## Context

The `hero-ai` application currently allows users to create stories, which triggers background tasks (Celery workers) to generate scripts and images via Google Gemini APIs. Sometimes, these tasks fail due to transient errors, API limits, or content filtering. When a task fails, the story's status is set to `failed`, and the user is left with a stuck story in their dashboard. There is currently no way to remove or retry these failed stories.

## Goals / Non-Goals

**Goals:**
- Provide a clear UI for users to delete failed stories.
- Provide a clear UI for users to retry failed stories without re-entering their initial prompt.
- Ensure backend operations handle database, panel, and filesystem cleanup properly when deleting.
- Intelligently resume the background generation tasks from where they left off (e.g. if the script was approved but image generation failed, do not regenerate the script).

**Non-Goals:**
- Automatically retrying stories that fail (beyond the existing Celery retries). This design relies on manual user intervention to retry.
- Providing granular retry at the individual panel level. Retries will restart the entire phase (script generation or image generation) that failed.

## Decisions

**1. Re-using Existing Task Queues for Retries**
- **Decision:** The retry endpoint will determine the point of failure by checking the story's `script_generated_at` timestamp or current state logic. If the script was never generated/approved, we enqueue `generate_story_script`. If the script was generated and approved, we enqueue `generate_story_images`.
- **Rationale:** This prevents wasting tokens and time regenerating a script that the user already reviewed and approved.

**2. Hard Deletion of Assets**
- **Decision:** The delete endpoint will physically delete the associated images from the filesystem (`LOCAL_ASSET_DIR / stories / {story_id}`) using Python's `shutil` or `pathlib`.
- **Rationale:** Prevents the local Docker volume from filling up with orphaned images from deleted stories.

**3. Frontend UI Placement**
- **Decision:** Place the "Eliminar" and "Reintentar" buttons directly on the `StoryCard` component when the status is `failed`. Also, add them to the `ProgressPage` since users are redirected there when clicking a failed story.
- **Rationale:** Makes it immediately obvious to the user what actions they can take to resolve the error.

## Risks / Trade-offs

- **Risk:** User retries a story multiple times causing a buildup of background tasks if the API is consistently failing (e.g. due to policy violations).
  - *Mitigation:* The backend will clear the error message and set the status to `pending` or `approved` immediately upon retry, preventing multiple clicks. We can also disable the button on the frontend during the request.
- **Risk:** Deleting physical files fails due to permission issues.
  - *Mitigation:* Wrap the file deletion in a `try...except` block and log the error, but still allow the database record to be deleted so the user isn't stuck.