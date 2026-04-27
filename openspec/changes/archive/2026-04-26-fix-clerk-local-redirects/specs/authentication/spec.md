## ADDED Requirements

### Requirement: Clerk authentication redirects
The system SHALL redirect the user to the `/dashboard` route upon successful sign-in or sign-up.

#### Scenario: Successful sign-in redirect
- **WHEN** the user successfully signs in using Clerk
- **THEN** the system redirects the user to `/dashboard`

#### Scenario: Successful sign-up redirect
- **WHEN** the user successfully signs up using Clerk
- **THEN** the system redirects the user to `/dashboard`