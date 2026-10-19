# Deploying Smart Medical Box

The frontend is a static site on Vercel and the Flask API runs on Render. The
backend supports both MySQL and PostgreSQL. Set `MYSQL_URL` to use MySQL;
otherwise, it uses `DATABASE_URL` for PostgreSQL. The two GitHub repositories
are separate.

## Local MySQL development

Install MySQL 8.0 and create a database and dedicated application user:

```sql
CREATE DATABASE smart_medical_box
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'smart_medical_box'@'localhost'
    IDENTIFIED BY 'choose-a-strong-password';
GRANT ALL PRIVILEGES ON smart_medical_box.*
    TO 'smart_medical_box'@'localhost';
```

Copy `.env.example` to `.env`, set `MYSQL_URL` to the local database connection
URL, and set a private `SECRET_KEY`. URL-encode special characters in database
credentials. Do not commit `.env` or share its contents. When `MYSQL_URL` is
set, the backend uses MySQL and creates tables from `schema.mysql.sql`.

The backend can also use local PostgreSQL by leaving `MYSQL_URL` unset and
setting `DATABASE_URL`; that schema is in `schema.sql`.

## Render backend

1. Verify your Render account email, then import the
   `smart-medical-box-backend` GitHub repository into Render as a Blueprint,
   using the repository root. Render reads `render.yaml` to configure the
   Python web service and PostgreSQL database.
2. The Blueprint sets `DATABASE_URL` to the Render PostgreSQL database. Do not
   set `MYSQL_URL` on the Render service unless you have a hosted MySQL server:
   the local MySQL server at `localhost` or `127.0.0.1` belongs to the
   developer's computer, not Render.
3. On startup, the backend initializes the schema for the configured database.
   Render generates the Flask session secret and secure session cookies are
   enabled. Check `/api/health` on the generated Render URL.

The Blueprint uses Render's free PostgreSQL and web-service plans for a demo.
Free PostgreSQL is limited to 1 GB and expires 30 days after creation; after a
14-day grace period, Render deletes the database and its data. Free web
services spin down after 15 minutes without inbound traffic. This setup is not
appropriate for production data or dependable medicine reminders. Upgrade to
paid plans before storing real user or medical data.

The app starts without web-push keys, but push subscription and medicine
notifications require `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, and
`VAPID_SUBJECT` to be set as Render environment variables. Keep the private key
secret.

The reminder scheduler checks for due doses every five seconds. Actual delivery
can take longer due to the push provider and receiving device. Render's free
web service sleeps after inactivity, so reminders are not dependable on the
free plan.

Notification sound and vibration are controlled by the receiving device and
browser. On Android, allow sound and vibration for the browser's notifications
and this site. On iOS, web-push sound and vibration support depends on iOS
notification settings and browser support. The optional dashboard tone only
plays while the dashboard is open and the sound option is enabled.

## Vercel frontend

1. Import the `smart-medical-box-frontend` repository into Vercel. Use the
   repository root as the project root; no build command is needed.
2. Set the Vercel environment variable `BACKEND_URL` to the Render service's
   public origin (for example, `https://your-api.onrender.com`, without a
   trailing slash).
3. Deploy the frontend. Its `/api/*` requests are proxied through Vercel to
   Render, keeping session cookies same-origin in the browser.

The frontend continues to use `http://127.0.0.1:5000` for local development
when opened from localhost. For local backend development, install
`requirements.txt`, configure MySQL or PostgreSQL in `backend/.env`, then run
the Flask app. The service initializes the corresponding database schema on
startup.
