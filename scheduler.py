
import json
import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from pywebpush import WebPushException

from config import MYSQL_URL
from db import get_connection, get_cursor
from push_utils import send_push

TIMEZONE = ZoneInfo("Asia/Kolkata")
CHECK_INTERVAL_SECONDS = 5


def check_due_reminders():
    """Find medicines due now and push alerts to subscribed devices."""
    now = datetime.now(TIMEZONE)
    today = now.date()
    current_time = now.strftime("%H:%M")

    conn = get_connection()
    cursor = get_cursor(conn)

    try:
        cursor.execute("""
            SELECT medicine_id, user_id, medicine_name, dosage,
                   dose_times, start_date, end_date, instructions
            FROM user_medicine_track_details
            WHERE status = 'Active'
              AND start_date <= %s
              AND end_date >= %s
        """, (today, today))

        medicines = cursor.fetchall()

        for medicine in medicines:
            raw_times = medicine["dose_times"]

            if isinstance(raw_times, str):
                try:
                    dose_times = json.loads(raw_times)
                except (ValueError, TypeError):
                    print(
                        "Invalid dose_times for medicine:",
                        medicine["medicine_id"]
                    )
                    continue
            else:
                dose_times = raw_times or []

            if not isinstance(dose_times, list):
                continue

            # Only send a reminder when a dose matches the current minute.
            if current_time not in dose_times:
                continue

            cursor.execute("""
                SELECT endpoint, p256dh, auth
                FROM push_subscriptions
                WHERE user_id = %s
            """, (medicine["user_id"],))

            subscriptions = cursor.fetchall()

            for sub in subscriptions:
                endpoint = sub["endpoint"]

                # Hash the endpoint so the database doesn't need to store it
                # again in the reminder log.
                import hashlib
                endpoint_hash = hashlib.sha256(
                    endpoint.encode("utf-8")
                ).hexdigest()

                # Skip a reminder already sent for this dose and device.
                cursor.execute("""
                    SELECT id
                    FROM medicine_reminder_log
                    WHERE medicine_id = %s
                      AND dose_date = %s
                      AND dose_time = %s
                      AND endpoint_hash = %s
                """, (
                    medicine["medicine_id"],
                    today,
                    current_time,
                    endpoint_hash
                ))

                if cursor.fetchone():
                    continue

                subscription_info = {
                    "endpoint": endpoint,
                    "keys": {
                        "p256dh": sub["p256dh"],
                        "auth": sub["auth"]
                    }
                }

                payload = {
                    "title": "Time to take your medicine",
                    "body": (
                        f'{medicine["medicine_name"]} '
                        f'({medicine["dosage"]}) is scheduled now.'
                    ),
                    "tag": (
                        f'medicine-{medicine["medicine_id"]}-'
                        f'{today}-{current_time}'
                    ),
                    "url": "/dashboard.html"
                }

                try:
                    send_push(subscription_info, payload)

                    reminder_log_values = (
                        medicine["medicine_id"],
                        today,
                        current_time,
                        endpoint_hash
                    )
                    if MYSQL_URL:
                        cursor.execute("""
                            INSERT IGNORE INTO medicine_reminder_log
                                (medicine_id, dose_date, dose_time, endpoint_hash)
                            VALUES (%s, %s, %s, %s)
                        """, reminder_log_values)
                    else:
                        cursor.execute("""
                            INSERT INTO medicine_reminder_log
                                (medicine_id, dose_date, dose_time, endpoint_hash)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (
                                medicine_id, dose_date, dose_time, endpoint_hash
                            ) DO NOTHING
                        """, reminder_log_values)

                    conn.commit()

                    print(
                        "Medicine reminder sent:",
                        medicine["medicine_name"],
                        current_time
                    )

                except WebPushException as exc:
                    print(
                        "Push failed for medicine",
                        medicine["medicine_id"],
                        exc
                    )
                except Exception as exc:
                    conn.rollback()
                    print("Reminder error:", exc)

    finally:
        cursor.close()
        conn.close()


def reminder_loop():
    """Keep checking for due reminders while the backend is running."""
    print("Medicine reminder scheduler started.")

    while True:
        try:
            check_due_reminders()
        except Exception as exc:
            print("Scheduler check failed:", exc)

        time.sleep(CHECK_INTERVAL_SECONDS)


_scheduler_started = False
_scheduler_lock = threading.Lock()


def start_scheduler():
    """Start the scheduler thread only once in this process."""
    global _scheduler_started

    with _scheduler_lock:
        if _scheduler_started:
            return

        thread = threading.Thread(
            target=reminder_loop,
            name="medicine-reminder-scheduler",
            daemon=True
        )
        thread.start()
        _scheduler_started = True
