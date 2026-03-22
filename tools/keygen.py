"""
keygen.py — Generate an Ed25519 keypair for evidence signing.

Usage:
    python tools/keygen.py --out keys/

Outputs:
    keys/signing_key.pem         Ed25519 private key (keep secret, never commit)
    keys/signing_key.pub.pem     Ed25519 public key  (safe to commit)
    keys/signing_key.pub.sha256  SHA-256 fingerprint of raw public key bytes
"""

import argparse
import hashlib
import os
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def main():
    parser = argparse.ArgumentParser(
        description="Generate an Ed25519 keypair for evidence signing."
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Directory to write keys into (relative to repo root)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    priv_path = out_dir / "signing_key.pem"
    pub_path = out_dir / "signing_key.pub.pem"
    fingerprint_path = out_dir / "signing_key.pub.sha256"

    for p in (priv_path, pub_path, fingerprint_path):
        if p.exists():
            print(f"ERROR: {p} already exists. Delete it manually to regenerate.")
            raise SystemExit(1)

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    raw_pub = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    fingerprint = hashlib.sha256(raw_pub).hexdigest()

    priv_path.write_bytes(priv_bytes)
    try:
        os.chmod(priv_path, 0o600)
    except OSError:
        pass

    pub_path.write_bytes(pub_bytes)
    fingerprint_path.write_text(fingerprint + "\n", encoding="utf-8")

    print(f"Private key      : {priv_path}")
    print(f"Public key       : {pub_path}")
    print(f"Fingerprint      : {fingerprint}")
    print(f"Fingerprint file : {fingerprint_path}")
    print()
    print("IMPORTANT: Add the private key path to .gitignore and never commit it.")
    print("           The public key and fingerprint file are safe to commit.")


if __name__ == "__main__":
    main()