#!/usr/bin/env python3
import base64, json, os
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

password = os.environ.get("ICLOUD_APP_PASSWORD", "").encode()
if not password:
    raise SystemExit("ICLOUD_APP_PASSWORD is missing")

out = Path("outreach/secure")
out.mkdir(parents=True, exist_ok=True)
pub_path = out / "public_key.b64"
wrapped_path = out / "wrapped_private_key.json"

if pub_path.exists() and wrapped_path.exists():
    print("Outreach encryption keypair already initialized.")
    raise SystemExit(0)

private_key = x25519.X25519PrivateKey.generate()
public_key = private_key.public_key()

priv_raw = private_key.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption(),
)
pub_raw = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw,
)

salt = os.urandom(16)
nonce = os.urandom(12)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=600000,
)
kek = kdf.derive(password)
wrapped = AESGCM(kek).encrypt(nonce, priv_raw, b"icloud-outreach-private-key-v1")

pub_path.write_text(base64.b64encode(pub_raw).decode() + "\n", encoding="utf-8")
wrapped_path.write_text(json.dumps({
    "version": 1,
    "kdf": "PBKDF2-HMAC-SHA256",
    "iterations": 600000,
    "salt": base64.b64encode(salt).decode(),
    "nonce": base64.b64encode(nonce).decode(),
    "ciphertext": base64.b64encode(wrapped).decode(),
}, indent=2) + "\n", encoding="utf-8")
print("Initialized public encryption key and wrapped private key.")
