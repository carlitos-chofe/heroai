## Context

The backend services (`api` and `worker`) use the `google-genai` SDK configured to access Google Cloud Vertex AI (`vertexai=True`). Vertex AI ignores API keys and requires Application Default Credentials (ADC) to authenticate requests.

The current development environment is hosted on an LXC machine, where Google Cloud credentials are generated using the host's `gcloud init --console-only` or `gcloud auth application-default login --no-browser` and stored in `~/.config/gcloud/`. However, the Celery worker generating the scripts and images runs inside an isolated Docker container which does not have access to the host's filesystem. Consequently, when the SDK inside Docker attempts to locate the ADC, it throws a `"Your default credentials were not found"` error.

## Goals / Non-Goals

**Goals:**
- Provide a mechanism for the `google-genai` SDK running inside Docker containers to locate and use the host machine's Application Default Credentials (ADC) during local development.
- Allow developers to authenticate seamlessly by simply running `gcloud` login commands on their host.

**Non-Goals:**
- Implementing production-grade authentication using Service Accounts (IAM JSON keys) is explicitly out of scope for this change (we will address this when deploying to a production environment).
- Modifying the Python code for the AI workers (`script_worker.py` and `image_worker.py`), as they are already correctly configured to use `vertexai=True`.

## Decisions

- **Decision 1: Use Read-Only Docker Bind Mounts**
  - **Rationale**: By mounting the host's `~/.config/gcloud/` directory to the container, any updates to the credentials (like refreshing expired tokens via the host's `gcloud` CLI) are instantly reflected inside the container without needing to rebuild or restart the Docker services.
  - **Alternatives Considered**: Copying the credentials file into the Docker image during the build process. This was rejected because ADC tokens expire, and copying them would require frequent, tedious container rebuilds.

- **Decision 2: Explicitly set `GOOGLE_APPLICATION_CREDENTIALS`**
  - **Rationale**: While the SDK natively looks for credentials in standard paths (like `~/.config/gcloud/`), specifying the `GOOGLE_APPLICATION_CREDENTIALS` environment variable guarantees that the SDK locates the JSON file regardless of the user the container is running under (e.g., `root` vs a non-root user).
  - **Alternatives Considered**: Relying purely on the default search path. This was rejected due to its fragility in containerized environments where the `$HOME` path might vary.

## Risks / Trade-offs

- **Risk: Cross-platform compatibility for path expansion (`~`) in Docker Compose**
  - **Mitigation**: Docker Compose generally resolves `~` to the home directory of the user executing `docker-compose up`. This should work reliably in LXC/Linux and macOS environments. If an issue arises on Windows, users may need to specify the absolute path.
- **Risk: Permissions and Ownership**
  - **Mitigation**: We will mount the volume as read-only (`:ro`). The container processes just need to read the JSON file. If the container runs as a non-root user with a different UID/GID that lacks read access to the host's files, developers might face a permission denied error. We'll monitor this, but standard Docker-on-Linux setups usually handle read-only mounts of user files smoothly.