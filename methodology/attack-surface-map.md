# Attack Surface Map
 
**Lab:** AI Security Training Lab
**Scope:** `environments/chatbot`, `environments/rag-pipeline`, `environments/agent`
**Frameworks:** OWASP Top 10 for LLM Applications (2025) · MITRE ATLAS · NIST AI RMF
**Last updated:** 2025
 
---
 
## 1. Purpose
 
This document maps every attack covered in this lab to:
 
- The environment it targets
- The OWASP LLM category it falls under
- The MITRE ATLAS technique ID
- The NIST AI RMF function it stress-tests
 
It is the connective tissue between the threat model, the playbooks, and
the finding reports. Every finding in `reports/findings/` should trace back
to a row in this map.
 
---
 
## 2. OWASP Coverage Matrix
 
### Legend
 
| Symbol | Meaning |
|--------|---------|
| ✅ | Covered — payload exists, playbook written |
| 🔄 | Partial — payload exists, playbook in progress |
| ⬜ | Not covered in this lab |
 
---
 
### LLM01 — Prompt Injection
 
| Attack | chatbot | rag-pipeline | agent | Payload ID prefix |
|--------|:-------:|:------------:|:-----:|-------------------|
| Direct prompt injection | ✅ | ⬜ | ✅ | `PI-001` – `PI-003` |
| Indirect injection via retrieved content | ⬜ | ✅ | ✅ | `PI-004` – `PI-005` |
| Jailbreak / persona hijack | ✅ | ⬜ | ⬜ | `PI-006` |
| Gradual context erosion (multi-turn) | ✅ | ⬜ | ⬜ | `PI-007` |
| System prompt extraction (SPE) | ✅ | ⬜ | ⬜ | `PI-008` – `PI-010` |
| Identity confusion | ✅ | ⬜ | ⬜ | `PI-011` |
 
---
 
### LLM02 — Insecure Output Handling
 
| Attack | chatbot | rag-pipeline | agent | Payload ID prefix |
|--------|:-------:|:------------:|:-----:|-------------------|
| Reflected injection in model output | 🔄 | ⬜ | ⬜ | *(planned)* |
| Downstream tool execution via output | ⬜ | ⬜ | 🔄 | *(planned)* |
 
> LLM02 coverage is planned for a future release. Current lab focus is
> LLM01, LLM03, and LLM08.
 
---
 
### LLM03 — Training Data Poisoning
 
| Attack | chatbot | rag-pipeline | agent | Payload ID prefix |
|--------|:-------:|:------------:|:-----:|-------------------|
| Document poisoning (RAG knowledge base) | ⬜ | ✅ | ⬜ | `RAG-001` – `RAG-003` |
| Retrieval ranking manipulation | ⬜ | ✅ | ⬜ | `RAG-004` |
| Context window flooding | ⬜ | ✅ | ⬜ | `RAG-005` |
| Indirect injection via poisoned document | ⬜ | ✅ | ⬜ | `RAG-006` |
 
---
 
### LLM06 — Sensitive Information Disclosure
 
| Attack | chatbot | rag-pipeline | agent | Payload ID prefix |
|--------|:-------:|:------------:|:-----:|-------------------|
| System prompt extraction | ✅ | ⬜ | ⬜ | `PI-008` – `PI-010` |
| RAG document exfiltration via response | ⬜ | ✅ | ⬜ | `RAG-007` |
| Tool schema / config disclosure | ⬜ | ⬜ | 🔄 | *(planned)* |
 
---
 
### LLM08 — Excessive Agency
 
| Attack | chatbot | rag-pipeline | agent | Payload ID prefix |
|--------|:-------:|:------------:|:-----:|-------------------|
| Tool invocation outside intended scope | ⬜ | ⬜ | ✅ | `AGENT-001` – `AGENT-002` |
| SSRF via HTTP tool | ⬜ | ⬜ | ✅ | `AGENT-003` – `AGENT-004` |
| Privilege escalation via tool chain | ⬜ | ⬜ | ✅ | `AGENT-005` |
| Indirect injection → tool hijack | ⬜ | ✅ | ✅ | `AGENT-006` |
 
---
 
### OWASP Coverage Summary
 
| OWASP Category | Lab Coverage |
|----------------|-------------|
| LLM01 — Prompt Injection | ✅ Full |
| LLM02 — Insecure Output Handling | 🔄 Partial |
| LLM03 — Training Data Poisoning | ✅ Full |
| LLM04 — Model Denial of Service | ⬜ Not in scope |
| LLM05 — Supply Chain Vulnerabilities | ⬜ Not in scope |
| LLM06 — Sensitive Information Disclosure | ✅ Full |
| LLM07 — Insecure Plugin Design | ⬜ Not in scope |
| LLM08 — Excessive Agency | ✅ Full |
| LLM09 — Overreliance | ⬜ Not in scope |
| LLM10 — Model Theft | ⬜ Not in scope |
 
---
 
## 3. MITRE ATLAS Technique Mapping
 
| MITRE ATLAS Technique | ID | Attacks Covered | Environment |
|-----------------------|----|-----------------|-------------|
| LLM Prompt Injection | AML.T0051 | Direct injection, indirect injection, jailbreak, SPE, identity confusion, gradual erosion | chatbot, rag-pipeline, agent |
| Poison Training Data | AML.T0020 | Document poisoning, retrieval manipulation, context flooding | rag-pipeline |
| Craft Adversarial Data | AML.T0043 | Tool misuse, SSRF, privilege escalation, indirect injection via tool response | agent |
| Discover ML Model Ontology | AML.T0013 | System prompt extraction, tool schema disclosure | chatbot, agent |
| ML Model Inference API Access | AML.T0040 | All attacks — OpenAI API is the inference layer for all environments | all |
 
---
 
## 4. NIST AI RMF Mapping
 
The NIST AI Risk Management Framework organises AI risk into four core
functions: **Govern, Map, Measure, Manage**. The attacks in this lab
stress-test the *Measure* and *Manage* functions most directly — they
expose what happens when governance and mapping controls are absent or
insufficient in a deployed AI system.
 
---
 
### GOVERN — Policies and accountability structures
 
| Lab Finding Type | GOVERN Sub-category | What the attack reveals |
|------------------|---------------------|-------------------------|
| System prompt extraction | GV-1.1 — Organisational AI policies | Absence of confidentiality controls on model configuration |
| Jailbreak / restriction bypass | GV-1.2 — Roles and responsibilities | No enforcement of acceptable use at the model layer |
| Excessive agency | GV-6.1 — Policies for third-party risks | Insufficient scope controls on tool-enabled models |
 
---
 
### MAP — Risk identification and context
 
| Lab Finding Type | MAP Sub-category | What the attack reveals |
|------------------|-----------------|-------------------------|
| RAG document poisoning | MP-2.3 — AI system context | Data provenance not considered in retrieval design |
| Indirect injection via RAG | MP-5.1 — Likelihood of AI risks | Injection via trusted retrieval context not identified as a threat |
| SSRF via agent tool | MP-3.5 — Organisational risk tolerance | External network access from tools not mapped as a risk |
 
---
 
### MEASURE — Risk analysis and assessment
 
| Lab Finding Type | MEASURE Sub-category | What the attack reveals |
|------------------|---------------------|-------------------------|
| All prompt injection variants | MS-2.5 — Evaluations for AI risks | No adversarial testing performed before deployment |
| Context manipulation | MS-2.6 — Evaluations of data quality | Retrieved content not validated before use as model context |
| Tool privilege escalation | MS-2.10 — Privacy risk | Downstream impact of tool calls not assessed |
| Evidence pipeline (lab tool) | MS-4.1 — Effectiveness of risk treatments | SHA-256 signed artifacts demonstrate measurable, reproducible evidence |
 
---
 
### MANAGE — Risk response and recovery
 
| Lab Finding Type | MANAGE Sub-category | What the attack reveals |
|------------------|---------------------|-------------------------|
| Any confirmed PASS verdict | MG-2.2 — Mechanisms for risk response | No input sanitisation or output filtering deployed |
| RAG poisoning persistence | MG-3.1 — Residual risk after treatment | Poisoned vector store persists across restarts without `down -v` |
| Finding report (lab output) | MG-4.1 — Residual risk documentation | Each `AI-SEC-YYYY-NNN.md` maps directly to this sub-category |
 
---
 
## 5. Attack Chain Coverage
 
Attack chains combine techniques across multiple OWASP categories,
MITRE techniques, and environments. Both chains in this lab are
documented in `playbooks/chains/`.
 
### Chain 01 — RAG Exfiltration
 
```
Document poisoning (LLM03 / AML.T0020)
  → Indirect injection via retrieval (LLM01 / AML.T0051)
  → Sensitive data exfiltration via response (LLM06 / AML.T0013)
```
 
**Environments:** rag-pipeline → chatbot
**Playbook:** `playbooks/chains/chain-01-rag-exfiltration.md`
 
---
 
### Chain 02 — Agent Escalation
 
```
Indirect injection via tool response (LLM01 / AML.T0051)
  → Tool invocation outside scope (LLM08 / AML.T0043)
  → Privilege escalation via chained tool calls (LLM08 / AML.T0043)
```
 
**Environments:** agent (self-contained)
**Playbook:** `playbooks/chains/chain-02-agent-escalation.md`
 
---
 
## 6. Coverage Gaps and Roadmap
 
The following OWASP categories are not currently covered and represent
areas for future lab expansion:
 
| Gap | Rationale for exclusion | Suggested addition |
|-----|-------------------------|-------------------|
| LLM02 — Insecure Output Handling | Requires a downstream consumer (browser renderer, second model) to demonstrate impact | Add a simple HTML renderer to the chatbot environment |
| LLM07 — Insecure Plugin Design | Overlaps significantly with LLM08 in this lab's architecture | Introduce a plugin manifest and demonstrate schema bypass |
| LLM04 — Model Denial of Service | Requires cost/latency monitoring infrastructure | Add token usage tracking to the fuzzer output |
 
---
 
## 7. References
 
- [OWASP Top 10 for LLM Applications (2025)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MITRE ATLAS](https://atlas.mitre.org/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- `methodology/threat-model.md` — attacker profiles and impact tiers
- `methodology/rules-of-engagement.md` — authorised scope and data handling
- `playbooks/README.md` — full operational testing guide
 
