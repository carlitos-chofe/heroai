## 1. Migration Updates

- [x] 1.1 Update `preference_summary` default to use `sa.text("'{}'::jsonb")` in `0001_initial.py`
- [x] 1.2 Update `generation_status` default to use `sa.text("'pending'")` in `0001_initial.py`

## 2. Verification

- [x] 2.1 Verify database initialized by running `docker exec hero-api alembic upgrade head`