# Blog API

A RESTful blog API built with FastAPI, PostgreSQL, and Redis. It supports user authentication, role-based access control, post management, categories, tags, and comments.

---

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy (async)** — ORM with async support via `asyncpg`
- **PostgreSQL** — primary database
- **Redis** — caching layer
- **Alembic** — database migrations
- **JWT (python-jose)** — authentication via access + refresh tokens
- **SlowAPI** — rate limiting
- **Docker / Docker Compose** — containerized infrastructure

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
├── docker/              # Docker init scripts
├── docker-compose.yml
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

| Role     | Permissions                                      |
|----------|--------------------------------------------------|
| `reader` | Read posts, read/create comments                 |
| `author` | All reader permissions + create/edit/delete own posts |
| `admin`  | Full access — manage users, categories, tags, delete any comment |

---

## API Endpoints

### Auth — `/api/v1/auth`
| Method | Path       | Description                          | Auth     |
|--------|------------|--------------------------------------|----------|
| POST   | /register  | Register a new user                  | Public   |
| POST   | /login     | Login and receive access token       | Public   |
| POST   | /refresh   | Refresh access token via cookie      | Cookie   |

### Users — `/api/v1/users`
| Method | Path        | Description                          | Auth          |
|--------|-------------|--------------------------------------|---------------|
| GET    | /           | List all users (paginated)           | Admin         |
| GET    | /me         | Get own profile                      | Authenticated |
| PUT    | /me         | Update own profile                   | Authenticated |
| GET    | /{user_id}  | Get user by ID                       | Public        |
| PUT    | /{user_id}  | Update user (own or admin)           | Authenticated |
| PATCH  | /{user_id}  | Activate / deactivate user           | Admin         |

### Posts — `/api/v1/posts`
| Method | Path        | Description                          | Auth          |
|--------|-------------|--------------------------------------|---------------|
| GET    | /           | List posts (paginated, filter by published) | Public |
| POST   | /           | Create a post                        | Author/Admin  |
| GET    | /{post_id}  | Get a single post                    | Public        |
| PATCH  | /{post_id}  | Update a post (own author only)      | Authenticated |
| DELETE | /{post_id}  | Delete a post (own author or admin)  | Authenticated |

### Categories — `/api/v1/categories`
| Method | Path             | Description              | Auth   |
|--------|------------------|--------------------------|--------|
| GET    | /                | List all categories      | Public |
| POST   | /                | Create a category        | Admin  |
| GET    | /{category_id}   | Get category by ID       | Public |
| DELETE | /{category_id}   | Delete a category        | Admin  |

### Tags — `/api/v1/tags`
| Method | Path        | Description         | Auth   |
|--------|-------------|---------------------|--------|
| GET    | /           | List all tags       | Public |
| POST   | /           | Create a tag        | Admin  |
| GET    | /{tag_id}   | Get tag by ID       | Public |
| DELETE | /{tag_id}   | Delete a tag        | Admin  |

### Comments — `/api/v1/comments`
| Method | Path           | Description                    | Auth          |
|--------|----------------|--------------------------------|---------------|
| POST   | /              | Add a comment to a post        | Authenticated |
| GET    | /{post_id}     | Get all comments for a post    | Public        |
| DELETE | /{comment_id}  | Delete a comment               | Admin         |

---

## Authentication Flow

1. Register via `POST /api/v1/auth/register`
2. Login via `POST /api/v1/auth/login` — returns an `access_token` (15 min) and sets a `refresh_token` as an `HttpOnly` cookie (7 days)
3. Pass the access token as a `Bearer` token in the `Authorization` header
4. When the access token expires, call `POST /api/v1/auth/refresh` — the refresh token cookie is read automatically

---

## Caching

Categories and tags list responses are cached in Redis with a 5-minute TTL. The cache is invalidated automatically on create or delete operations.

---

## Running the Application

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed

### 1. Clone the repository

```bash
git clone <repository-url>
cd blog_api
```

### 2. Create a `.env` file

```bash
cp .env.example .env   # or create it manually
```

Populate it with the following values:

```env
APP_NAME="Blog API"
APP_VERSION=1.0.0
API_V1_PREFIX=/api/v1
DEBUG=False
DATABASE_URL=postgresql+asyncpg://<user>:<password>@db:5432/blog_db
REDIS_URL=redis://redis:6379
TEST_DATABASE_URL=postgresql+asyncpg://<user>:<password>@db:5432/blog_db_test
JWT_SECRET_KEY=<your-secret-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRY_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRY_DAYS=7
```

### 3. Start all services

```bash
docker compose up --build
```

This starts PostgreSQL, Redis, and the API server. The app will be available at `http://localhost:8000`.

### 4. Run database migrations

In a separate terminal (while containers are running):

```bash
docker compose exec app uv run alembic upgrade head
```

### 5. Access the API docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Running Without Docker (Local Development)

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- A running PostgreSQL and Redis instance

### Setup

```bash
# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate

# Run migrations
alembic upgrade head

# Start the server
uv run main.py
```

---

## Running Tests

```bash
# With Docker
docker compose exec app uv run pytest tests/ -v

# Locally
uv run pytest tests/ -v
```

---

## What's Not Yet Implemented

The following features are missing and would be natural next additions:

- [ ] **Token blacklisting / logout** — there is no logout endpoint; issued tokens remain valid until expiry. A Redis-backed token blacklist would fix this.
- [ ] **Password reset flow** — no forgot-password or reset-password endpoints exist.
- [ ] **Email verification** — users are active immediately after registration with no email confirmation step.
- [ ] **Post search and filtering** — posts can only be filtered by `published` status. There is no search by title, author, category, or tag.
- [ ] **Pagination on comments** — comments are returned as a flat list with no pagination.
- [x] **Update/edit comments** — there is no `PUT`/`PATCH` endpoint for comments.
- [x] **Category and tag update** — there are no `PUT`/`PATCH` endpoints for categories or tags.
- [x] **Author profile / public posts by user** — no endpoint to fetch all posts by a specific author.
- [ ] **Post caching** — individual posts and post lists are not cached, unlike categories and tags.
- [x] **Admin role assignment** — there is no endpoint to promote a user to `admin` or `author`; the role must be set directly in the database.
- [ ] **File/image uploads** — no support for post cover images or user avatars.
- [x] **`.env.example` file** — there is no example env file for new contributors.
