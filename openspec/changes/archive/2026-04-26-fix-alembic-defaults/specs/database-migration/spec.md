## ADDED Requirements

### Requirement: Database Initialization
The `alembic upgrade head` command SHALL run without throwing `invalid input syntax for type json` errors.

#### Scenario: Running initial migration
- **WHEN** the user executes `alembic upgrade head`
- **THEN** the `child_profiles` table is created successfully with the correct `preference_summary` default (`'{}'::jsonb`)
- **AND** the `story_panels` table is created successfully with the correct `generation_status` default (`'pending'`)