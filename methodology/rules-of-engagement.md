
# Rules of Engagement
 
**Lab:** AI Security Training Lab
**Scope:** Local lab environments only — `localhost` / `127.0.0.1`
**Last updated:** 2025
 
---
 
## 1. Purpose
 
This document defines the authorised scope, boundaries, and conduct
standards for all security testing performed within this lab.
 
These rules apply whether the lab is used for personal skill development,
team training, or as a portfolio demonstration of AI red-teaming
methodology. They exist to ensure testing remains controlled, reproducible,
and professionally defensible.
 
---
 
## 2. Authorised Scope
 
Testing is authorised **only** against the following environments:
 
| Environment | Host | Port |
|-------------|------|------|
| `chatbot` | `127.0.0.1` / `localhost` | `8000` |
| `rag-pipeline` | `127.0.0.1` / `localhost` | `8001` |
| `agent` | `127.0.0.1` / `localhost` | `8002` |
 
All three environments are intentionally vulnerable systems created
specifically for this lab. No other systems, APIs, or services are
in scope.
 
---
 
## 3. Explicitly Out of Scope
 
The following are strictly prohibited:
 
- Any system not listed in Section 2
- The OpenAI API itself — testing is against lab environments only; the
  upstream provider is never a target
- Any production, staging, or third-party AI system
- Cloud-hosted instances of this lab unless explicitly authorised in writing
- Attacks designed to cause financial harm via excessive API usage
 
> If you are unsure whether a target is in scope, it is out of scope.
 
---
 
## 4. Data Handling
 
**Test payloads must never contain real personal data.**
 
All attack payloads in `attacks/*/payloads.json` use synthetic, fictional
content only. When creating new payloads:
 
- Use placeholder names, emails, and identifiers (e.g. `user@example.com`,
  `John Doe`, `ACME Corp`)
- Never include real credentials, API keys, PII, or proprietary information
- Never ingest real documents into the RAG vector store during testing
 
Evidence collected by `tools/collect_evidence.py` is stored locally in
`evidence/transcripts/`. This directory should not be committed to a public
repository if it contains sensitive test outputs.
 
---
 
## 5. API Key Responsibility
 
The `OPENAI_API_KEY` in `.env` is the operator's personal credential.
 
- Never commit `.env` to version control — `.gitignore` excludes it by default
- Never share API keys in screenshots, findings reports, or public artifacts
- Monitor API usage during extended fuzzing runs to avoid unintended cost
- Rotate the key immediately if it is accidentally exposed
 
---
 
## 6. Evidence and Reporting Standards
 
All findings must be evidence-backed and reproducible:
 
- Raw fuzzer output in `artifacts/results/` is never cited directly in reports
- Evidence must be promoted via `tools/collect_evidence.py` before citation
- Each finding report must reference a specific evidence ID (e.g. `EV-2025-042`)
- Reproduction steps must be accurate and complete — a reader should be able
  to replicate the finding from the report alone
 
When sharing findings externally (portfolio, team review, consulting context):
 
- Redact any API keys, internal hostnames, or sensitive configuration values
- Confirm all evidence was generated against authorised lab environments only
- Do not present lab findings as vulnerabilities in third-party production systems
 
---
 
## 7. Conduct Standards
 
This lab is a professional training environment. All operators are expected to:
 
- Treat the methodology, evidence pipeline, and reporting workflow as they
  would on a real engagement
- Document findings accurately — do not overstate impact or fabricate evidence
- Disclose the lab context clearly when sharing work publicly or in a portfolio
- Not use techniques, payloads, or tooling from this lab against systems
  outside the authorised scope
 
---
 
## 8. Pre-Test Checklist
 
Complete this checklist before starting any test session:
 
```
[ ] Lab environment started and sanity-checked (POST /chat returns expected response)
[ ] .env confirmed present and not committed to version control
[ ] Test payloads reviewed — no real PII or credentials present
[ ] artifacts/results/ directory exists and is writable
[ ] evidence/transcripts/ directory exists and is writable
[ ] Scope confirmed — testing against localhost only
```
 
---
 
## 9. Incident Response
 
If an attack payload produces an unintended result — such as unexpected
external network calls, excessive API usage, or exposure of real credentials:
 
1. Stop the fuzzer immediately (`Ctrl+C`)
2. Stop all running containers (`docker-compose down`)
3. Review `artifacts/results/` for the triggering payload
4. Rotate any credentials that may have been exposed
5. Document the incident in `reports/findings/` as a lab observation
 
---
 
## 10. References
 
- `methodology/threat-model.md` — attacker profiles and assets at risk
- `methodology/attack-surface-map.md` — OWASP coverage matrix per environment
- `playbooks/README.md` — full operational testing guide
- [OWASP Top 10 for LLM Applications (2025)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
