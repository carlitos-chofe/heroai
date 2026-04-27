## Context

The current implementation relies on the legacy `google-generativeai` SDK, which is tied to Google AI Studio. While functional, enterprise requirements demand routing our AI requests through Vertex AI on Google Cloud. Google recently released the unified `google-genai` SDK which allows seamless switching between AI Studio and Vertex AI via configuration (`vertexai=True`), while still supporting authentication via API Key for ease of transition.

## Goals / Non-Goals

**Goals:**
- Upgrade the backend to use the unified `google-genai` SDK.
- Configure the SDK to route all requests through Vertex AI.
- Continue using the existing API Key for authentication to avoid complex IAM/Service Account setups in this phase.
- Update project configuration to include GCP project ID and location identifiers.
- Ensure zero regression in story generation quality, performance, or existing system logic.

**Non-Goals:**
- Moving to Service Account/IAM authentication (out of scope for now, keeping API Key).
- Changing the underlying generative models (Gemini Pro/Flash versions remain exactly the same).

## Decisions

- **Decision 1: Use unified `google-genai` SDK over `google-cloud-aiplatform`**
  - **Rationale**: The unified SDK is the newest official recommendation from Google for both AI Studio and Vertex AI. It provides a cleaner, modern interface and makes the "Vertex AI + API Key" setup trivial with the `vertexai=True` flag.
  - **Alternatives**: Using the heavier `google-cloud-aiplatform` SDK (complex and lacks the simplified GenAI interface) or keeping the old SDK without Vertex support.

- **Decision 2: Explicit Client Instantiation**
  - **Rationale**: Instead of global configuration (`genai.configure()`), we will instantiate a `genai.Client` per worker session. This follows the new SDK's idiomatic usage and is more robust for concurrent worker tasks.

## Risks / Trade-offs

- **Risk: SDK Response Incompatibility** 
  - **Trade-off/Mitigation**: The unified SDK has slightly different response objects (e.g., extracting text or image bytes). We will carefully update the extraction logic in the workers and test thoroughly to prevent regressions.
- **Risk: Vertex AI quota/region issues** 
  - **Trade-off/Mitigation**: We will default to `us-central1` where Gemini models are fully supported, but allow this to be configurable via environment variables.
