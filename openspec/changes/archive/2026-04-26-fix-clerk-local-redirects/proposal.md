## Why

The application is being run in an LXC container and accessed via a local domain (`http://heroai.local:3000`) rather than `localhost`. Because of this change in the origin, the current Clerk authentication flow succeeds but fails to redirect back to the app properly. Additionally, backend environment configurations for CORS and the API base URL are hardcoded to the container's IP address instead of using the new local domain, which breaks cross-origin requests.

## What Changes

- Update environment variables to handle Clerk fallback redirects correctly after successful sign-in/sign-up.
- Update API and CORS environment variables to properly reflect the new `heroai.local` domain instead of the container's IP.
- Modify the sign-in page component to enforce a fallback redirect URL.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `authentication`: Ensuring the authentication redirect flow handles the local domain setup properly.
- `network-configuration`: Setting appropriate defaults and examples for CORS and API base URL in local containerized environments.

## Impact

- `apps/web/app/sign-in/page.tsx`
- `.env` and `.env.example` configurations (affecting both frontend API calls and backend CORS validation)