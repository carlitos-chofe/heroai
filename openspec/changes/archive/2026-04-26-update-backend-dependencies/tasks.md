## 1. Package Dependencies

- [x] 1.1 In `apps/api/pyproject.toml`, update `fastapi` to `>=0.136.1`, `sqlmodel` to `>=0.0.38`, `uvicorn[standard]` to `>=0.46.0`, and `google-genai` to `>=1.73.1`.
- [x] 1.2 In `apps/api/pyproject.toml`, update `pydantic` to `>=2.7.0` (ensure it remains `>=2.7.0` or higher to support modern SQLModel).

## 2. Model & Worker Validation

- [x] 2.1 Audit `apps/api/app/workers/script_worker.py` and `image_worker.py` to ensure `google-genai` SDK usage is compatible with version 1.73.1.
- [x] 2.2 Rebuild the backend docker container to install the new Python dependencies (`docker-compose build api worker`).

## 3. Execution & Verification

- [x] 3.1 Start the API container (`docker-compose up -d api worker`) and ensure it successfully boots without tracebacks.
- [x] 3.2 Run a simple request to the `/health` or equivalent endpoint to verify FastAPI and Uvicorn functionality.
- [x] 3.3 Create a dummy user/profile through the database or API to confirm SQLModel 0.0.38 schema validations and Pydantic integrations remain stable.