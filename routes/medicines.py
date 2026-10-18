import json
from datetime import date, time as datetime_time

from flask import Blueprint, request, jsonify, session
from db import get_connection

medicines_bp = Blueprint("medicines", __name__)


def get_user_id():
    return session.get("user_id")


def get_medicine_for_user(cursor, medicine_id, user_id):
    cursor.execute(
        """
        SELECT medicine_id, user_id, medicine_name, dosage,
               frequency, dose_times, start_date, end_date,
               instructions, status, created_at
        FROM user_medicine_track_details
        WHERE medicine_id = %s
          AND user_id = %s
          AND status != 'Deleted'
        """,
        (medicine_id, user_id)
    )
    return cursor.fetchone()


def serialize_medicine(row):
    if not row:
        return None

    for field in ("start_date", "end_date", "created_at"):
        if row.get(field):
            row[field] = row[field].isoformat()

    if isinstance(row.get("dose_times"), str):
        try:
            row["dose_times"] = json.loads(row["dose_times"])
        except (ValueError, TypeError):
            row["dose_times"] = []

    return row


@medicines_bp.route("", methods=["GET"])
def list_medicines():
    user_id = get_user_id()

    if not user_id:
        return jsonify({"error": "Please log in"}), 401

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT medicine_id, user_id, medicine_name, dosage,
                   frequency, dose_times, start_date, end_date,
                   instructions, status, created_at
            FROM user_medicine_track_details
            WHERE user_id = %s AND status != 'Deleted'
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

        medicines = [
            serialize_medicine(row)
            for row in cursor.fetchall()
        ]

        return jsonify({"medicines": medicines}), 200

    finally:
        cursor.close()
        conn.close()


@medicines_bp.route("", methods=["POST"])
def add_medicine():
    user_id = get_user_id()

    if not user_id:
        return jsonify({"error": "Please log in"}), 401

    data = request.get_json(silent=True) or {}

    name = str(data.get("medicine_name", "")).strip()
    dosage = str(data.get("dosage", "")).strip()
    instructions = str(data.get("instructions", "")).strip()
    times = data.get("dose_times")
    frequency = data.get("frequency")

    if not name or not dosage:
        return jsonify({
            "error": "Medicine name and dosage are required"
        }), 400

    if len(name) > 150 or len(dosage) > 100:
        return jsonify({
            "error": "Medicine name or dosage is too long"
        }), 400

    if not isinstance(times, list) or not times:
        return jsonify({
            "error": "Add at least one dose time"
        }), 400

    try:
        frequency = int(frequency)
        start_date = date.fromisoformat(data.get("start_date", ""))
        end_date = date.fromisoformat(data.get("end_date", ""))
    except (ValueError, TypeError):
        return jsonify({
            "error": "Enter valid dates and frequency"
        }), 400

    if frequency < 1 or frequency > 4 or len(times) != frequency:
        return jsonify({
            "error": "The number of dose times must match the daily frequency (1–4)"
        }), 400

    for dose_time in times:
        if not isinstance(dose_time, str):
            return jsonify({
                "error": "Dose times must use HH:MM format"
            }), 400

        try:
            parsed_time = datetime_time.fromisoformat(dose_time)
            if len(dose_time) != 5 or parsed_time.second != 0:
                raise ValueError
        except ValueError:
            return jsonify({
                "error": "Use valid dose times, for example 09:00 or 21:00"
            }), 400

    if len(set(times)) != len(times):
        return jsonify({
            "error": "Dose times must be different"
        }), 400

    if end_date < start_date:
        return jsonify({
            "error": "End date cannot be before start date"
        }), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO user_medicine_track_details
                (user_id, medicine_name, dosage, frequency,
                 dose_times, start_date, end_date, instructions, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Active')
            """,
            (
                user_id,
                name,
                dosage,
                frequency,
                json.dumps(times),
                start_date,
                end_date,
                instructions
            )
        )

        conn.commit()

        return jsonify({
            "message": "Medicine added successfully",
            "medicine_id": cursor.lastrowid
        }), 201

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


@medicines_bp.route("/<int:medicine_id>", methods=["PATCH"])
def update_medicine(medicine_id):
    user_id = get_user_id()

    if not user_id:
        return jsonify({"error": "Please log in"}), 401

    data = request.get_json(silent=True) or {}

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        medicine = get_medicine_for_user(cursor, medicine_id, user_id)

        if not medicine:
            return jsonify({"error": "Medicine not found"}), 404

        if data.get("action") == "complete":
            cursor.execute(
                """
                UPDATE user_medicine_track_details
                SET status = 'Completed'
                WHERE medicine_id = %s AND user_id = %s
                """,
                (medicine_id, user_id)
            )

        elif data.get("action") == "extend":
            try:
                new_end_date = date.fromisoformat(
                    data.get("end_date", "")
                )
            except (ValueError, TypeError):
                return jsonify({
                    "error": "Enter a valid new end date"
                }), 400

            if new_end_date <= medicine["end_date"]:
                return jsonify({
                    "error": "New end date must be after the current end date"
                }), 400

            cursor.execute(
                """
                UPDATE user_medicine_track_details
                SET end_date = %s, status = 'Active'
                WHERE medicine_id = %s AND user_id = %s
                """,
                (new_end_date, medicine_id, user_id)
            )

        else:
            return jsonify({"error": "Unknown update action"}), 400

        conn.commit()

        return jsonify({
            "message": "Medicine updated successfully"
        }), 200

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


@medicines_bp.route("/<int:medicine_id>", methods=["DELETE"])
def delete_medicine(medicine_id):
    user_id = get_user_id()

    if not user_id:
        return jsonify({"error": "Please log in"}), 401

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE user_medicine_track_details
            SET status = 'Deleted'
            WHERE medicine_id = %s
              AND user_id = %s
              AND status != 'Deleted'
            """,
            (medicine_id, user_id)
        )

        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({"error": "Medicine not found"}), 404

        conn.commit()

        return jsonify({
            "message": "Medicine deleted successfully"
        }), 200

    finally:
        cursor.close()
        conn.close()