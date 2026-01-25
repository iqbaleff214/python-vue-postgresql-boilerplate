# Python + Vue + PostgreSQL Boilerplate

A production-ready boilerplate for modern web applications with **separated Frontend and Backend**.

- **Backend**: Python (API + Worker)
- **Frontend**: Vue.js
- **Database**: PostgreSQL
- **Queue/Broker**: Redis
- **Email-ready**: SMTP / transactional email
- **Auth-ready**: Login, Logout, Register, Forgot Password
- **Authorization**: Multi-role with hardcoded permissions

---

## Architecture Overview

```
root/
│
├── backend/                  # Python Backend (API + Worker)
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── auth/             # Auth logic
│   │   ├── users/            # User & profile
│   │   ├── mail/             # Email templates & helpers
│   │   ├── tasks/            # Celery tasks
│   │   ├── core/             # Config, security, constants
│   │   ├── models/           # ORM models
│   │   ├── celery.py     # Celery App entrypoint
│   │   └── main.py           # API entrypoint
│   │
│   ├── migrations/
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/                 # Vue.js Application
│   ├── src/
│   ├── public/
│   ├── .env.example
│   └── README.md
│
└── README.md
````


## Tech Stack

### Backend (API + Worker)
- Python 3.10+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Celery
- Redis (broker & result backend)
- JWT Authentication
- Alembic / Django Migrations

### Frontend
- Vue 3 (Composition API)
- Vite
- Vue Router
- Pinia
- Axios

---

## Core Features

### Authentication
- Register
- Login
- Logout
- Forgot Password
- Reset Password via email link
- JWT-based authentication

### User Management
- View profile
- Update profile
- Change password

### Authorization (Multi-Role)
- Roles are **static / hardcoded**
- Typical roles:
  - `ADMIN`
- Permission checks:
  - Backend: dependency / middleware
  - Frontend: route meta & UI condition

---

## Email & Worker System

### Design Principles
- API never sends email directly
- All emails are sent via Celery background jobs
- Worker uses the same codebase as the API

### Common Tasks
- Send reset password email
- Send welcome email
- Send password changed notification

### Forgot Password Flow

1. User submits email
2. API generates reset token (with expiration)
3. API enqueues Celery task
4. Celery worker sends email with reset link
5. User opens link → frontend reset page
6. Frontend calls reset password API

---

## Environment Variables

### Backend `.env`

```env
APP_NAME='Python Vue Boilerplate'
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development # options: development, production, staging

DATABASE_URL=postgresql://username:password@localhost:5432/python_vue_boilerplate
REDIS_URL=redis://localhost:6379/0

SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=

DO_SPACES_REGION=
DO_SPACES_BUCKET=
DO_SPACES_ACCESS_KEY=
DO_SPACES_SECRET_KEY=
DO_SPACES_ENDPOINT=https://sgp1.digitaloceanspaces.com
DO_SPACES_CDN_ENDPOINT=https://sgp1.digitaloceanspaces.com

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-email-password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME="Python Vue Boilerplate"

MIDTRANS_SERVER_KEY=
MIDTRANS_CLIENT_KEY=
MIDTRANS_IS_PRODUCTION=false
MIDTRANS_NOTIFICATION_URL=http://localhost:8000/payments/notification
````

---

## Running the Application

### Backend API

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

API available at:

```
http://localhost:8000
```

### Celery Worker

Run in **separate terminal**, same directory and env:

```bash
cd backend
source venv/bin/activate

celery -A app.celery worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at:

```
http://localhost:5173
```

---

## Role & Permission Example

### Backend (Hardcoded)

```python
ROLE_PERMISSIONS = {
    "ADMIN": ["user.read", "user.write", "system.manage"],
    "STAFF": ["user.read"],
    "USER": ["profile.read", "profile.update"],
}
```

### Frontend (Route Guard)

```js
{
  path: "/admin",
  meta: {
    requiresAuth: true,
    roles: ["ADMIN"]
  }
}
```

---

## API Endpoints

### Auth

* `POST /auth/login`
* `POST /auth/register`
* `POST /auth/logout`
* `POST /auth/forgot-password`
* `POST /auth/reset-password`

### User

* `GET /users/me`
* `PUT /users/me`
* `PUT /users/change-password`

---

## Security Notes

* Passwords hashed (bcrypt / argon2)
* Reset tokens are single-use and time-limited
* Role checks enforced server-side
* Rate limiting recommended for auth endpoints
* CORS restricted by environment

---

## Production Notes

* Run API and Celery as separate processes/containers
* Use managed Redis & email provider
* Enable Celery retries and monitoring
* Use HTTPS and secure secrets management

This boilerplate prioritizes **simplicity, clarity, and fast iteration**, suitable for MVPs and internal tools.

## License

MIT