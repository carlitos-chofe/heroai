## 1. Backend Service Layer Updates

- [x] 1.1 Implement `delete_story(session, user, story_id)` in `app/services/story_service.py` to delete panels, database record, and physical files.
- [x] 1.2 Implement `retry_story(session, user, story_id)` in `app/services/story_service.py` to reset the story status to `pending` or `approved` based on the previous generation phase.

## 2. Backend API Routes

- [x] 2.1 Add `DELETE /stories/{story_id}` endpoint to `app/api/routes/stories.py` that delegates to `delete_story`.
- [x] 2.2 Add `POST /stories/{story_id}/retry` endpoint to `app/api/routes/stories.py` that delegates to `retry_story` and enqueues the appropriate Celery task.

## 3. Frontend API Client Updates

- [x] 3.1 Add `deleteStory(token, storyId)` function in `apps/web/lib/api.ts` to call the new DELETE endpoint.
- [x] 3.2 Add `retryStory(token, storyId)` function in `apps/web/lib/api.ts` to call the new POST retry endpoint.

## 4. Frontend Component Updates

- [x] 4.1 Update `StoryCard.tsx` component to include "Eliminar" and "Reintentar" action buttons when `story.status` is `failed`.
- [x] 4.2 Update `StoryCard.tsx` to handle the onClick events for these new buttons using `e.preventDefault()`, invoking the API client, and notifying the parent to refresh the list.
- [x] 4.3 Update `DashboardPage` in `apps/web/app/dashboard/page.tsx` to pass a refresh callback to `StoryCard` or handle state update locally when a story is deleted/retried.
- [x] 4.4 Add equivalent action buttons to the `ProgressPage` in `apps/web/app/stories/[storyId]/progress/page.tsx` for when a story is in the `failed` state.