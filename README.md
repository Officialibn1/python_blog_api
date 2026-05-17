# Blog API

A RESTful blog API built with FastAPI, PostgreSQL, and Redis. It supports user authentication, role-based access control, post management, categories, tags, and comments.

---

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy (async)** — ORM with async support via `asyncpg`
- **PostgreSQL** — primary database
- **Redis** — caching and token blacklisting
- **Alembic** — database migrations
- **JWT (python-jose)** — authentication via access + refresh tokens
- **SlowAPI** — rate limiting
- **Docker / Docker Compose** — containerized infrastructure
- **uv** — Python package manager

---

## Architecture

```
blog_api/
├── app/
│   ├── api/v1/          # Route handlers (auth, users, posts, comments, tags, categories)
│   ├── core/            # Config, DB, security, cache, exceptions, logging, rate limiting
│   ├── models/
│   │   ├── db.py        # SQLAlchemy ORM models
│   │   └── domain.py    # Pure Python dataclasses (domain layer)
│   ├── repositories/    # Database access layer (raw queries via SQLAlchemy)
│   ├── schemas/         # Pydantic request/response models
│   └── services/        # Business logic layer
├── migrations/          # Alembic migration files
├── tests/               # Pytest test suite
├── docker/              # Docker entrypoint and init scripts
├── docker-compose.yml
├── docker-compose.dev.yml
├── Dockerfile
└── main.py
```

The project follows a layered architecture:

```
Request → Router → Service → Repository → Database
```

- **Routers** handle HTTP concerns (auth, validation, response codes)
- **Services** contain all business logic and orchestrate repositories
- **Repositories** are the only layer that touches the database

---

## User Roles

| Role     | Permissions                                                        |
|----------|--------------------------------------------------------------------|
| `reader` | Read posts, read/create/edit own comments                          |
| `author` | All reader permissions + create/edit/delete own posts              |
| `admin`  | Full access — manage users, categories, tags, delete any comment, assign roles |

New users are assigned the `reader` role by default. Role promotion is done by an admin via `PUT /api/v1/users/{user_id}`.

---

## API Endpoints

### Auth — `/api/v1/auth`

| Method | Path              | Description                                    | Auth          | Rate Limit  |
|--------|-------------------|------------------------------------------------|---------------|-------------|
| POST   | /register         | Register a new user                            | Public        | 10/min      |
| POST   | /login            | Login and receive access token                 | Public        | 10/min      |
| POST   | /refresh          | Refresh access token via cookie                | Cookie        | 10/min      |
| POST   | /logout           | Logout and blacklist tokens                    | Authenticated | 10/min      |
| POST   | /forgot-password  | Request a password reset email                 | Public        | 5/min       |
| POST   | /reset-password   | Reset password using token from email          | Public        | 5/min       |

### Users — `/api/v1/users`

| Method | Path                   | Description                          | Auth          | Rate Limit |
|--------|------------------------|--------------------------------------|---------------|------------|
| GET    | /                      | List all users (paginated)           | Admin         | 20/min     |
| GET    | /me                    | Get own profile                      | Authenticated | 10/min     |
| PUT    | /me                    | Update own profile                   | Authenticated | 10/min     |
| GET    | /{user_id}             | Get user by ID                       | Public        | 5/min      |
| PUT    | /{user_id}             | Update user (own or admin)           | Authenticated | 10/min     |
| PATCH  | /{user_id}             | Activate / deactivate user           | Admin         | 5/min      |
| GET    | /{author_id}/posts     | List all posts by an author          | Authenticated | —          |

### Posts — `/api/v1/posts`

| Method | Path        | Description                                              | Auth          |
|--------|-------------|----------------------------------------------------------|---------------|
| GET    | /           | List posts (paginated, filterable)                       | Public        |
| POST   | /           | Create a post                                            | Author/Admin  |
| GET    | /{post_id}  | Get a single post                                        | Public        |
| PATCH  | /{post_id}  | Update a post (own author or admin)                      | Authenticated |
| DELETE | /{post_id}  | Delete a post (own author or admin)                      | Authenticated |

**Post list query parameters:**

| Parameter     | Type    | Description                          |
|---------------|---------|--------------------------------------|
| `page`        | int     | Page number (default: 1)             |
| `size`        | int     | Items per page (default: 10, max: 100) |
| `search_term` | string  | Search by title or content           |
| `author_id`   | int     | Filter by author                     |
| `category_id` | int     | Filter by category                   |
| `tag_id`      | int     | Filter by tag                        |

### Categories — `/api/v1/categories`

| Method | Path               | Description              | Auth   |
|--------|--------------------|--------------------------|--------|
| GET    | /                  | List all categories      | Public |
| POST   | /                  | Create a category        | Admin  |
| GET    | /{category_id}     | Get category by ID       | Public |
| PATCH  | /{category_id}     | Update a category        | Admin  |
| DELETE | /{category_id}     | Delete a category        | Admin  |

### Tags — `/api/v1/tags`

| Method | Path        | Description         | Auth   |
|--------|-------------|---------------------|--------|
| GET    | /           | List all tags       | Public |
| POST   | /           | Create a tag        | Admin  |
| GET    | /{tag_id}   | Get tag by ID       | Public |
| PATCH  | /{tag_id}   | Update a tag        | Admin  |
| DELETE | /{tag_id}   | Delete a tag        | Admin  |

### Comments — `/api/v1/comments`

| Method | Path              | Description                          | Auth          |
|--------|-------------------|--------------------------------------|---------------|
| POST   | /                 | Add a comment to a post              | Authenticated |
| GET    | /{post_id}        | Get all comments for a post (paginated) | Public     |
| PATCH  | /{comment_id}     | Edit own comment                     | Authenticated |
| DELETE | /{comment_id}     | Delete a comment (own or admin)      | Authenticated |

### Health

| Method | Path      | Description        |
|--------|-----------|--------------------|
| GET    | /         | Welcome message    |
| GET    | /health   | API health check   |

---

## Authentication Flow

1. Register via `POST /api/v1/auth/register`
2. Login via `POST /api/v1/auth/login` — returns an `access_token` (15 min) and sets a `refresh_token` as an `HttpOnly` cookie (7 days)
3. Pass the access token as a `Bearer` token in the `Authorization` header:
   ```
   Authorization: Bearer <access_token>
   ```
4. When the access token expires, call `POST /api/v1/auth/refresh` — the refresh token cookie is sent automatically
5. Logout via `POST /api/v1/auth/logout` — blacklists both tokens in Redis immediately

---

## Password Reset Flow

1. Call `POST /api/v1/auth/forgot-password` with `{"email": "user@example.com"}`
2. A reset link is sent to the email (token valid for 10 minutes)
3. Call `POST /api/v1/auth/reset-password` with `{"token": "<token>", "new_password": "<password>"}`

---

## Caching

- Categories and tags list responses are cached in Redis with a **5-minute TTL**
- Cache is invalidated automatically on create, update, or delete operations
- Blacklisted tokens (logout) are stored in Redis until their natural expiry

---

## Environment Variables

| Variable                              | Description                                      | Example                                                    |
|---------------------------------------|--------------------------------------------------|------------------------------------------------------------|
| `APP_NAME`                            | Application name                                 | `"Blog API"`                                               |
| `APP_VERSION`                         | Application version                              | `1.0.0`                                                    |
| `API_V1_PREFIX`                       | API route prefix                                 | `/api/v1`                                                  |
| `DEBUG`                               | Enable debug mode                                | `False`                                                    |
| `DATABASE_URL`                        | PostgreSQL connection string (asyncpg)           | `postgresql+asyncpg://user:pass@localhost:5432/blog_db`    |
| `REDIS_URL`                           | Redis connection string                          | `redis://localhost:6379`                                   |
| `TEST_DATABASE_URL`                   | PostgreSQL connection string for tests           | `postgresql+asyncpg://user:pass@localhost:5432/blog_db_test` |
| `JWT_SECRET_KEY`                      | Secret key for signing JWTs                      | `<random-secret>`                                          |
| `JWT_ALGORITHM`                       | JWT signing algorithm                            | `HS256`                                                    |
| `JWT_ACCESS_TOKEN_EXPIRY_MINUTES`     | Access token lifetime in minutes                 | `15`                                                       |
| `JWT_REFRESH_TOKEN_EXPIRY_DAYS`       | Refresh token lifetime in days                   | `7`                                                        |
| `JWT_RESET_PASSWORD_TOKEN_EXPIRY_MINUTES` | Password reset token lifetime in minutes     | `10`                                                       |
| `MAIL_HOST`                           | SMTP host                                        | `smtp.gmail.com`                                           |
| `MAIL_PORT`                           | SMTP port                                        | `587`                                                      |
| `MAIL_USERNAME`                       | SMTP username / email address                    | `you@gmail.com`                                            |
| `MAIL_PASSWORD`                       | SMTP password or app password                    | `<app-password>`                                           |
| `MAIL_FROM`                           | Sender email address                             | `noreply@yourdomain.com`                                   |
| `APP_URL`                             | Public base URL (used in reset email links)      | `http://localhost:8000`                                    |
| `ADMIN_EMAIL`                         | Seed admin email                                 | `admin@blog.com`                                           |
| `ADMIN_USERNAME`                      | Seed admin username                              | `admin`                                                    |
| `ADMIN_PASSWORD`                      | Seed admin password                              | `<strong-password>`                                        |

Generate a secure `JWT_SECRET_KEY` with:
```bash
python -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

---

## Running with Docker (Production)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

### 1. Clone the repository

```bash
git clone <repository-url>
cd blog_api
```

### 2. Create a `.env` file

```bash
cp .env.example .env
```

Set `DATABASE_URL` to use the Docker service hostname:
```env
DATABASE_URL=postgresql+asyncpg://<user>:<password>@db:5432/blog_db
REDIS_URL=redis://redis:6379
```

### 3. Start all services

```bash
docker compose up --build
```

This starts PostgreSQL, Redis, and the API server. Migrations and admin seeding run automatically via the entrypoint script.

The app will be available at `http://localhost:8000`.

---

## Local Development (without Docker app container)

Run only the infrastructure (PostgreSQL + Redis) in Docker and the app locally.

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for the database and Redis)

### 1. Start infrastructure only

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

This starts `db` and `redis` but skips the `app` container.

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure `.env`

Use `localhost` for database and Redis:
```env
DATABASE_URL=postgresql+asyncpg://<user>:<password>@localhost:5432/blog_db
REDIS_URL=redis://localhost:6379
```

### 4. Run migrations

```bash
uv run alembic upgrade head
```

### 5. Start the server

```bash
uv run main.py
```

The app runs at `http://localhost:8000` with hot reload enabled.

---

## API Documentation

Once the server is running:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Running Tests

Tests use a separate test database (`TEST_DATABASE_URL`).

```bash
# Locally
uv run pytest tests/ -v

# With Docker
docker compose exec app uv run pytest tests/ -v
```

---

## What's Not Yet Implemented

- [ ] **Email verification** — users are active immediately after registration with no email confirmation step
- [ ] **Post caching** — individual posts and post lists are not cached, unlike categories and tags
- [ ] **File/image uploads** — no support for post cover images or user avatars
