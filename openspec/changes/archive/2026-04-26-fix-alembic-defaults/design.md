## Context

When initializing the database with `alembic upgrade head`, the script fails with `invalid input syntax for type json` due to literal strings being used as `server_default` for `JSONB` and `String` columns in the `0001_initial.py` migration file.

## Goals / Non-Goals

**Goals:**
- Fix the Alembic migration script so the database can be initialized without errors.

**Non-Goals:**
- Modifying the actual SQLAlchemy models (they are already correct).

## Decisions

- **Use `sa.text()` for literal defaults in Alembic**: Alembic/SQLAlchemy's `server_default` expects a SQL expression or a string that will be quoted. To pass raw SQL strings (like `'{}'::jsonb` or `'pending'`), they must be wrapped in `sa.text()` to avoid SQLAlchemy adding extra quotes that cause invalid syntax in PostgreSQL.

## Risks / Trade-offs

- **Risk**: Database already exists with a different schema. 
  **Mitigation**: This is the initial migration, so any existing database failing this step is likely empty or incomplete and can be safely recreated.