
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    mobile = data.get("mobile_number", "").strip()
    password = data.get("password", "")

    if not all([name, email, mobile, password]):
        return jsonify({"error": "All fields are required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """INSERT INTO user_login_details
               (full_name, email, mobile_number, password_hash)
               VALUES (%s, %s, %s, %s)""",
            (name, email, mobile, generate_password_hash(password))
        )
        conn.commit()
        return jsonify({"message": "Registration successful"}), 201

    except Exception as error:
        conn.rollback()
        if getattr(error, "errno", None) == 1062:
            return jsonify({"error": "Email already registered"}), 409
        return jsonify({"error": "Could not register user"}), 500

    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """SELECT user_id, full_name, email, password_hash
               FROM user_login_details WHERE email = %s""",
            (email,)
        )
        user = cursor.fetchone()

        if not user or not check_password_hash(
            user["password_hash"], password
        ):
            return jsonify({"error": "Invalid email or password"}), 401

        session.clear()
        session["user_id"] = user["user_id"]

        return jsonify({
            "message": "Login successful",
            "user": {
                "user_id": user["user_id"],
                "full_name": user["full_name"],
                "email": user["email"]
            }
        }), 200

    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"error": "Please log in"}), 401

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """SELECT user_id, full_name, email, mobile_number
               FROM user_login_details WHERE user_id = %s""",
            (session["user_id"],)
        )
        user = cursor.fetchone()

        if not user:
            session.clear()
            return jsonify({"error": "User not found"}), 404

        return jsonify({"user": user}), 200

    finally:
        cursor.close()
        conn.close()
