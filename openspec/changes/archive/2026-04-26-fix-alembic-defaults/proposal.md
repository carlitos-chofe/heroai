## Why

Running `alembic upgrade head` fails when setting up the database with the initial schema because of an invalid input syntax for type json. This is caused by literal strings being passed as `server_default` for `JSONB` and `String` columns in the Alembic migration file, causing PostgreSQL to receive extra quotes and fail.

## What Changes

Update the Alembic migration script `0001_initial.py` to correctly define `server_default` values for JSONB and String columns using SQLAlchemy's `sa.text()` wrapper. This prevents SQLAlchemy from incorrectly escaping or quoting literal strings when generating the DDL.

## Capabilities

### New Capabilities
- `database-migration`: Fixing the alembic migration script to initialize the database without errors.

### Modified Capabilities
None.

## Impact

- `apps/api/alembic/versions/0001_initial.py`: Migration script will be updated.
- No other APIs or dependencies are affected. The underlying `models/child_profile.py` has a correct definition for SQLAlchemy but requires the migration fix.