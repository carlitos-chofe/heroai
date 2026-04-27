## Why

This change upgrades the core dependencies of the frontend web application (UI layer) to their latest stable versions: Next.js from 15.3.1 to 16.2.4 and `@clerk/nextjs` from ^6.12.0 to 7.2.7. Upgrading these libraries proactively prevents technical debt accumulation, ensures we benefit from the latest performance improvements (like caching/Turbopack enhancements in Next 16), and aligns our codebase with the latest async patterns enforced by both frameworks.

## What Changes

- **BREAKING**: Upgrade `next` to `16.2.4` in `apps/web/package.json`.
- **BREAKING**: Upgrade `@clerk/nextjs` to `7.2.7` in `apps/web/package.json`.
- **Refactoring**: Update `apps/web/app/layout.tsx` to move `<ClerkProvider>` inside the `<body>` tag, as required by Clerk v7.
- **Refactoring**: Update `apps/web/middleware.ts` to await the `auth()` function, as it is now asynchronous in Clerk v7.
- **Refactoring**: Audit and update all Next.js dynamic route components (e.g., `[storyId]`, `[profileId]`) to consume `params` and `searchParams` asynchronously if passed as props, or ensure `useParams` is used safely in Client Components.

## Capabilities

### New Capabilities

- `ui-infrastructure`: Specifications for framework and dependency compliance (Next.js 16, Clerk 7).

### Modified Capabilities

*(No existing capabilities modified at the specification level.)*

## Impact

- **UI Dependencies**: `apps/web/package.json`
- **Application Layout**: `apps/web/app/layout.tsx`
- **Authentication Flow**: `apps/web/middleware.ts`
- **Dynamic Routes**: Components in `apps/web/app/stories/[storyId]/` and `apps/web/app/profiles/[profileId]/`