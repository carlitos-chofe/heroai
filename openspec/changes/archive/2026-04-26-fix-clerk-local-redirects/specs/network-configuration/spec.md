## ADDED Requirements

### Requirement: Local domain configuration
The system SHALL support cross-origin requests and API communication using the local domain `heroai.local`.

#### Scenario: API base URL resolution
- **WHEN** the frontend application attempts to reach the backend API
- **THEN** it resolves to `http://heroai.local:8000` as configured by the environment variables

#### Scenario: Cross-origin resource sharing
- **WHEN** the frontend application (`http://heroai.local:3000`) sends a request to the backend API (`http://heroai.local:8000`)
- **THEN** the backend API accepts the request and responds successfully, validating the origin against `CORS_ALLOW_ORIGINS`