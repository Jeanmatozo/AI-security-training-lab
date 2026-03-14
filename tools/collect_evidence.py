from __future__ import annotations

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

RESULTS_DIR = Path("artifacts/results")
TRANSCRIPTS_DIR = Path("evidence/transcripts")


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def candidate_result_files() -> list[Path]:
    if not RESULTS_DIR.exists():
        raise RuntimeError("artifacts/results/ does not exist.")

    files = [p for p in RESULTS_DIR.glob("*.json") if p.is_file()]
    files = [p for p in files if p.stat().st_size > 0]

    if not files:
        raise RuntimeError("No non-empty JSON result files found in artifacts/results/")

    files.sort(key=lambda p: p.stat().st_mtime)
    return files


def load_results_file(path: Path):
    encodings_to_try = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
    last_error = None

    for enc in encodings_to_try:
        try:
            with path.open("r", encoding=enc) as f:
                content = f.read()

            if not content.strip():
                raise RuntimeError(f"Results file is empty: {path}")

            data = json.loads(content)

            if not isinstance(data, list):
                raise RuntimeError(f"Expected top-level JSON array in: {path}")

            return data

        except Exception as e:
            last_error = e

    raise RuntimeError(f"Could not parse JSON results file {path}: {last_error}")


def load_latest_results():
    files = candidate_result_files()

    # Try newest to oldest until one parses correctly
    for path in reversed(files):
        try:
            results = load_results_file(path)
            return path, results
        except Exception:
            continue

    raise RuntimeError(
        "No valid JSON results file could be parsed from artifacts/results/"
    )


def next_evidence_id() -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(TRANSCRIPTS_DIR.glob(f"EVID-PI-{today}-*.md"))
    num = len(existing) + 1
    return f"EVID-PI-{today}-{num:03d}"


def main() -> None:
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    source_file, results = load_latest_results()

    sha256 = sha256_of_file(source_file)
    evidence_id = next_evidence_id()
    promoted_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    output_path = TRANSCRIPTS_DIR / f"{evidence_id}.md"

    with output_path.open("w", encoding="utf-8") as out:
        out.write("---\n")
        out.write(f"evidence_id: {evidence_id}\n")
        out.write(f"source_artifact: {source_file.name}\n")
        out.write(f"sha256: {sha256}\n")
        out.write(f"promoted_at: {promoted_at}\n")
        out.write("category: prompt-injection\n")
        out.write("---\n\n")

        out.write("# Evidence Transcript\n\n")

        for r in results:
            out.write(f"## Payload {r.get('payload_id', 'UNKNOWN')} — {r.get('payload_name', 'UNKNOWN')}\n\n")
            out.write(f"**Timestamp:** {r.get('timestamp')}\n")
            out.write(f"**Target Environment:** {r.get('target_environment')}\n")
            out.write(f"**Target:** {r.get('target_url')}\n")
            out.write(f"**HTTP Status:** {r.get('status_code')}\n\n")

            out.write("### Request Body\n")
            out.write("```json\n")
            out.write(json.dumps(r.get("request_body"), indent=2, ensure_ascii=False))
            out.write("\n```\n\n")

            out.write("### Response Body\n")
            out.write("```json\n")
            out.write(json.dumps(r.get("response_body"), indent=2, ensure_ascii=False))
            out.write("\n```\n\n")

            out.write("### Error\n")
            out.write("```text\n")
            out.write(str(r.get("error_text")))
            out.write("\n```\n\n")

    print(f"[+] Source artifact: {source_file}")
    print(f"[+] Evidence ID: {evidence_id}")
    print(f"[+] Transcript written: {output_path}")


if __name__ == "__main__":
    main()