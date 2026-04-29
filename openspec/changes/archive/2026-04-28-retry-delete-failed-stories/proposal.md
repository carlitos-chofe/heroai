## Why

Users currently cannot manage stories that fail during the generation process (either script or image generation). This leads to a cluttered dashboard with stuck "Error" cards and frustration when a generation fails due to a transient issue, as there is no way to retry it without starting the story creation process from scratch.

## What Changes

- Add the ability to delete failed stories from the dashboard and database.
- Add the ability to retry failed stories, picking up from the step where they failed (script generation or image generation).
- Add "Eliminar" (🗑️) and "Reintentar" (🔁) action buttons on the Story Cards in the dashboard when the status is "failed".
- Add equivalent buttons to the story progress page for failed stories.

## Capabilities

### New Capabilities
- `story-retry-delete`: Defines the requirements and behavior for managing (deleting and retrying) failed stories from the user interface down to the backend API and worker queues.

### Modified Capabilities
*(None)*

## Impact

- **Frontend (`apps/web`)**: UI updates on `StoryCard` and `ProgressPage` components to add new action buttons. Add new API client functions for deletion and retry.
- **Backend API (`apps/api`)**: New routes for `DELETE /stories/{story_id}` and `POST /stories/{story_id}/retry`. Business logic updates in `story_service.py` to handle the state transitions and resource cleanup safely.
- **Database**: When deleting a story, cascade deletion or explicit cleanup of associated `StoryPanel` records.
- **Storage**: When deleting a story, cleanup of generated physical assets in the `LOCAL_ASSET_DIR` to avoid orphaned files.
