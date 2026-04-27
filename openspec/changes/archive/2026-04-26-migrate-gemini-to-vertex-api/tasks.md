## 1. Project Configuration

- [x] 1.1 Update `pyproject.toml` to remove `google-generativeai>=0.7.0` and add `google-genai>=1.7.0`.
- [x] 1.2 Update `app/core/config.py` to include `gcp_project_id` and `gcp_location` (default to 'us-central1') in the settings model.
- [x] 1.3 Add `GCP_PROJECT_ID` and `GCP_LOCATION` variables to the `.env.example` and local `.env` files.

## 2. Text Generation Migration (`script_worker.py`)

- [x] 2.1 Update imports from `google.generativeai` to the new `google.genai` SDK.
- [x] 2.2 Replace global `genai.configure` with local `client = genai.Client(vertexai=True, project=settings.gcp_project_id, location=settings.gcp_location, api_key=settings.google_api_key)` inside the worker.
- [x] 2.3 Refactor text generation call to use `client.models.generate_content(...)`.
- [x] 2.4 Update the response parsing logic to use `response.text` from the unified SDK output.

## 3. Image Generation Migration (`image_worker.py`)

- [x] 3.1 Update imports from `google.generativeai` to the new `google.genai` SDK and `google.genai.types`.
- [x] 3.2 Replace global `genai.configure` with local `client = genai.Client(vertexai=True, ...)` inside `_generate_image_bytes`.
- [x] 3.3 Refactor image generation call to use `client.models.generate_images(...)` with `types.GenerateImagesConfig`.
- [x] 3.4 Update the byte extraction logic to pull from `response.generated_images[0].image.image_bytes`.

## 4. Validation and Deployment

- [x] 4.1 Run standard tests or trigger a local API flow to ensure text and image scripts generate without errors.
- [x] 4.2 Verify the `vertexai=True` behavior traces back to GCP as expected while honoring the `GOOGLE_API_KEY`.
