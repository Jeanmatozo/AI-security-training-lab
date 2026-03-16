import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone


def compute_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_results(input_file: Path):
    with input_file.open("r", encoding="utf-8") as f:
        results = json.load(f)

    if not isinstance(results, list):
        raise ValueError("Input artifact must contain a top-level JSON array.")

    return results


def detect_category(results: list) -> str:
    if not results:
        return "unknown"

    first_id = str(results[0].get("payload_id", ""))
    if first_id.startswith("PI-"):
        return "prompt-injection"
    if first_id.startswith("RAG-"):
        return "rag-attacks"
    if first_id.startswith("AG-"):
        return "agent-attacks"
    return "unknown"


def next_evidence_id(output_dir: Path, category: str) -> str:
    prefix_map = {
        "prompt-injection": "EVID-PI",
        "rag-attacks": "EVID-RAG",
        "agent-attacks": "EVID-AG",
        "unknown": "EVID-UNK",
    }

    prefix = prefix_map.get(category, "EVID-UNK")
    today = datetime.now(timezone.utc).strftime("%Y%m%d")

    existing = sorted(output_dir.glob(f"{prefix}-{today}-*.md"))
    next_num = len(existing) + 1

    return f"{prefix}-{today}-{next_num:03d}"


def format_json_block(data) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def build_transcript(
    evidence_id: str,
    source_artifact: Path,
    sha256: str,
    category: str,
    results: list,
) -> str:
    promoted_at = datetime.now(timezone.utc).isoformat()

    lines = []
    lines.append("---")
    lines.append(f"evidence_id: {evidence_id}")
    lines.append(f"source_artifact: {source_artifact.name}")
    lines.append(f"sha256: {sha256}")
    lines.append(f"promoted_at: {promoted_at}")
    lines.append(f"category: {category}")
    lines.append("---")
    lines.append("")
    lines.append("# Evidence Transcript")
    lines.append("")

    for item in results:
        payload_id = item.get("payload_id", "UNKNOWN")
        payload_name = item.get("payload_name", "Unnamed payload")
        timestamp = item.get("timestamp", "")
        target_url = item.get("target_url", "")
        status_code = item.get("status_code")
        request_body = item.get("request_body", {})
        response_body = item.get("response_body", {})
        error_text = item.get("error_text")

        lines.append(f"## Payload {payload_id} — {payload_name}")
        lines.append("")
        lines.append(f"**Timestamp:** {timestamp}")
        lines.append(f"**Target:** `{target_url}`")
        lines.append(f"**HTTP Status:** {status_code}")
        lines.append("")

        lines.append("### Request Body")
        lines.append("```json")
        lines.append(format_json_block(request_body))
        lines.append("```")
        lines.append("")

        lines.append("### Response Body")
        lines.append("```json")
        lines.append(format_json_block(response_body))
        lines.append("```")
        lines.append("")

        lines.append("### Error")
        lines.append("```text")
        lines.append("None" if error_text is None else str(error_text))
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Promote raw fuzzer output into signed evidence transcripts."
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
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    input_file = repo_root / args.input
    output_dir = repo_root / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    results = load_results(input_file)
    sha256 = compute_sha256(input_file)
    category = detect_category(results)
    evidence_id = next_evidence_id(output_dir, category)

    transcript = build_transcript(
        evidence_id=evidence_id,
        source_artifact=input_file,
        sha256=sha256,
        category=category,
        results=results,
    )

    output_file = output_dir / f"{evidence_id}.md"
    with output_file.open("w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"Promoted evidence to: {output_file}")


if __name__ == "__main__":
    main()
