## Context

The current `apps/web` project is running Next.js `15.3.1` and `@clerk/nextjs` `^6.12.0`. Newer stable versions are available (Next.js `16.2.4` and Clerk `7.2.7`), bringing improved performance, caching enhancements, and important paradigm shifts (like fully asynchronous request APIs in Next.js). We are adopting a "layered upgrade" strategy, modernizing the UI layer first while keeping the backend infrastructure (`apps/api`) intact to isolate and minimize risks.

## Goals / Non-Goals

**Goals:**
- Successfully bump `next` to `16.2.4` and `@clerk/nextjs` to `7.2.7`.
- Adapt the application code to conform to the breaking changes introduced by Next.js 16 (asynchronous `params` and `searchParams`).
- Adjust the layout structure to meet Clerk 7's requirement of rendering `<ClerkProvider>` inside the `<body>`.
- Refactor the authentication middleware to use the new asynchronous `auth()` function signature.

**Non-Goals:**
- Upgrading backend services (FastAPI, SQLModel, Uvicorn) or infrastructure (PostgreSQL, Redis).
- Changing or refactoring application business logic or adding new features.
- Adopting Turbopack across the entire build process if it introduces critical build errors (we'll focus on the framework upgrade first).

## Decisions

- **Handling Asynchronous Request APIs**: For Client Components (`"use client"`), we will continue using the `useParams()` hook as it is safe and handles the dynamic segments automatically on the client. For any Server Components that rely on dynamic route `params`, we will refactor them to use the new Promise-based `props.params` and `await` them.
- **ClerkProvider Relocation**: Move `<ClerkProvider>` to reside purely within the `<body>` tag in `app/layout.tsx`. This avoids the strict hydration errors Clerk 7 throws if it wraps `<html>`.
- **Middleware Update**: The `middleware.ts` will `await auth()` before calling `.protect()`, as `auth` is no longer a synchronous object but an asynchronous function.

## Risks / Trade-offs

- **Risk: Breaking Data Fetching/Caching**: Next.js 16 may alter default caching behaviors or `fetch` caching semantics.
  - *Mitigation*: We will review `lib/api.ts` and the polling mechanism in `[storyId]/progress/page.tsx` to ensure `fetch` options (`cache: "no-store"` or `revalidate`) are explicitly defined.
- **Risk: Next.js Peer Dependency Conflicts**: Some existing packages (like `react`) might complain about Next 16 if they haven't explicitly added it to their peer dependencies.
  - *Mitigation*: Update `react` to the latest `19.2.5` version matching Next.js 16 requirements and use `--legacy-peer-deps` only if strictly necessary.