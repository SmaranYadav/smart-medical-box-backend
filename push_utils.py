
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from pywebpush import webpush

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")


def get_vapid_public_key():
    return os.getenv("VAPID_PUBLIC_KEY")


def get_vapid_private_key_path():
    path = os.getenv("VAPID_PRIVATE_KEY_PATH", "vapid_private.pem")
    return str(BACKEND_DIR / path)


def send_push(subscription, payload):
    private_key_path = get_vapid_private_key_path()

    if not os.path.exists(private_key_path):
        raise FileNotFoundError(
            f"VAPID private key not found: {private_key_path}"
        )

    return webpush(
        subscription_info=subscription,
        data=json.dumps(payload),
        vapid_private_key=private_key_path,
        vapid_claims={
            "sub": os.getenv(
                "VAPID_SUBJECT",
                "mailto:your-email@example.com"
            )
        },
    )
