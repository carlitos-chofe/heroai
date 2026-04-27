## Context

The system is deployed in an LXC container and accessed locally via `http://heroai.local:3000`. Currently, Clerk authentication successfully completes but fails to redirect back to the application due to missing or misconfigured fallback redirect environment variables. In addition, the API and CORS configuration are hardcoded to the container's IP (`10.10.10.130`) instead of utilizing the `heroai.local` domain, causing cross-origin and API access issues.

## Goals / Non-Goals

**Goals:**
- Fix the Clerk sign-in and sign-up redirect flows so users are properly sent back to `/dashboard` upon authentication.
- Ensure the backend API base URL and CORS origins accept the `heroai.local` domain to enable seamless communication between frontend and backend in local LXC environments.

**Non-Goals:**
- We are not changing the core authentication provider or rewriting the Clerk implementation.
- We are not handling production domains or configuring reverse proxies (like Nginx) outside of the `.env` settings.

## Decisions

- **Environment Variable Updates**: Update `.env` and `.env.example` with `NEXT_PUBLIC_CLERK_SIGN_IN_FALLBACK_REDIRECT_URL` and `NEXT_PUBLIC_CLERK_SIGN_UP_FALLBACK_REDIRECT_URL` pointing to `/dashboard`. This is a standard Next.js Clerk integration pattern to control post-auth redirection without hardcoding absolute paths.
- **API URL Updates**: Change `NEXT_PUBLIC_API_BASE_URL` to `http://heroai.local:8000` and `CORS_ALLOW_ORIGINS` to include `http://heroai.local:3000`. This unifies the local development experience under a single domain name, sidestepping IP changes when recreating or restarting LXC containers.
- **Component Modifications**: Explicitly add `fallbackRedirectUrl="/dashboard"` to the `<SignIn />` component in `apps/web/app/sign-in/page.tsx` as a defense-in-depth approach alongside the environment variables.

## Risks / Trade-offs

- **Risk**: Hardcoding `/dashboard` as a fallback means all sign-ins will go to the dashboard regardless of where the user started. 
  - *Mitigation*: This is acceptable for the current MVP requirements since `/dashboard` is the main entry point after login.
- **Risk**: Other team members might not use `heroai.local` or LXC containers.
  - *Mitigation*: The `.env.example` should reflect standard setups, but documenting this specific setup allows flexibility for developers using `.local` domains. The example can show both `localhost` and `heroai.local` or clearly comment on the use-case.