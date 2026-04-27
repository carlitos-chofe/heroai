## ADDED Requirements

### Requirement: Next.js 16 Asynchronous Request APIs Compliance
The web application MUST handle `params` and `searchParams` asynchronously in all Server Components, as required by Next.js 16. Client Components MAY continue using `useParams()` safely.

#### Scenario: Server Component Rendering
- **WHEN** a Server Component receives `params` via props
- **THEN** it MUST await `props.params` before accessing its properties to avoid runtime errors

### Requirement: Clerk v7 Layout Provider Compliance
The web application MUST wrap the Next.js `children` with `<ClerkProvider>` exclusively inside the `<body>` tag to comply with Clerk v7's architectural requirements.

#### Scenario: Root Layout Rendering
- **WHEN** the `RootLayout` component renders the application shell
- **THEN** `<ClerkProvider>` MUST be a direct child of `<body>` and MUST NOT wrap the `<html>` tag

### Requirement: Clerk v7 Asynchronous Middleware Compliance
The Next.js middleware MUST execute authentication protection using the new asynchronous `auth()` function provided by `@clerk/nextjs/server`.

#### Scenario: Middleware Execution on Protected Route
- **WHEN** a user requests a protected route
- **THEN** the middleware MUST `await auth()` to resolve the authentication state before calling `.protect()`