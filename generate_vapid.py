
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Generate a VAPID key pair
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# Save the private key securely
with open("backend/vapid_private.pem", "wb") as f:
    f.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    )

# Convert public key to the format required by Web Push
public_numbers = public_key.public_numbers()
public_bytes = (
    b"\x04"
    + public_numbers.x.to_bytes(32, "big")
    + public_numbers.y.to_bytes(32, "big")
)
public_key_b64 = base64.urlsafe_b64encode(public_bytes).rstrip(b"=").decode()

print("VAPID keys generated successfully!")
print("Public key (copy this into your .env file):")
print(public_key_b64)
print("Private key saved to backend/vapid_private.pem")
