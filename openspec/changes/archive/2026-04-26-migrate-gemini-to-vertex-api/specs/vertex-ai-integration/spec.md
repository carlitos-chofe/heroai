## ADDED Requirements

### Requirement: Unified GenAI Client Initialization
The system SHALL initialize the `google-genai` client configured for Vertex AI instead of using the legacy `google-generativeai` SDK. The client MUST be explicitly instantiated per worker with `vertexai=True` and the required project, location, and API key credentials.

#### Scenario: Worker invokes model
- **WHEN** a background worker starts a generation task
- **THEN** it creates a new `genai.Client` passing `vertexai=True`
- **THEN** the request successfully routes to the Vertex AI endpoints

### Requirement: GCP Environment Configuration
The system SHALL require `GCP_PROJECT_ID` and `GCP_LOCATION` as environment variables to correctly configure the Vertex AI client.

#### Scenario: Application startup
- **WHEN** the FastAPI application or Celery workers initialize
- **THEN** the system reads `GCP_PROJECT_ID` and `GCP_LOCATION` from the environment or `.env` file along with the `GOOGLE_API_KEY`

### Requirement: Text Generation Compatibility
The script worker SHALL generate text using the new unified SDK's `client.models.generate_content` method and correctly extract the text response, ensuring no degradation in story generation quality.

#### Scenario: Script generation
- **WHEN** `generate_story_script` is executed
- **THEN** the system passes the prompt to `client.models.generate_content`
- **THEN** the system extracts the text using `response.text` and validates it against linguistic and age rules

### Requirement: Image Generation Compatibility
The image worker SHALL generate PNG images using the new unified SDK's `client.models.generate_images` method and correctly extract the image bytes, ensuring no degradation in panel illustration generation.

#### Scenario: Panel image generation
- **WHEN** `_generate_image_bytes` is executed
- **THEN** the system passes the prompt to `client.models.generate_images`
- **THEN** the system extracts the bytes from the generated image object
