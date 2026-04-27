## 1. Docker Compose Configuration Updates

- [x] 1.1 Update `docker-compose.yml`: Add `GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json` environment variable to the `api` service.
- [x] 1.2 Update `docker-compose.yml`: Add volume mount `- ~/.config/gcloud:/root/.config/gcloud:ro` to the `api` service.
- [x] 1.3 Update `docker-compose.yml`: Add `GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json` environment variable to the `worker` service.
- [x] 1.4 Update `docker-compose.yml`: Add volume mount `- ~/.config/gcloud:/root/.config/gcloud:ro` to the `worker` service.

## 2. Verification

- [x] 2.1 Restart containers with `docker-compose down && docker-compose up -d`.
- [x] 2.2 Trigger a story generation through the frontend and monitor `hero-worker` logs to ensure Vertex AI authentication succeeds and images/scripts are generated.