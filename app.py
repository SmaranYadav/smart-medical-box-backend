import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from routes.push import push_bp
from routes.auth import auth_bp
from routes.medicines import medicines_bp
from scheduler import start_scheduler
# Load environment variables from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY is missing. Add it to backend/.env")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False
)

CORS(
    app,
    origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501"
    ],
    supports_credentials=True
)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(medicines_bp, url_prefix="/api/medicines")
app.register_blueprint(push_bp, url_prefix="/api/push")

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Smart Medical Box API is running"
    }), 200


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "success",
        "message": "Smart Medical Box backend is running"
    }), 200


if __name__ == "__main__":
    start_scheduler()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )