
import json

from flask import Blueprint, jsonify, request, session
from pywebpush import WebPushException

from db import get_connection
from push_utils import get_vapid_public_key, send_push

push_bp = Blueprint("push", __name__)


@push_bp.route("/public-key", methods=["GET"])
def public_key():
    key = get_vapid_public_key()
    if not key:
        return jsonify({"error": "VAPID public key is not configured"}), 500
    return jsonify({"publicKey": key})


@push_bp.route("/subscribe", methods=["POST"])
def subscribe():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    data = request.get_json(silent=True) or {}
    sub = data.get("subscription", {})
    keys = sub.get("keys", {})
    endpoint = sub.get("endpoint")
    p256dh = keys.get("p256dh")
    auth = keys.get("auth")

    if not all([endpoint, p256dh, auth]):
        return jsonify({"error": "Invalid push subscription"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id FROM push_subscriptions
            WHERE user_id = %s AND endpoint = %s
            """,
            (user_id, endpoint),
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE push_subscriptions
                SET p256dh = %s, auth = %s
                WHERE id = %s
                """,
                (p256dh, auth, existing[0]),
            )
        else:
            cursor.execute(
                """
                INSERT INTO push_subscriptions
                    (user_id, endpoint, p256dh, auth)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, endpoint, p256dh, auth),
            )

        conn.commit()
        return jsonify({"message": "Push subscription saved"}), 201
    finally:
        cursor.close()
        conn.close()


@push_bp.route("/test", methods=["POST"])
def test_push():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT endpoint, p256dh, auth
            FROM push_subscriptions
            WHERE user_id = %s
            """,
            (user_id,),
        )
        subscriptions = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not subscriptions:
        return jsonify({"error": "Enable push notifications first"}), 400

    sent = 0
    for sub in subscriptions:
        subscription_info = {
            "endpoint": sub["endpoint"],
            "keys": {
                "p256dh": sub["p256dh"],
                "auth": sub["auth"],
            },
        }
        try:
            send_push(
                subscription_info,
                {
                    "title": "Smart Medical Box",
                    "body": "Test notification received successfully!",
                    "url": "/dashboard.html",
                },
            )
            sent += 1
        except WebPushException as exc:
            print("Test push failed:", exc)

    if sent:
        return jsonify({"message": "Test notification sent"})
    return jsonify({"error": "Could not send test notification"}), 502
