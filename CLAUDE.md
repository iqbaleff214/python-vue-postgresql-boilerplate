# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python + Vue.js + PostgreSQL boilerplate for web applications with separated frontend and backend. This is a scaffolding/template project — actual application code is built on top of this structure.

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Celery, Redis, JWT auth (HS256)
- **Frontend**: Vue 3 (Composition API), Vite, Vue Router, Pinia, Axios
- **Database**: PostgreSQL
- **Queue/Broker**: Redis (Celery broker and result backend)
- **Email**: SMTP via Celery background tasks (API never sends email directly)

## Common Commands

### Backend

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run API server (http://localhost:8000)
uvicorn app.main:app --reload

# Run Celery worker (separate terminal, same venv)
celery -A app.celery worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev    # http://localhost:5173
```

### Environment Setup

Copy `.env.example` to `.env` in both `backend/` and `frontend/` directories. Requires PostgreSQL and Redis running locally.

## Architecture

```
backend/
  app/
    main.py          # FastAPI entrypoint
    celery.py        # Celery app entrypoint
    api/             # API route handlers
    auth/            # Authentication logic
    users/           # User & profile management
    mail/            # Email templates & SMTP helpers
    tasks/           # Celery background tasks
    core/            # Config, security, constants
    models/          # SQLAlchemy ORM models
  migrations/        # Alembic database migrations

frontend/
  src/
    components/      # Vue components
    views/           # Page-level views
    stores/          # Pinia state stores
    router/          # Vue Router with role-based guards
    services/        # Axios API service layer
```

### Data Flow

Frontend (Axios) → Backend API (FastAPI) → Database (PostgreSQL). Background work (emails, notifications) is dispatched to Celery via Redis, processed by the worker using the same backend codebase.

### Authentication & Authorization

- JWT tokens (HS256) with configurable expiry (default 30 min)
- Optional Google OAuth 2.0
- Static/hardcoded RBAC roles (ADMIN, STAFF, USER) with permission maps
- Backend enforces via dependency injection/middleware; frontend enforces via route meta guards and conditional rendering

### API Endpoints

Auth: `POST /auth/{login,register,logout,forgot-password,reset-password}`
User: `GET /users/me`, `PUT /users/me`, `PUT /users/change-password`

### Email Pattern

All emails go through Celery tasks, never sent directly from API handlers. Forgot-password flow: API generates time-limited single-use token → enqueues Celery task → worker sends email with reset link → user clicks link to frontend → frontend calls reset API.

## Optional Integrations

Configured via environment variables (see `.env.example` files):
- **File storage**: DigitalOcean Spaces or AWS S3
- **Payments**: Midtrans (notification webhook at `/payments/notification`)
- **Monitoring**: Sentry (backend + frontend), Google Analytics (frontend)
- **Feature flags**: Frontend Vite env vars (`VITE_ENABLE_GOOGLE_SSO`, `VITE_ENABLE_PAYMENT`, `VITE_ENABLE_ANALYTICS`)
