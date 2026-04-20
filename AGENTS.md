# AGENTS.md - Hero Adventure AI

## Project State
- **Current Status**: Specification & Planning phase. No implementation code currently exists in the repository.
- **Primary Source of Truth**: `specs-mvp.md` (Technical Specification for MVP).

## Intended Architecture
Monorepo structure as defined in `specs-mvp.md`:
- `apps/web/`: Next.js 16 (App Router), TypeScript, Clerk.
- `apps/api/`: FastAPI, SQLModel/SQLAlchemy, Alembic, Pydantic v2.
- `apps/api/workers/`: Celery workers for async AI generation.
- `storage/`: Local filesystem storage for generated comic assets.

## Tech Stack & Infrastructure
- **Database**: PostgreSQL 16.
- **Broker/Cache**: Redis 7.
- **Auth**: Clerk.
- **AI Models**:
  - Text/Scripting: `Gemini 2.5 Pro`.
  - Image Generation: `Gemini 2.5 Flash Image (Nano Banana)`.

## Core Implementation Constraints
- **Image Assets**: Images MUST NOT contain text, lettering, speech bubbles, or captions.
- **Text Rendering**: All narrative and dialogue text must be served from the database and rendered as UI elements in the frontend.
- **Linguistic Rules**: Text must be validated for orthography and adapted to the child's age range (4-12) and target language (`es`, `en`, `mixed_es_en`).
- **Asset Storage**: Use `LOCAL_ASSET_DIR` for persisting images; ensuring the volume is shared between `api` and `worker`.

## Intended Commands
- **Environment**: `docker-compose up` to launch `web`, `api`, `worker`, `redis`, and `postgres`.
- **API**: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` (inside `apps/api`).
- **Worker**: `celery -A app.workers.celery_app worker --loglevel=info` (inside `apps/api`).
- **Migrations**: `alembic upgrade head`.
