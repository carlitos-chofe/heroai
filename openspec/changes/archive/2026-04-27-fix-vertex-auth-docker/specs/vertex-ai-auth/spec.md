## ADDED Requirements

### Requirement: Local Development Vertex AI Authentication
The local development environment MUST allow Docker containers (`api` and `worker`) to authenticate with Google Cloud Vertex AI using the host machine's Application Default Credentials (ADC).

#### Scenario: Running worker container reads host credentials
- **WHEN** the `worker` or `api` service is started via `docker-compose`
- **THEN** the container MUST have read access to the host's `~/.config/gcloud/` directory
- **AND** the `GOOGLE_APPLICATION_CREDENTIALS` environment variable MUST point to the `application_default_credentials.json` file within that mounted directory
- **AND** the AI generation tasks MUST successfully authenticate and execute using those credentials without throwing a "default credentials were not found" error.