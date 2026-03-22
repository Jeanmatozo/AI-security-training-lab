import argparse
import base64
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------

def compute_sha256_file(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


# ---------------------------------------------------------------------------
# Signing helpers
# ---------------------------------------------------------------------------

def load_ed25519_private_key(key_path: Path) -> Ed25519PrivateKey:
    with key_path.open("rb") as f:
        key_bytes = f.read()

    key = serialization.load_pem_private_key(key_bytes, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("Signing key must be an Ed25519 private key in PEM format.")
    return key


def derive_public_key(private_key: Ed25519PrivateKey) -> Ed25519PublicKey:
    return private_key.public_key()


def public_key_fingerprint_sha256(public_key: Ed25519PublicKey) -> str:
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return compute_sha256_bytes(public_bytes)


def sign_bytes(private_key: Ed25519PrivateKey, data: bytes) -> str:
    signature = private_key.sign(data)
    return base64.b64encode(signature).decode("ascii")


def write_signature_sidecar(
    sidecar_path: Path,
    *,
    evidence_id: str,
    transcript_file: str,
    transcript_sha256: str,
    source_artifact: str,
    source_sha256: str,
    category: str,
    promoted_at: str,
    signature_b64: str,
    public_key_sha256: str,
) -> None:
    payload = {
        "evidence_id": evidence_id,
        "transcript_file": transcript_file,
        "transcript_sha256": transcript_sha256,
        "source_artifact": source_artifact,
        "source_sha256": source_sha256,
        "category": category,
        "promoted_at": promoted_at,
        "signature_algorithm": "Ed25519",
        "signed_at": datetime.now(timezone.utc).isoformat(),
        "public_key_sha256": public_key_sha256,
        "signature_base64": signature_b64,
        "signed_content": "transcript_file_bytes",
    }

    with sidecar_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Signature sidecar  : {sidecar_path}")


# ---------------------------------------------------------------------------
# Result loading
# ---------------------------------------------------------------------------

def load_results(input_file: Path) -> list:
    with input_file.open("r", encoding="utf-8") as f:
        results = json.load(f)
    if not isinstance(results, list):
        raise ValueError("Input artifact must contain a top-level JSON array.")
    return results


# ---------------------------------------------------------------------------
# Category detection
# ---------------------------------------------------------------------------

def detect_category(results: list) -> str:
    if not results:
        return "unknown"

    payload_ids = [str(item.get("payload_id", "")).strip().upper() for item in results]

    has_pi = any(pid.startswith("PI-") for pid in payload_ids)
    has_rag = any(pid.startswith("RAG-") for pid in payload_ids)
    has_ag = any(pid.startswith("AG-") for pid in payload_ids)

    matched = sum([has_pi, has_rag, has_ag])

    if matched == 0:
        return "unknown"
    if matched > 1:
        raise ValueError(f"Mixed payload categories found in artifact: {payload_ids}")
    if has_pi:
        return "prompt-injection"
    if has_rag:
        return "rag-attacks"
    if has_ag:
        return "agent-attacks"
    return "unknown"


# ---------------------------------------------------------------------------
# Evidence ID sequencing
# ---------------------------------------------------------------------------

def next_evidence_id(output_dir: Path, category: str) -> str:
    prefix_map = {
        "prompt-injection": "PI",
        "rag-attacks": "RAG",
        "agent-attacks": "AG",
        "unknown": "UNK",
    }
    prefix = prefix_map.get(category, "UNK")
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    existing = sorted(output_dir.glob(f"{prefix}-{today}-*.md"))
    next_num = len(existing) + 1
    return f"{prefix}-{today}-{next_num:03d}"


# ---------------------------------------------------------------------------
# Verdict helpers
# ---------------------------------------------------------------------------

VERDICT_EMOJI = {
    "VULNERABLE": "🔴",
    "VETOED": "🟡",
    "SAFE": "🟢",
    "ERROR": "⚪",
}


def verdict_label(verdict: str) -> str:
    emoji = VERDICT_EMOJI.get(verdict, "⚪")
    return f"{emoji} {verdict}"


def build_verdict_summary(results: list) -> list[str]:
    counts = {"VULNERABLE": 0, "VETOED": 0, "SAFE": 0, "ERROR": 0}
    for r in results:
        v = r.get("verdict", "ERROR")
        counts[v] = counts.get(v, 0) + 1

    lines = []
    lines.append("## Verdict Summary")
    lines.append("")
    lines.append("| Payload ID | Name | Severity | Verdict |")
    lines.append("|---|---|---|---|")
    for r in results:
        pid = r.get("payload_id", "UNKNOWN")
        name = r.get("payload_name", "—")
        severity = r.get("severity", "—")
        verdict = r.get("verdict", "ERROR")
        lines.append(f"| `{pid}` | {name} | {severity} | {verdict_label(verdict)} |")
    lines.append("")
    lines.append("**Totals:**")
    lines.append("")
    for v, count in counts.items():
        lines.append(f"- {verdict_label(v)}: {count}")
    lines.append("")
    return lines


# ---------------------------------------------------------------------------
# Transcript builder
# ---------------------------------------------------------------------------

def format_json_block(data) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def build_transcript(
    evidence_id: str,
    source_artifact: Path,
    source_sha256: str,
    category: str,
    results: list,
    signature_sidecar_name: str | None = None,
    public_key_sha256: str | None = None,
) -> str:
    promoted_at = datetime.now(timezone.utc).isoformat()

    lines = []

    # --- Frontmatter ---
    lines.append("---")
    lines.append(f"evidence_id: {evidence_id}")
    lines.append(f"source_artifact: {source_artifact.name}")
    lines.append(f"source_sha256: {source_sha256}")
    lines.append(f"promoted_at: {promoted_at}")
    lines.append(f"category: {category}")
    if signature_sidecar_name:
        lines.append(f"signature_sidecar: {signature_sidecar_name}")
        lines.append("signature_algorithm: Ed25519")
        if public_key_sha256:
            lines.append(f"public_key_sha256: {public_key_sha256}")
    else:
        lines.append("signature_sidecar: UNSIGNED")
        lines.append("signature_algorithm: UNSIGNED")
    lines.append("---")
    lines.append("")
    lines.append(f"# Evidence Transcript — {evidence_id}")
    lines.append("")
    lines.append("> **Tamper-evident record.**")
    lines.append("> - `source_sha256` covers the raw fuzzer JSON artifact.")
    lines.append("> - The final transcript file SHA-256 is stored in `MANIFEST.json`.")
    if signature_sidecar_name:
        lines.append(f"> - The detached signature is stored in `{signature_sidecar_name}`.")
    lines.append("> Any modification to the transcript file will invalidate verification.")
    lines.append("")

    # --- Verdict summary table ---
    lines.extend(build_verdict_summary(results))
    lines.append("---")
    lines.append("")
    lines.append("## Payload Detail")
    lines.append("")

    # --- Per-payload detail ---
    for item in results:
        payload_id = item.get("payload_id", "UNKNOWN")
        payload_name = item.get("payload_name", "Unnamed payload")
        timestamp = item.get("timestamp", "")
        target_url = item.get("target_url", "")
        status_code = item.get("status_code")
        severity = item.get("severity", "—")
        attack_type = item.get("attack_type", "—")
        request_body = item.get("request_body", {})
        response_body = item.get("response_body", {})
        error_text = item.get("error_text")
        verdict = item.get("verdict", "ERROR")
        matched_any = item.get("matched_any", [])
        matched_none = item.get("matched_none", [])
        regex_hit = item.get("regex_matched", False)

        lines.append(f"### {payload_id} — {payload_name}")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|---|---|")
        lines.append(f"| **Verdict** | {verdict_label(verdict)} |")
        lines.append(f"| **Severity** | {severity} |")
        lines.append(f"| **Attack type** | {attack_type} |")
        lines.append(f"| **Timestamp** | {timestamp} |")
        lines.append(f"| **Target** | `{target_url}` |")
        lines.append(f"| **HTTP status** | {status_code} |")
        lines.append(f"| **match\\_any hits** | {matched_any if matched_any else '—'} |")
        lines.append(f"| **match\\_none hits** | {matched_none if matched_none else '—'} |")
        lines.append(f"| **regex matched** | {regex_hit} |")
        lines.append("")

        lines.append("#### Request Body")
        lines.append("```json")
        lines.append(format_json_block(request_body))
        lines.append("```")
        lines.append("")

        lines.append("#### Response Body")
        lines.append("```json")
        lines.append(format_json_block(response_body))
        lines.append("```")
        lines.append("")

        if error_text:
            lines.append("#### Error")
            lines.append("```text")
            lines.append(str(error_text))
            lines.append("```")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Manifest updater
# ---------------------------------------------------------------------------

def update_manifest(
    output_dir: Path,
    *,
    evidence_id: str,
    transcript_file: str,
    transcript_sha256: str,
    source_artifact: str,
    source_sha256: str,
    category: str,
    promoted_at: str,
    results: list,
    signature_file: str | None = None,
    signature_algorithm: str | None = None,
    public_key_sha256: str | None = None,
) -> None:
    manifest_path = output_dir / "MANIFEST.json"

    manifest = []
    if manifest_path.exists():
        with manifest_path.open("r", encoding="utf-8") as f:
            try:
                manifest = json.load(f)
            except json.JSONDecodeError:
                manifest = []

    counts = {"VULNERABLE": 0, "VETOED": 0, "SAFE": 0, "ERROR": 0}
    for r in results:
        v = r.get("verdict", "ERROR")
        counts[v] = counts.get(v, 0) + 1

    entry = {
        "evidence_id": evidence_id,
        "transcript_file": transcript_file,
        "transcript_sha256": transcript_sha256,
        "source_artifact": source_artifact,
        "source_sha256": source_sha256,
        "category": category,
        "promoted_at": promoted_at,
        "payload_count": len(results),
        "verdicts": counts,
        "signature_file": signature_file,
        "signature_algorithm": signature_algorithm,
        "public_key_sha256": public_key_sha256,
    }

    manifest = [e for e in manifest if e.get("evidence_id") != evidence_id]
    manifest.append(entry)

    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Manifest updated   : {manifest_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Promote raw fuzzer output into tamper-evident evidence transcripts."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to raw artifact JSON relative to repo root",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to evidence transcript directory relative to repo root",
    )
    parser.add_argument(
        "--signing-key",
        required=False,
        help="Optional path to Ed25519 private key PEM relative to repo root",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    input_file = repo_root / args.input
    output_dir = repo_root / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    results = load_results(input_file)
    source_sha256 = compute_sha256_file(input_file)
    category = detect_category(results)
    promoted_at = datetime.now(timezone.utc).isoformat()

    print(f"Detected category  : {category}")
    print(f"Source SHA-256     : {source_sha256}")

    evidence_id = next_evidence_id(output_dir, category)

    signing_enabled = bool(args.signing_key)
    private_key = None
    public_key_sha256 = None
    signature_sidecar_name = None

    if signing_enabled:
        signing_key_path = repo_root / args.signing_key
        private_key = load_ed25519_private_key(signing_key_path)
        public_key = derive_public_key(private_key)
        public_key_sha256 = public_key_fingerprint_sha256(public_key)
        signature_sidecar_name = f"{evidence_id}.sig.json"
        print(f"Signing enabled    : yes")
        print(f"Public key SHA-256 : {public_key_sha256}")
    else:
        print("Signing enabled    : no")

    transcript = build_transcript(
        evidence_id=evidence_id,
        source_artifact=input_file,
        source_sha256=source_sha256,
        category=category,
        results=results,
        signature_sidecar_name=signature_sidecar_name,
        public_key_sha256=public_key_sha256,
    )

    output_file = output_dir / f"{evidence_id}.md"
    with output_file.open("w", encoding="utf-8", newline="\n") as f:
        f.write(transcript)

    transcript_sha256 = compute_sha256_file(output_file)
    print(f"Transcript SHA-256 : {transcript_sha256}")
    print(f"Promoted evidence  : {output_file}")

    signature_file = None
    signature_algorithm = None

    if signing_enabled and private_key is not None:
        transcript_bytes = output_file.read_bytes()
        signature_b64 = sign_bytes(private_key, transcript_bytes)

        sidecar_path = output_dir / signature_sidecar_name
        write_signature_sidecar(
            sidecar_path,
            evidence_id=evidence_id,
            transcript_file=output_file.name,
            transcript_sha256=transcript_sha256,
            source_artifact=input_file.name,
            source_sha256=source_sha256,
            category=category,
            promoted_at=promoted_at,
            signature_b64=signature_b64,
            public_key_sha256=public_key_sha256,
        )

        signature_file = sidecar_path.name
        signature_algorithm = "Ed25519"

    update_manifest(
        output_dir=output_dir,
        evidence_id=evidence_id,
        transcript_file=output_file.name,
        transcript_sha256=transcript_sha256,
        source_artifact=input_file.name,
        source_sha256=source_sha256,
        category=category,
        promoted_at=promoted_at,
        results=results,
        signature_file=signature_file,
        signature_algorithm=signature_algorithm,
        public_key_sha256=public_key_sha256,
    )


if __name__ == "__main__":
    main()