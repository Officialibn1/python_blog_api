#!/bin/sh
uv run alembic upgrade head

HASHED=$(uv run python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('${ADMIN_PASSWORD}'))")
PSQL_URL=$(echo "$DATABASE_URL" | sed 's|postgresql+asyncpg|postgresql|')

psql "$PSQL_URL" <<SQL
INSERT INTO users (email, username, hashed_password, role, is_active, created_at)
SELECT '${ADMIN_EMAIL}', '${ADMIN_USERNAME}', '${HASHED}', 'admin', true, NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE role = 'admin');
SQL

exec uv run main.py
