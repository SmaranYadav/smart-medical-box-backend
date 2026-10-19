# Deploying Smart Medical Box

The frontend is a static site on Vercel; the Flask API and PostgreSQL database
run on Render. The frontend and backend repositories are separate.

## Render backend

1. Verify your Render account email, then import the
   `smart-medical-box-backend` GitHub repository into Render as a Blueprint,
   using the repository root. Render reads `render.yaml` to configure the
   Python web service and PostgreSQL database.
2. The service's `DATABASE_URL` is linked to the database by the Blueprint.
   Render generates the Flask session secret, and secure session cookies are
   enabled.
3. On its first successful database connection, the service creates the
   application tables from `schema.sql` if they do not exist. The scheduler
   creates its reminder-log table at startup. Check `/api/health` on the
   generated Render URL.

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
when opened from localhost.

For local backend development, install `requirements.txt`, create a local
PostgreSQL database, and configure `DATABASE_URL` and `SECRET_KEY` in
`backend/.env` using `.env.example` as a template.
