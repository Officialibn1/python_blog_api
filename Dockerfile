FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN UV_PROJECT_ENVIRONMENT=/opt/venv uv sync --frozen

COPY . .

CMD ["sh", "docker/entrypoint.sh"]
