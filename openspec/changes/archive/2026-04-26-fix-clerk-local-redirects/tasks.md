## 1. Environment Configuration

- [x] 1.1 Update `.env` and `.env.example` with `NEXT_PUBLIC_CLERK_SIGN_IN_FALLBACK_REDIRECT_URL=/dashboard`
- [x] 1.2 Update `.env` and `.env.example` with `NEXT_PUBLIC_CLERK_SIGN_UP_FALLBACK_REDIRECT_URL=/dashboard`
- [x] 1.3 Update `.env` and `.env.example` to set `NEXT_PUBLIC_API_BASE_URL=http://heroai.local:8000`
- [x] 1.4 Update `.env` and `.env.example` to set `CORS_ALLOW_ORIGINS=http://heroai.local:3000`

## 2. Frontend Updates

- [x] 2.1 Update `apps/web/app/sign-in/page.tsx` to add `fallbackRedirectUrl="/dashboard"` to the `<SignIn />` component