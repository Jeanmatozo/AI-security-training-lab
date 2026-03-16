# AI-SEC-YYYY-NNN

## Title
Short descriptive title of the security finding.

---

## Summary
Brief explanation of the issue or observation.

Describe:

• what was tested  
• what occurred  
• why it matters

Keep this section short and readable.

---

## Scope

Environment:
`environments/<environment_name>`

Endpoint / Target:
`<target_url>`

Attack Category:
`attacks/<category>`

Payload IDs Tested:
- ID-001
- ID-002
- ID-003

---

## Evidence

Evidence ID:
`EVID-XXX-YYYYMMDD-NNN`

Source Artifact:
`artifacts/results/<artifact_filename>.json`

SHA-256:
`<artifact_sha256_hash>`

Evidence Transcript:
`evidence/transcripts/<evidence_id>.md`

---

## Method

Explain how the attack was executed.

Typically includes:

• payload library used  
• attack runner used (`tools/fuzzer.py`)  
• how artifacts were generated  
• how evidence was promoted (`tools/collect_evidence.py`)

---

## Payload Results

### Payload ID — Description

Result:
Success / Failed / Partial

Observation:
Short explanation of what happened.

---

## Security Impact

Explain the security significance.

Examples:

• prompt injection success  
• data disclosure  
• tool misuse  
• privilege escalation  
• or no vulnerability observed

---

## Limitations

Explain testing boundaries.

Examples:

• small payload set  
• single-turn prompts only  
• no encoding techniques tested  
• environment limitations

---

## Recommendation

Explain next actions.

Examples:

• expand payload library  
• implement guardrails  
• add output filtering  
• test multi-turn attacks

---

## Status

Example values:

• Confirmed vulnerability  
• Mitigation recommended  
• Baseline assessment completed  
• Under investigation