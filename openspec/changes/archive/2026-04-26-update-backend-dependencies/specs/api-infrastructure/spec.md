## ADDED Requirements

### Requirement: FastAPI 0.136.1 Compliance
The backend API MUST run cleanly on `fastapi>=0.136.1` and `uvicorn>=0.46.0` without startup or routing errors.

#### Scenario: API Application Boot
- **WHEN** the FastAPI application is initialized via Uvicorn
- **THEN** it MUST start successfully without raising `FastAPI` or `Starlette` deprecation errors

### Requirement: SQLModel 0.0.38 Compatibility
The database models MUST be compatible with `sqlmodel>=0.0.38` and correctly integrate with Pydantic v2 schemas.

#### Scenario: Database Session and Schema Integrity
- **WHEN** a database session is instantiated and models are parsed
- **THEN** the schemas MUST validate correctly and all Alembic migrations MUST remain compatible with the ORM definitions

### Requirement: Google GenAI 1.73.1 Integration
The Celery workers MUST successfully invoke the Google AI models using the `google-genai>=1.73.1` SDK syntax.

#### Scenario: Text and Image Model Invocation
- **WHEN** the `script_worker.py` or `image_worker.py` is executed
- **THEN** the GenAI client MUST instantiate correctly and return valid generative responses without SDK-specific errors