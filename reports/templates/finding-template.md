# AI-SEC-YYYY-NNN

**Severity:** `Critical / High / Medium / Low`

**Status:** `Open / Mitigated / Regression / Informational`

---

## Title
Short descriptive title of the security finding.

---

## Summary

Brief explanation of the issue or observation.

Describe:

- what was tested
- what occurred
- why it matters

Keep this section short and readable.

---

## Scope

**Environment:**
`environments/<environment_name>`

**Endpoint / Target:**
`<target_url>`

**Attack Category:**
`attacks/<category>`

**OWASP LLM Category:**
`LLM01 — Prompt Injection`

**MITRE ATLAS Technique:**
`AML.T0051`

**Payload IDs Tested:**
- ID-001
- ID-002
- ID-003

---

## Evidence

**Evidence IDs:**
- `EVID-XXX-YYYYMMDD-001`
- `EVID-XXX-YYYYMMDD-002`

**Source Artifact:**
`artifacts/results/<artifact_filename>.json`

**SHA-256:**
`<artifact_sha256_hash>`

**Evidence Transcripts:**
- `evidence/transcripts/EVID-XXX-YYYYMMDD-001.md`
- `evidence/transcripts/EVID-XXX-YYYYMMDD-002.md`

---

## Method

Explain how the attack was executed.

Typically includes:

- payload library used
- attack runner used (`tools/fuzzer.py`)
- evaluation mode used (`keyword` / `llm_judge` / `hybrid`)
- how artifacts were generated
- how evidence was promoted (`tools/collect_evidence.py`)

---

## Reproduction Steps

Exact commands to reproduce this finding end-to-end.

```bash
# 1. Start the target environment
docker-compose up --build

# 2. Run the relevant payloads
python tools/fuzzer.py \
  --payloads attacks/<category>/payloads.json \
  --output   artifacts/results/<artifact_filename>.json

# 3. Promote to evidence
python tools/collect_evidence.py \
  --input  artifacts/results/<artifact_filename>.json \
  --output evidence/transcripts/
```

---

## Payload Results

### ID-001 — Payload Name

**Result:** `VULNERABLE → PASS`
**Confidence:** `0.00`
**Judge rationale:** One-sentence explanation from the LLM judge.
**Matched indicators:** `["keyword one", "keyword two"]`
**Observation:** Short explanation of what happened.

---

### ID-002 — Payload Name

**Result:** `SAFE → FAIL`
**Confidence:** `null`
**Judge rationale:** N/A
**Matched indicators:** `[]`
**Observation:** Short explanation of what happened.

---

### ID-003 — Payload Name

**Result:** `VETOED → PASS`
**Confidence:** `0.00`
**Judge rationale:** One-sentence explanation from the LLM judge.
**Matched indicators:** `["keyword one"]`
**Observation:** Requires manual triage — match_any fired but refusal phrase also present.

---

## Security Impact

Explain the security significance.

Examples:

- prompt injection success
- data disclosure
- tool misuse
- privilege escalation
- or no vulnerability observed

---

## Limitations

Explain testing boundaries.

Examples:

- small payload set
- single-turn prompts only
- no encoding techniques tested
- environment limitations

---

## Recommendation

Explain next actions.

Examples:

- expand payload library
- implement guardrails
- add output filtering
- test multi-turn attacks

---

## Remediation Verification

> Complete this section after a defense has been applied.

**Defense applied:**
`environments/<environment_name>/defenses/<module_name>.py`

**Re-run command:**
```bash
docker-compose --profile hardened up --build

python tools/fuzzer.py \
  --payloads attacks/<category>/payloads.json \
  --output   artifacts/results/<artifact_filename>_hardened.json
```

**Result after hardening:**
- ID-001: `SAFE → FAIL` ✓
- ID-002: `SAFE → FAIL` ✓
- ID-003: `VETOED → PASS` — manual review still required

**Conclusion:**
`Mitigated / Partially mitigated / Not mitigated`

---

## Status

| Field | Value |
|-------|-------|
| Current status | `Open` |
| Finding date | `YYYY-MM-DD` |
| Last updated | `YYYY-MM-DD` |
| Assigned to | `—` |

**Status definitions:**

- `Open` — vulnerability confirmed, no mitigation applied
- `Mitigated` — defense enabled, re-run confirms SAFE / FAIL on all previously passing payloads
- `Regression` — previously mitigated finding re-introduced
- `Informational` — no vulnerability observed; baseline assessment result