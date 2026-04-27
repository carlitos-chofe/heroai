# Plan: Configure LXC Access

This plan outlines the steps to make the Hero Adventure AI project accessible from outside its LXC container.

## 1. Context
- **LXC IP**: 10.10.10.130
- **Current State**: Hardcoded `localhost` in `docker-compose.yml` and `.env`.
- **Constraint**: Next.js requires `NEXT_PUBLIC_` variables at build time.

## 2. Artifacts for configure-lxc-access

### proposal.md
- **Why**: Enable external access to the services hosted in LXC.
- **What Changes**: Use environment variables for network configuration instead of hardcoded `localhost`.
- **Impact**: `.env`, `docker-compose.yml`, and `web` container.

### design.md
- **Approach**:
  - Update `docker-compose.yml` to reference `${NEXT_PUBLIC_API_BASE_URL}` and `${CORS_ALLOW_ORIGINS}`.
  - Update `.env` with the specific LXC IP.
  - Rebuild the `web` service to inject the environment variables into the static build.

### tasks.md
1. **Update `.env`**:
   - Change `NEXT_PUBLIC_API_BASE_URL` to `http://10.10.10.130:8000`.
   - Change `CORS_ALLOW_ORIGINS` to `http://10.10.10.130:3000`.
2. **Update `docker-compose.yml`**:
   - `web.environment.NEXT_PUBLIC_API_BASE_URL`: change to `${NEXT_PUBLIC_API_BASE_URL}`.
   - `api.environment.CORS_ALLOW_ORIGINS`: change to `${CORS_ALLOW_ORIGINS}`.
3. **Restart Services**:
   - Execute `docker-compose up --build -d`.

## 3. Implementation
Once this plan is approved and Plan Mode is deactivated, I will apply these changes.
