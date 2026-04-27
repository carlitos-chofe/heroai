## Why

The project currently uses the legacy `google-generativeai` SDK which is designed primarily for Google AI Studio. To align with enterprise requirements, leverage Google Cloud's infrastructure, and use the latest officially recommended unified API, we need to migrate to Vertex AI using the new unified `google-genai` SDK. This allows us to continue using the existing API Key via the `vertexai=True` configuration while modernizing the codebase.

## What Changes

- **SDK Replacement**: Remove the old `google-generativeai` dependency and install the new unified `google-genai` SDK.
- **Client Initialization**: Update `script_worker.py` and `image_worker.py` to instantiate the new `genai.Client` with `vertexai=True` and the API key.
- **Environment Variables**: Add `GCP_PROJECT_ID` and `GCP_LOCATION` to support Vertex AI regional requirements.
- **Method Signatures**: Update the model invocation methods (e.g., from `model.generate_content` to `client.models.generate_content` and images to `client.models.generate_images`) to match the new SDK structure.

## Capabilities

### New Capabilities
- `vertex-ai-integration`: Implementation of the unified Google GenAI SDK configured for Vertex AI mode across all backend workers.

### Modified Capabilities
- None: This is an implementation detail change. The functional requirements for story generation remain exactly the same.

## Impact

- **Backend Dependencies**: `pyproject.toml` requires updates to swap the Google GenAI SDK packages.
- **Celery Workers**: Both `apps/api/app/workers/script_worker.py` and `apps/api/app/workers/image_worker.py` require refactoring of how they invoke the AI models.
- **Configuration**: `apps/api/app/core/config.py` and the `.env` schema must include the new GCP project and location variables.
