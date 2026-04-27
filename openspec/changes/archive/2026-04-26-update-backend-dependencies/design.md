## Context

The backend infrastructure `apps/api` is running outdated dependencies (`fastapi>=0.111.0`, `sqlmodel>=0.0.19`, `uvicorn[standard]>=0.29.0`, `google-genai>=1.7.0`). Following the successful Next.js 16 update on the frontend, we are now standardizing the backend dependencies to modern versions (`fastapi>=0.136.1`, `sqlmodel>=0.0.38`, `uvicorn>=0.46.0`, `google-genai>=1.73.1`). These bumps contain major bug fixes, Pydantic v2 optimizations in SQLModel, and significant enhancements in the Google GenAI SDK.

## Goals / Non-Goals

**Goals:**
- Successfully bump core backend dependencies to their most recent stable versions.
- Ensure SQLModel 0.0.38 compatibility with existing models, considering it heavily integrates with Pydantic v2.
- Refactor the Celery worker (`script_worker.py`, `image_worker.py`) usage of `google-genai` to align with the new 1.73.1 SDK syntax if there are deprecations.
- Ensure the API still starts cleanly and health checks pass.

**Non-Goals:**
- Changing database schema or running new Alembic migrations (unless the SQLModel update forces an internal constraint change, which is highly unlikely for minor versions).
- Upgrading PostgreSQL or Redis Docker images.
- Modifying frontend code.

## Decisions

- **Version Bumps in pyproject.toml**: We will manually bump the versions in `apps/api/pyproject.toml` and rely on `pip install` (or Docker build) to fetch the latest compliant dependencies.
- **SQLModel Validation**: SQLModel has evolved rapidly. We will run the API and immediately hit the `/health` or core endpoints to verify that the Pydantic v2 schema generation still matches FastAPI's OpenAPI expectations.
- **Google GenAI SDK Verification**: The `google-genai` package had major refactors between 1.7.x and 1.73.x. We will review the workers to ensure the initialization of the `genai` client and the calling syntax (like `client.models.generate_content`) remain valid.

## Risks / Trade-offs

- **Risk: Breaking changes in Google GenAI SDK**: The massive version jump (1.7 to 1.73) might introduce removed parameters or changed client instantiation.
  - *Mitigation*: We will carefully review the worker files (`script_worker.py` and `image_worker.py`) after the update, and test the Celery tasks locally to ensure the AI pipeline still works.
- **Risk: Pydantic v2/SQLModel conflicts**: Although the current project likely already uses Pydantic v2, SQLModel `0.0.38` is much stricter about model inheritance.
  - *Mitigation*: We will run `pytest` (if available) or spin up the API via `uvicorn` and watch for startup traceback errors, fixing any `ConfigDict` or inheritance issues immediately.