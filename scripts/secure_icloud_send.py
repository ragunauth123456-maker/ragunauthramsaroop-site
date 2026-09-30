#!/usr/bin/env python3
import base64, json, os, smtplib, ssl, sys
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

from send_icloud_smtp import build_cv_pdf, CV_SOURCE

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SMTP_HOST="smtp.mail.me.com"
SMTP_PORT=587
SENDER="ragunauthramsaroop@icloud.com"
SENDER_NAME="Ragunauth Ramsaroop"
WRAPPED_KEY=Path("outreach/secure/wrapped_private_key.json")
CV_PDF=Path("/tmp/Ragunauth_Ramsaroop_Executive_CV_2026.pdf")

def b64(s): return base64.b64decode(s)

def unwrap_private(password: bytes):
    obj=json.loads(WRAPPED_KEY.read_text(encoding="utf-8"))
    kdf=PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b64(obj["salt"]),
        iterations=int(obj["iterations"]),
    )
    kek=kdf.derive(password)
    raw=AESGCM(kek).decrypt(
        b64(obj["nonce"]),
        b64(obj["ciphertext"]),
        b"icloud-outreach-private-key-v1",
    )
    return x25519.X25519PrivateKey.from_private_bytes(raw)

def decrypt_payload(path: Path, private_key):
    obj=json.loads(path.read_text(encoding="utf-8"))
    eph=x25519.X25519PublicKey.from_public_bytes(b64(obj["ephemeral_public"]))
    shared=private_key.exchange(eph)
    key=HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b64(obj["salt"]),
        info=b"icloud-outreach-payload-v1",
    ).derive(shared)
    clear=AESGCM(key).decrypt(
        b64(obj["nonce"]),
        b64(obj["ciphertext"]),
        b"icloud-outreach-payload-v1",
    )
    payload=json.loads(clear.decode())
    messages=payload.get("messages")
    if not isinstance(messages,list) or not messages or len(messages)>10:
        raise ValueError("Payload must contain 1 to 10 messages.")
    return payload

def attach_cv(msg: EmailMessage):
    if not CV_PDF.exists():
        build_cv_pdf(CV_SOURCE, CV_PDF)
    msg.add_attachment(CV_PDF.read_bytes(), maintype="application", subtype="pdf",
                       filename="Ragunauth_Ramsaroop_Executive_CV_2026.pdf")

def send(payload, password):
    ctx=ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST,SMTP_PORT,timeout=30) as server:
        server.ehlo()
        server.starttls(context=ctx)
        server.ehlo()
        server.login(SENDER,password.decode())
        for item in payload["messages"]:
            to=item["to"].strip()
            subject=item["subject"].strip()
            body=item["body"].strip()
            if "@" not in to or not subject or not body:
                raise ValueError("Invalid recipient, subject, or body.")
            msg=EmailMessage()
            msg["From"]=formataddr((SENDER_NAME,SENDER))
            msg["To"]=to
            msg["Subject"]=subject
            msg["Reply-To"]=SENDER
            msg.set_content(body)
            attach_cv(msg)
            server.send_message(msg, from_addr=SENDER, to_addrs=[to])
            print("Sent secure iCloud outreach message.")

def main():
    if len(sys.argv)!=2:
        raise SystemExit("Usage: secure_icloud_send.py <encrypted_payload.json>")
    password=os.environ.get("ICLOUD_APP_PASSWORD","").encode()
    if not password:
        raise SystemExit("ICLOUD_APP_PASSWORD is missing")
    private_key=unwrap_private(password)
    payload=decrypt_payload(Path(sys.argv[1]), private_key)
    send(payload,password)

if __name__=="__main__":
    main()
