## Why

This change upgrades the core dependencies of the backend API layer (`apps/api`) to their latest stable versions, including `fastapi` (from >=0.111.0 to >=0.136.1), `sqlmodel` (from >=0.0.19 to >=0.0.38), `uvicorn` (from >=0.29.0 to >=0.46.0), and `google-genai` (from >=1.7.0 to >=1.73.1). Following the successful UI layer upgrade, this ensures the backend also benefits from the latest security patches, performance improvements, and API enhancements, reducing technical debt.

## What Changes

- **BREAKING**: Upgrade `fastapi` to `>=0.136.1` in `apps/api/pyproject.toml`.
- **BREAKING**: Upgrade `sqlmodel` to `>=0.0.38` in `apps/api/pyproject.toml`.
- **BREAKING**: Upgrade `uvicorn[standard]` to `>=0.46.0` in `apps/api/pyproject.toml`.
- **BREAKING**: Upgrade `google-genai` to `>=1.73.1` in `apps/api/pyproject.toml`.
- **Refactoring**: Address any deprecation warnings or breaking changes surfaced by FastAPI or SQLModel upgrades during testing.
- **Refactoring**: Ensure the `google-genai` client and model invocation patterns align with the updated `1.73.1` SDK syntax.

## Capabilities

### New Capabilities

- `api-infrastructure`: Specifications for framework and dependency compliance on the backend (FastAPI, SQLModel, Google GenAI SDK).

### Modified Capabilities

*(No existing capabilities modified at the specification level.)*

## Impact

- **API Dependencies**: `apps/api/pyproject.toml`
- **Generative AI Integration**: `apps/api/app/workers/script_worker.py` and `image_worker.py`
- **Database ORM**: `apps/api/app/models/` and routing models using `SQLModel`
- **Server Execution**: Docker compose backend build and execution scripts