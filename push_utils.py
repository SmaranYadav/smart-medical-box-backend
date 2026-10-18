
import os
import json
from pathlib import Path
import tempfile

from dotenv import load_dotenv
from pywebpush import webpush

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")


def get_vapid_public_key():
    return os.getenv("VAPID_PUBLIC_KEY")


def get_vapid_private_key_path():
    private_key = os.getenv("VAPID_PRIVATE_KEY")
    if private_key:
        path = Path(tempfile.gettempdir()) / (
            f"smart-medical-box-vapid-{os.getpid()}.pem"
        )
        if not path.exists():
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as key_file:
                key_file.write(private_key.replace("\\n", "\n"))
        return str(path)

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
