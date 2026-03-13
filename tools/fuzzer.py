import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

import requests


def load_payloads(payload_file: Path):
    with payload_file.open("r", encoding="utf-8") as f:
        payloads = json.load(f)

    if not isinstance(payloads, list):
        raise ValueError("payloads.json must contain a top-level JSON array.")

    return payloads


def send_payload(payload: dict) -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()

    target = payload.get("target", {})
    request_data = payload.get("request", {})

    base_url = target.get("base_url", "").rstrip("/")
    endpoint = target.get("endpoint", "")
    method = target.get("method", "POST").upper()

    url = f"{base_url}{endpoint}"
    headers = request_data.get("headers", {})
    body = request_data.get("body", {})

    result = {
        "payload_id": payload.get("id"),
        "payload_name": payload.get("name"),
        "target_environment": target.get("environment"),
        "target_url": url,
        "timestamp": timestamp,
        "request_body": body,
        "status_code": None,
        "response_body": None,
        "error_text": None,
    }

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=body,
            timeout=15,
        )
        result["status_code"] = response.status_code

        try:
            result["response_body"] = response.json()
        except ValueError:
            result["response_body"] = response.text

    except Exception as e:
        result["error_text"] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Run attack payloads against a target environment."
    )
    parser.add_argument(
        "--payloads",
        required=True,
        help="Path to payloads.json relative to repo root",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    payload_file = repo_root / args.payloads
    output_dir = repo_root / "artifacts" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    payloads = load_payloads(payload_file)

    results = []
    for payload in payloads:
        results.append(send_payload(payload))

    output_file = output_dir / f"fuzz_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Saved results to: {output_file}")


if __name__ == "__main__":
    main()