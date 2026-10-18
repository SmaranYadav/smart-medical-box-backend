# Deploying Smart Medical Box

The frontend is a static site for Vercel; the Flask API and its MySQL database
run on Railway. The repositories are separate, so configure each platform with
its matching GitHub repository and set the project root to that repository's
root.

## Railway backend

1. Create a Railway project and add a MySQL service.
2. Deploy the `smart-medical-box-backend` repository as a service. The
   `Procfile` starts Gunicorn and the medicine-reminder scheduler.
3. Add these variables to the backend service, using Railway's MySQL variable
   references where applicable:
   - `SECRET_KEY`: a long, randomly generated secret.
   - `MYSQLHOST`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`, and
     `MYSQLPORT`: reference the corresponding variables from the MySQL service.
   - `SESSION_COOKIE_SECURE=true`.
   - `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, and `VAPID_SUBJECT` for web push.
     `VAPID_PRIVATE_KEY` is the PEM content of the private key; keep it in
     Railway's secret variables and never commit it.
4. Generate a public domain for the backend. On startup, the backend creates
   the application tables from `schema.sql` if they do not exist; the scheduler
   also creates its reminder-log table. Its `/api/health` endpoint should
   return a successful status.

## Vercel frontend

1. Import the `smart-medical-box-frontend` repository into Vercel. Use the
   repository root as the project root; no build command is needed.
2. Add `BACKEND_URL` as a Vercel environment variable, set to the Railway
   backend's public origin (for example, `https://your-api.up.railway.app`,
   without a trailing slash).
3. Deploy the frontend. Its `/api/*` requests are proxied through Vercel to
   Railway, keeping session cookies same-origin in the browser.

The frontend continues to use `http://127.0.0.1:5000` for local development
when opened from localhost. Do not put database passwords, Flask secrets, or
VAPID private keys in frontend files or Vercel client-side variables.
