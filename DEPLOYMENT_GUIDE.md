# WasteWise Deployment Guide

This guide will walk you through deploying the complete WasteWise platform to a production-ready, globally distributed architecture using **Supabase** (Database), **Fly.io** (Backend API & WebSockets), and **Cloudflare Pages** (Frontend PWA).

---

## Phase 1: Database Setup (Supabase)

Supabase gives us a managed PostgreSQL database with PostGIS (for geospatial queries) out of the box.

1. **Create Project**: Go to [supabase.com](https://supabase.com/), sign up, and click "New Project". Give it a name and secure password.
2. **Get Connection String**: 
   * Once the project provisions, go to **Project Settings** (the gear icon) → **Database**.
   * Scroll down to **Connection string** and select the `URI` format.
   * It will look like this: `postgresql://postgres.[project-id]:[password]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres`
   * Replace `[password]` with your actual database password. Keep this URL safe for Phase 2.

> [!TIP]
> **PostGIS**: Supabase has PostGIS installed by default! You don't need to do any extra configuration for the location-based queries to work.

---

## Phase 2: Backend Setup (Fly.io)

Fly.io will host your Python/Django/FastAPI Docker container.

### 1. Install & Authenticate
* Install the Fly CLI: [Instructions here](https://fly.io/docs/hands-on/install-flyctl/).
* Open your terminal and run: `fly auth signup` or `fly auth login`.

### 2. Initialize the App
Navigate into your backend folder:
```bash
cd /Users/mac/Downloads/eee/wastewise-web/backend
fly launch
```
* **App Name**: Choose a unique name (e.g., `wastewise-api`).
* **Region**: Choose a region close to your users (e.g., `jnb` Johannesburg).
* **Set up Postgres?**: Choose **No** (we are using Supabase).
* **Set up Upstash Redis?**: Choose **Yes** (we need this for WebSockets and Celery).
* **Deploy now?**: Choose **No**.

### 3. Configure Processes (Web + Background Tasks)
Open the newly generated `fly.toml` file in the `backend/` folder and add a `[processes]` block to tell Fly to run both your API and Celery background workers:

```toml
[processes]
  web = "daphne -b 0.0.0.0 -p 8000 core.asgi:application"
  worker = "celery -A core worker -l info"
  beat = "celery -A core beat -l info"
```
*(Make sure the `[[services]]` block in the file specifies `processes = ["web"]` so internet traffic only goes to Daphne).*

### 4. Set Environment Variables
We must securely pass our API keys and database URL:
```bash
fly secrets set DATABASE_URL="<your-supabase-uri>"
fly secrets set SECRET_KEY="create-a-long-random-secret-string"
fly secrets set CORS_ALLOWED_ORIGINS="https://<your-project>.pages.dev"
fly secrets set DEBUG="False"
```

### 5. Deploy & Migrate
Deploy the container to the internet:
```bash
fly deploy
```

Once deployed, run your database migrations inside the cloud container:
```bash
fly ssh console -C "python manage.py migrate"
fly ssh console -C "python manage.py createsuperuser"
```
*(Follow the prompts to create your admin account).*

**Your backend is now live at: `https://wastewise-api.fly.dev`**

---

## Phase 3: Frontend Setup (Cloudflare Pages)

Cloudflare Pages will host your HTML/CSS/JS files and distribute them to edge servers globally.

### 1. Update API Base URL
Before uploading, your frontend needs to know where the backend is. Create or update your API configuration file (e.g., `frontend/js/api.js`) to point to Fly.io:

```javascript
// Change this before deploying
const API_BASE_URL = "https://wastewise-api.fly.dev/api";
const WS_BASE_URL = "wss://wastewise-api.fly.dev/ws";
```
*(Ensure all your `fetch()` calls in the frontend use this `API_BASE_URL` instead of a hardcoded `/api/` path).*

### 2. Deploy via Cloudflare Dashboard
The easiest way without Git is a direct upload:
1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Navigate to **Workers & Pages** -> **Create application** -> **Pages**.
3. Click **Upload assets**.
4. Drag and drop your entire `/Users/mac/Downloads/eee/wastewise-web/frontend` folder into the upload area.
5. Click **Deploy**.

> [!IMPORTANT]
> **SPA Routing Rule**: In your Cloudflare Pages dashboard, go to Settings -> Build & deployments -> **Single-page application (SPA)** and ensure it is checked. This ensures that refreshing the page doesn't break your hash routing!

---

## 🎉 Verification

1. Go to your Cloudflare Pages URL (e.g., `https://wastewise.pages.dev`).
2. Attempt to log in or request an OTP.
3. If it succeeds, your Frontend is talking to your Fly.io Backend, which is saving data into your Supabase Database!
