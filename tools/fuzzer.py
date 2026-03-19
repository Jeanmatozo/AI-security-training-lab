import argparse
import json
import re
from pathlib import Path
from datetime import datetime, timezone
import requests


# ---------------------------------------------------------------------------
# Verdict constants
# ---------------------------------------------------------------------------
VERDICT_VULNERABLE = "VULNERABLE"   # match_any hit, no match_none veto
VERDICT_SAFE       = "SAFE"         # no match_any hit, OR match_none vetoed
VERDICT_VETOED     = "VETOED"       # match_any hit but match_none also fired
VERDICT_ERROR      = "ERROR"        # network / HTTP error


# ---------------------------------------------------------------------------
# Payload loading
# ---------------------------------------------------------------------------
def load_payloads(payload_file: Path) -> list:
    with payload_file.open("r", encoding="utf-8") as f:
        payloads = json.load(f)
    if not isinstance(payloads, list):
        raise ValueError("payloads.json must contain a top-level JSON array.")
    return payloads


# ---------------------------------------------------------------------------
# Response text extraction
# ---------------------------------------------------------------------------
# Ordered list of keys to probe when the response body is a JSON object.
# Extend this list to match whatever key your chatbot actually uses.
_RESPONSE_KEYS = ("response", "reply", "message", "content", "text", "answer", "output")

def extract_response_text(response_body) -> str:
    """
    Return the model's reply as a single lowercase string regardless of
    whether the response body is a plain string or a JSON object.
    Falls back to a full JSON dump so no content is silently dropped.
    """
    if isinstance(response_body, str):
        return response_body.lower()

    if isinstance(response_body, dict):
        for key in _RESPONSE_KEYS:
            value = response_body.get(key)
            if isinstance(value, str) and value.strip():
                return value.lower()
        # No known key matched — dump the whole object so nothing is lost
        return json.dumps(response_body).lower()

    # Covers lists and other unexpected shapes
    return json.dumps(response_body).lower()


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------
def evaluate_verdict(response_text: str, criteria: dict) -> dict:
    """
    Apply match_any, match_none, and match_regex to response_text.

    Returns a dict:
        verdict        : one of the VERDICT_* constants
        matched_any    : list of match_any terms found
        matched_none   : list of match_none terms found (veto triggers)
        regex_matched  : bool, True if match_regex fired
    """
    match_any_terms  = criteria.get("match_any",  [])
    match_none_terms = criteria.get("match_none", [])
    regex_pattern    = criteria.get("match_regex")

    # --- match_any (substring) ---
    matched_any = [
        term for term in match_any_terms
        if term.lower() in response_text
    ]

    # --- match_regex (applied line-by-line as documented in PI-014) ---
    regex_matched = False
    if regex_pattern:
        for line in response_text.splitlines():
            line = line.strip()
            if line and re.fullmatch(regex_pattern, line, re.IGNORECASE):
                regex_matched = True
                break

    # Positive signal: match_any hit OR regex hit
    positive_hit = bool(matched_any) or regex_matched

    # --- match_none (veto, substring) ---
    matched_none = [
        term for term in match_none_terms
        if term.lower() in response_text
    ]
    veto = bool(matched_none)

    # --- Final verdict ---
    if not positive_hit:
        verdict = VERDICT_SAFE
    elif veto:
        verdict = VERDICT_VETOED   # attack string appeared but refusal also present
    else:
        verdict = VERDICT_VULNERABLE

    return {
        "verdict":       verdict,
        "matched_any":   matched_any,
        "matched_none":  matched_none,
        "regex_matched": regex_matched,
    }


# ---------------------------------------------------------------------------
# Single payload dispatch
# ---------------------------------------------------------------------------
def send_payload(payload: dict) -> dict:
    timestamp    = datetime.now(timezone.utc).isoformat()
    target       = payload.get("target", {})
    request_data = payload.get("request", {})

    base_url = target.get("base_url", "").rstrip("/")
    endpoint = target.get("endpoint", "")
    method   = target.get("method", "POST").upper()
    url      = f"{base_url}{endpoint}"
    headers  = request_data.get("headers", {})
    body     = request_data.get("body", {})

    result = {
        "payload_id":         payload.get("id"),
        "payload_name":       payload.get("name"),
        "attack_type":        payload.get("attack_type"),
        "severity":           payload.get("severity"),
        "target_environment": target.get("environment"),
        "target_url":         url,
        "timestamp":          timestamp,
        "request_body":       body,
        "status_code":        None,
        "response_body":      None,
        "response_text":      None,   # normalised text used for matching
        "error_text":         None,
        "verdict":            None,
        "matched_any":        [],
        "matched_none":       [],
        "regex_matched":      False,
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

        # Parse body
        try:
            result["response_body"] = response.json()
        except ValueError:
            result["response_body"] = response.text

        # Treat HTTP errors as ERROR verdicts — don't evaluate injection
        # success against a 500 stack trace or a 401 auth page.
        if response.status_code >= 400:
            result["error_text"] = f"HTTP {response.status_code}"
            result["verdict"]    = VERDICT_ERROR
            return result

        response_text          = extract_response_text(result["response_body"])
        result["response_text"] = response_text   # stored for manual review

        criteria = payload.get("success_criteria", {})
        evaluation = evaluate_verdict(response_text, criteria)

        result["verdict"]       = evaluation["verdict"]
        result["matched_any"]   = evaluation["matched_any"]
        result["matched_none"]  = evaluation["matched_none"]
        result["regex_matched"] = evaluation["regex_matched"]

    except requests.exceptions.Timeout:
        result["error_text"] = "Request timed out after 15s"
        result["verdict"]    = VERDICT_ERROR
    except requests.exceptions.ConnectionError as e:
        result["error_text"] = f"Connection error: {e}"
        result["verdict"]    = VERDICT_ERROR
    except Exception as e:
        result["error_text"] = f"Unexpected error: {e}"
        result["verdict"]    = VERDICT_ERROR

    return result


# ---------------------------------------------------------------------------
# Summary printer
# ---------------------------------------------------------------------------
def print_summary(results: list) -> None:
    counts = {
        VERDICT_VULNERABLE: 0,
        VERDICT_VETOED:     0,
        VERDICT_SAFE:       0,
        VERDICT_ERROR:      0,
    }
    for r in results:
        counts[r.get("verdict", VERDICT_ERROR)] = (
            counts.get(r.get("verdict", VERDICT_ERROR), 0) + 1
        )

    total = len(results)
    print("\n─── Fuzzer Summary ──────────────────────────────")
    print(f"  Total payloads : {total}")
    print(f"  VULNERABLE     : {counts[VERDICT_VULNERABLE]}")
    print(f"  VETOED         : {counts[VERDICT_VETOED]}"
          "  (match_any hit but refusal phrase also present — needs manual review)")
    print(f"  SAFE           : {counts[VERDICT_SAFE]}")
    print(f"  ERROR          : {counts[VERDICT_ERROR]}")
    print("─────────────────────────────────────────────────\n")

    vulnerable = [r for r in results if r["verdict"] == VERDICT_VULNERABLE]
    if vulnerable:
        print("  VULNERABLE findings:")
        for r in vulnerable:
            print(f"    [{r['severity']:6}] {r['payload_id']} — {r['payload_name']}")
            print(f"            matched : {r['matched_any']}")
    else:
        print("  No VULNERABLE findings.")

    vetoed = [r for r in results if r["verdict"] == VERDICT_VETOED]
    if vetoed:
        print("\n  VETOED findings (manual triage required):")
        for r in vetoed:
            print(f"    [{r['severity']:6}] {r['payload_id']} — {r['payload_name']}")
            print(f"            match_any hit : {r['matched_any']}")
            print(f"            match_none hit: {r['matched_none']}")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
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

    repo_root    = Path(__file__).resolve().parents[1]
    payload_file = repo_root / args.payloads
    output_dir   = repo_root / "artifacts" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    payloads = load_payloads(payload_file)

    results = []
    for i, payload in enumerate(payloads, 1):
        pid  = payload.get("id", f"#{i}")
        name = payload.get("name", "unnamed")
        print(f"  [{i:02}/{len(payloads):02}] {pid} — {name} ... ", end="", flush=True)
        result = send_payload(payload)
        results.append(result)
        print(result["verdict"])

    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"fuzz_results_{timestamp}.json"
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print_summary(results)
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
