# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python + Vue.js + PostgreSQL boilerplate for web applications with separated frontend and backend.

## Tech Stack

- **Backend**: Python 3.10+, FastAPI (async), SQLAlchemy (async with asyncpg), Alembic, JWT auth (HS256), bcrypt
- **Frontend**: Vue 3 (Composition API), TypeScript, Vite, Vue Router, Pinia, Axios, Tailwind CSS
- **Database**: PostgreSQL (async via asyncpg)
- **Queue/Broker**: Redis (Celery broker and result backend, not yet implemented)

## Common Commands

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Run API server (http://localhost:8001)
uvicorn app.main:app --reload --port 8001

# Swagger docs at http://localhost:8001/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev       # http://localhost:5173
npm run build     # Production build (runs vue-tsc then vite build)
```

### Environment Setup

Copy `.env.example` to `.env` in both `backend/` and `frontend/` directories. Requires PostgreSQL running locally. Update `DATABASE_URL` in `backend/.env` with real credentials.

## Architecture

```
backend/
  app/
    main.py              # FastAPI app, CORS, mounts api_router
    database.py          # Async SQLAlchemy engine + session factory
    core/
      config.py          # Pydantic BaseSettings loading .env
      security.py        # bcrypt password hashing, JWT create/decode
      constants.py       # ROLE_PERMISSIONS map
      dependencies.py    # get_db, get_current_user (HTTPBearer + JWT)
    models/
      base.py            # DeclarativeBase + TimestampMixin
      user.py            # User model (UUID PK, name, surname, email, phone_number, avatar_url, role, extra_data, password_hash)
    auth/
      schemas.py         # LoginRequest (identifier field), RegisterRequest, TokenResponse
      service.py         # authenticate_user (email/phone detection), register_user, create_user_token
      router.py          # POST /auth/login, /auth/register, /auth/logout
    users/
      schemas.py         # UserResponse (from_attributes=True)
      router.py          # GET /users/me
    api/
      router.py          # Aggregates auth (/auth) + users (/users) routers
  migrations/
    env.py               # Async-aware Alembic env
    versions/             # Migration scripts

frontend/
  src/
    main.ts              # App bootstrap (Pinia + Router)
    App.vue              # Root component (<router-view />)
    style.css            # Tailwind directives
    services/
      api.ts             # Axios instance, Bearer token interceptor, 401 redirect
      auth.ts            # login(), register(), getMe(), logout() + TS interfaces
    stores/
      auth.ts            # Pinia auth store: token (localStorage), user, login/register/logout actions
    router/
      index.ts           # Routes with meta.requiresAuth / meta.guest guards
    views/
      LoginView.vue      # Single identifier (email/phone) + password
      RegisterView.vue   # name, surname, email, phone, password
      DashboardView.vue  # Protected page with AppLayout
    components/
      AppLayout.vue      # Nav bar with user name + logout
```

### Key Patterns

- **Login identifier**: Single field auto-detects email vs phone number (contains `@` = email, otherwise phone). Logic in `backend/app/auth/service.py:is_email()`.
- **Database URL**: `.env` uses `postgresql://` but `database.py` replaces it with `postgresql+asyncpg://` for async support.
- **JWT payload**: Minimal `{"sub": user_id_as_string, "exp": ...}`. User is always fetched from DB on each request via `get_current_user` dependency.
- **Auth guard**: Frontend router `beforeEach` checks token + user. If token exists but user isn't loaded, calls `fetchUser()` to validate.
- **Token storage**: `localStorage` key `"token"`. Axios reads it directly from localStorage (not store) to avoid circular dependencies.
- **CORS**: Backend allows only the `FRONTEND_URL` origin.

### API Endpoints

- `POST /auth/login` — body: `{identifier, password}` → `{access_token, token_type}`
- `POST /auth/register` — body: `{name, surname?, email, phone_number, password}` → `{access_token, token_type}`
- `POST /auth/logout` — no-op acknowledgment (JWT is stateless)
- `GET /users/me` — requires Bearer token → `UserResponse`

### Users Table

UUID primary key, columns: `name`, `surname` (nullable), `email` (unique, indexed), `phone_number` (unique, indexed), `avatar_url` (nullable), `role` (string, default "USER"), `extra_data` (JSON), `password_hash`, `created_at`, `updated_at`.

## Optional Integrations

Configured via environment variables (see `.env.example` files):
- **File storage**: DigitalOcean Spaces or AWS S3
- **Payments**: Midtrans (notification webhook at `/payments/notification`)
- **Monitoring**: Sentry (backend + frontend), Google Analytics (frontend)
- **Feature flags**: `VITE_ENABLE_GOOGLE_SSO`, `VITE_ENABLE_PAYMENT`, `VITE_ENABLE_ANALYTICS`
