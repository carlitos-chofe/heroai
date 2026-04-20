# AGENTS.md - Hero Adventure AI

## Project State
- **Current Status**: MVP implemented. Full codebase exists in `apps/`. First build session completed on 2026-04-20.
- **Primary Source of Truth**: `specs-mvp.md` (Technical Specification for MVP).
- **Session Log**: `02-first-build-session.md` — detailed record of what was built, decisions made, and pending improvements.

## Implemented Architecture
Monorepo structure — fully implemented:
- `apps/web/`: Next.js 15.3.1 (App Router), TypeScript, Clerk, CSS Modules.
- `apps/api/`: FastAPI, SQLModel, Alembic, Pydantic v2, Celery workers.
- `apps/api/app/workers/`: `script_worker.py` (Gemini 2.5 Pro) + `image_worker.py` (Gemini Flash Image).
- `storage/stories/`: Local filesystem for generated panel images (Docker volume `story_assets`).

## Tech Stack & Infrastructure
- **Database**: PostgreSQL 16 (Docker service `hero-postgres`).
- **Broker/Cache**: Redis 7 (Docker service `hero-redis`).
- **Auth**: Clerk — JWT decode via `pyjwt`, lazy user provisioning on first request.
- **AI Models**:
  - Text/Scripting: `gemini-2.5-pro` (env: `GOOGLE_TEXT_MODEL`).
  - Image Generation: `gemini-2.5-flash-preview-image-generation` (env: `GOOGLE_IMAGE_MODEL`).
- **Retry Policy**: `tenacity` — exponential backoff, max 3 attempts per job.

## Core Implementation Constraints
- **Image Assets**: Images MUST NOT contain text, lettering, speech bubbles, or captions. Enforced in image prompt: `NO TEXT. NO LETTERING. NO SPEECH BUBBLES. NO CAPTIONS. NO WORDS IN IMAGE.`
- **Text Rendering**: All narrative and dialogue text is served from `story_panels.narrative_text` and `story_panels.dialogue` in DB. Never from OCR or image.
- **Linguistic Rules**: Script worker validates orthography, language target, and age-appropriate complexity in a mandatory second Gemini pass before persisting.
- **Asset Storage**: `LOCAL_ASSET_DIR` env var → Docker volume `story_assets` shared between `api` and `worker`.
- **Age Validation**: Profiles with age < 4 or > 12 are rejected at the API level.

## Key Files Reference

### Backend
| File | Purpose |
|---|---|
| `apps/api/app/main.py` | FastAPI app, CORS, `/assets` static mount, lifespan |
| `apps/api/app/core/config.py` | All env vars via pydantic-settings |
| `apps/api/app/core/auth.py` | Clerk JWT decode + lazy user provisioning |
| `apps/api/app/db/session.py` | SQLModel engine + `get_session` dependency |
| `apps/api/app/models/` | 5 SQLModel tables matching specs-mvp.md §8 |
| `apps/api/app/schemas/` | Pydantic v2 request/response schemas |
| `apps/api/app/services/` | Domain logic (profile, story, feedback) |
| `apps/api/app/api/routes/` | REST routes matching specs-mvp.md §11 |
| `apps/api/app/workers/script_worker.py` | `generate_story_script` Celery task |
| `apps/api/app/workers/image_worker.py` | `generate_story_images` Celery task |
| `apps/api/alembic/versions/0001_initial.py` | Full schema migration with all constraints |

### Frontend
| File | Purpose |
|---|---|
| `apps/web/middleware.ts` | Clerk auth — all routes except `/sign-in` protected |
| `apps/web/lib/api.ts` | Typed fetch client toward FastAPI |
| `apps/web/app/dashboard/page.tsx` | Profiles + Biblioteca Mágica |
| `apps/web/app/profiles/new/page.tsx` | Profile creation form |
| `apps/web/app/profiles/[profileId]/edit/page.tsx` | Profile edit form |
| `apps/web/app/stories/new/page.tsx` | Story creation (profile + text + language) |
| `apps/web/app/stories/[storyId]/script/page.tsx` | Script review + Approve button |
| `apps/web/app/stories/[storyId]/progress/page.tsx` | Polling every 4s |
| `apps/web/app/stories/[storyId]/read/page.tsx` | Full-screen reader (image 65% / text 35%) |
| `apps/web/components/AvatarBuilder.tsx` | 5 avatar attribute selectors |
| `apps/web/components/ReactionBar.tsx` | love / funny / scary feedback buttons |

## Story Status Flow
```
pending → scripting → script_ready → approved → generating_images → completed
                                                                   ↘ failed
(any state except completed/failed) → failed
```

## Commands
```bash
# First time setup
cp .env.example .env
# Fill in: GOOGLE_API_KEY, CLERK_SECRET_KEY, NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY

# Launch all services
docker-compose up --build

# Apply DB migrations (first time only)
docker exec hero-api alembic upgrade head

# Run worker locally (inside apps/api)
celery -A app.workers.celery_app worker --loglevel=info

# Run API locally (inside apps/api)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Required Environment Variables
```
DATABASE_URL=postgresql+psycopg://hero:hero@localhost:5432/hero_ai
REDIS_URL=redis://localhost:6379/0
GOOGLE_API_KEY=                              # Required for AI generation
GOOGLE_TEXT_MODEL=gemini-2.5-pro
GOOGLE_IMAGE_MODEL=gemini-2.5-flash-preview-image-generation
CLERK_SECRET_KEY=                            # Required for auth
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=           # Required for frontend auth
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
LOCAL_ASSET_DIR=/app/storage
CORS_ALLOW_ORIGINS=http://localhost:3000
```

## Known Limitations (MVP — acceptable for this phase)
1. **Clerk JWT**: signature verification is skipped (`verify_signature=False`). Sufficient for MVP; must be hardened before production.
2. **Google model ID**: `gemini-2.5-flash-preview-image-generation` is the preview identifier. Verify current official name in Google AI Studio before deploying.
3. **No tests**: no unit or integration tests exist yet.
4. **No rate limiting**: no per-user rate limits on API endpoints.
5. **Polling only**: story progress uses 4s polling. WebSockets are out of scope for MVP.
6. **Image error handling**: if any single panel image fails, the entire story is marked `failed`. Could be made more granular.
