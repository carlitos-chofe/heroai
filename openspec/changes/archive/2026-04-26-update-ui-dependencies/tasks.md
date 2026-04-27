## 1. Package Dependencies

- [x] 1.1 In `apps/web/package.json`, update `next` to `16.2.4`, `@clerk/nextjs` to `7.2.7`, and `react`/`react-dom` to `^19.2.5`.
- [x] 1.2 Run `npm install` inside `apps/web` to update the `package-lock.json` and `node_modules`.

## 2. Infrastructure & Layout Migration

- [x] 2.1 Update `apps/web/app/layout.tsx` to move `<ClerkProvider>` inside the `<body>` tag.
- [x] 2.2 Update `apps/web/middleware.ts` to `await auth()` before calling `.protect()`.

## 3. Asynchronous APIs Compliance (Next.js 16)

- [x] 3.1 Audit `apps/web/app/stories/[storyId]/read/page.tsx` and refactor `params` access to use Next.js 16 Promise-based APIs or `useParams` appropriately.
- [x] 3.2 Audit `apps/web/app/stories/[storyId]/progress/page.tsx` and refactor `params` access.
- [x] 3.3 Audit `apps/web/app/stories/[storyId]/script/page.tsx` and refactor `params` access.
- [x] 3.4 Audit `apps/web/app/profiles/[profileId]/edit/page.tsx` and refactor `params` access.

## 4. Verification

- [x] 4.1 Run `npm run build` in `apps/web` to verify there are no compilation errors or hydration issues.
- [x] 4.2 Start the local dev server (`npm run dev`) and test authentication flow and dynamic routes.