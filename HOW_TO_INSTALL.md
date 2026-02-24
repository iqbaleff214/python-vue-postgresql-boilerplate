# How to Install & Configure

This document covers the project setup and the configuration steps for each optional integration.

---

## Table of Contents

- [Project Setup](#project-setup)
  - [Prerequisites](#prerequisites)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Backend setup](#2-backend-setup)
  - [3. Frontend setup](#3-frontend-setup)
  - [4. Run the application](#4-run-the-application)
- [Integrations](#integrations)
  - [Google OAuth](#google-oauth)
  - [Facebook OAuth](#facebook-oauth)
  - [Email (SMTP)](#email-smtp)
  - [File Storage (DigitalOcean Spaces / AWS S3)](#file-storage)
  - [Payment (Midtrans)](#payment-midtrans)
  - [Monitoring (Sentry)](#monitoring-sentry)

---

## Project Setup

### Prerequisites

Make sure the following are installed on your machine before starting:

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.10+ | |
| Node.js | 18+ | |
| PostgreSQL | 14+ | Must be running locally or accessible via URL |
| Redis | 6+ | Required for Celery background tasks |

### 1. Clone the repository

```bash
git clone https://github.com/your-org/python-vue-boilerplate.git
cd python-vue-boilerplate
```

### 2. Backend setup

#### Create and activate a virtual environment

```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

#### Install dependencies

```bash
pip install -r requirements.txt
```

#### Configure environment variables

```bash
cp .env.example .env
```

Open `backend/.env` and update the following required values:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/python_vue_boilerplate
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
FRONTEND_URL=http://localhost:5173
```

#### Create the database

Create the PostgreSQL database manually before running migrations:

```bash
psql -U postgres -c "CREATE DATABASE python_vue_boilerplate;"
```

#### Run database migrations

```bash
alembic upgrade head
```

### 3. Frontend setup

In a new terminal:

```bash
cd frontend
npm install
cp .env.example .env
```

Open `frontend/.env` and update:

```env
VITE_APP_API_URL=http://localhost:8001
```

### 4. Run the application

You need up to three terminals running simultaneously.

**Terminal 1 — Backend API** (port 8001):

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

**Terminal 2 — Celery Worker** (required for emails):

```bash
cd backend
source venv/bin/activate
celery -A app.celery worker --loglevel=info
```

**Terminal 3 — Frontend** (port 5173):

```bash
cd frontend
npm run dev
```

Once all three are running:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8001 |
| Swagger docs | http://localhost:8001/docs |

---

## Integrations

The following integrations are optional. Each requires environment variables in `backend/.env` and/or `frontend/.env`.

---

## Google OAuth

Allows users to sign in with their Google account via the Google Identity Services (GSI) popup.

### 1. Create a Google Cloud project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Navigate to **APIs & Services → Credentials**
4. Click **Create Credentials → OAuth 2.0 Client ID**
5. Set **Application type** to **Web application**
6. Under **Authorized JavaScript origins**, add:
   - `http://localhost:5173` (development)
   - Your production frontend URL
7. Click **Create** and copy the **Client ID** and **Client Secret**

### 2. Configure backend

In `backend/.env`:

```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

Install the required package (if not already done):

```bash
cd backend
source venv/bin/activate
pip install google-auth httpx
```

### 3. Configure frontend

In `frontend/.env`:

```env
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

### 4. How it works

- The frontend loads the Google GSI script from `index.html`
- Clicking the **Google** button on login/register calls `google.accounts.id.prompt()`
- Google returns a signed **ID token** (credential)
- The frontend POSTs `{ credential }` to `POST /auth/google`
- The backend verifies the token with Google and finds or creates the user account
- A standard app JWT is returned — identical flow to email/password login from that point

---

## Facebook OAuth

Allows users to sign in with their Facebook account via the Facebook JS SDK popup.

### 1. Create a Facebook App

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click **My Apps → Create App**
3. Choose **Consumer** as the app type
4. Fill in the app name and contact email, then click **Create App**
5. In the app dashboard, add the **Facebook Login** product
6. Under **Facebook Login → Settings**, add to **Valid OAuth Redirect URIs**:
   - `http://localhost:5173` (development)
   - Your production frontend URL
7. Go to **Settings → Basic** and copy the **App ID** and **App Secret**

> Make sure the app is set to **Live** mode (not Development) when you want public users to log in. In Development mode, only app admins and testers can authenticate.

### 2. Configure backend

In `backend/.env`:

```env
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

Install the required package (if not already done):

```bash
cd backend
source venv/bin/activate
pip install httpx
```

### 3. Configure frontend

In `frontend/.env`:

```env
VITE_FACEBOOK_APP_ID=your-facebook-app-id
```

### 4. How it works

- The frontend loads the Facebook SDK script from `index.html`
- On mount, `FB.init()` is called with your App ID
- Clicking the **Facebook** button triggers `FB.login()` with `public_profile,email` scope
- Facebook returns an **access token**
- The frontend POSTs `{ access_token }` to `POST /auth/facebook`
- The backend verifies the token via two Graph API calls (`/debug_token` + `/me`) and finds or creates the user account
- A standard app JWT is returned

> **Note:** Facebook does not always provide an email address (e.g. if the account was created with a phone number). If no email is returned, the backend responds with HTTP 400.

---

## Email (SMTP)

Used for transactional emails such as reset password links and welcome emails. Emails are sent via Celery background tasks — the API never sends email directly.

### 1. Configure backend

In `backend/.env`:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME="Your App Name"
```

### 2. Gmail setup

If using Gmail, you must use an **App Password** (not your regular account password):

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** (required)
3. Go to **App passwords**, generate one for "Mail"
4. Use the generated 16-character password as `SMTP_PASSWORD`

### 3. Start the Celery worker

Email tasks run in a background worker. Start it in a separate terminal:

```bash
cd backend
source venv/bin/activate
celery -A app.celery worker --loglevel=info
```

Redis must be running as the task broker:

```bash
redis-server
```

---

## File Storage

Used for user avatar uploads. Supports DigitalOcean Spaces (S3-compatible).

### DigitalOcean Spaces

1. Create a Space at [cloud.digitalocean.com](https://cloud.digitalocean.com/)
2. Generate an **Spaces Access Key** under **API → Spaces Keys**

In `backend/.env`:

```env
DO_SPACES_REGION=sgp1
DO_SPACES_BUCKET=your-bucket-name
DO_SPACES_ACCESS_KEY=your-access-key
DO_SPACES_SECRET_KEY=your-secret-key
DO_SPACES_ENDPOINT=https://sgp1.digitaloceanspaces.com
DO_SPACES_CDN_ENDPOINT=https://sgp1.digitaloceanspaces.com
```

Replace `sgp1` with your region (e.g. `nyc3`, `ams3`).

---

## Payment (Midtrans)

Used for payment processing. A notification webhook receives payment status updates from Midtrans.

### 1. Create a Midtrans account

1. Register at [midtrans.com](https://midtrans.com/)
2. Go to **Settings → Access Keys**
3. Copy your **Server Key** and **Client Key** (use Sandbox keys for development)

### 2. Configure backend

In `backend/.env`:

```env
MIDTRANS_SERVER_KEY=your-server-key
MIDTRANS_CLIENT_KEY=your-client-key
MIDTRANS_IS_PRODUCTION=false
MIDTRANS_NOTIFICATION_URL=https://your-domain.com/payments/notification
```

In `frontend/.env`:

```env
VITE_MIDTRANS_CLIENT_KEY=your-client-key
```

> For local development, use a tunneling tool like [ngrok](https://ngrok.com/) to expose your local server for Midtrans webhook callbacks.

---

## Monitoring (Sentry)

Used for error tracking and performance monitoring.

### 1. Create a Sentry project

1. Sign up at [sentry.io](https://sentry.io/)
2. Create a new project — select **FastAPI** for backend, **Vue** for frontend
3. Copy the **DSN** for each project

### 2. Configure backend

In `backend/.env`:

```env
SENTRY_DSN=https://your-key@sentry.io/your-project-id
```

### 3. Configure frontend

In `frontend/.env`:

```env
VITE_SENTRY_DSN=https://your-key@sentry.io/your-project-id
```
