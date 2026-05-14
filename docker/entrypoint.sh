#!/bin/sh
uv run alembic upgrade head
exec uv run main.py
