# Threat Model
 
**Lab:** AI Security Training Lab
**Scope:** `environments/chatbot`, `environments/rag-pipeline`, `environments/agent`
**Framework:** OWASP Top 10 for LLM Applications (2025) + MITRE ATLAS
**Last updated:** 2025
 
---
 
## 1. System Overview
 
This lab simulates three production-representative AI deployment patterns,
each intentionally vulnerable to a distinct class of adversarial attack:
 
| Environment | Deployment Pattern | Primary Attack Surface |
|-------------|--------------------|------------------------|
| `chatbot` | Direct-access LLM with system prompt | Prompt injection, system prompt extraction |
| `rag-pipeline` | LLM + ChromaDB retrieval over ingested documents | Document poisoning, retrieval manipulation |
| `agent` | Tool-enabled LLM with HTTP and filesystem tools | Tool abuse, SSRF, privilege escalation |
 
All three environments are isolated to `localhost` and share no external
network access beyond the OpenAI API.
 
---
 
## 2. Assets at Risk
 
| Asset | Environment | Confidentiality | Integrity | Availability |
|-------|-------------|-----------------|-----------|--------------|
| System prompt | chatbot | High | High | Medium |
| Session memory (JSONL) | chatbot | Medium | High | Low |
| RAG vector store | rag-pipeline | Medium | High | Medium |
| Ingested documents | rag-pipeline | Medium | High | Low |
| Tool definitions + schemas | agent | Low | High | Medium |
| API key (`OPENAI_API_KEY`) | all | Critical | — | — |
| Model responses | all | Low | Medium | Low |
 
---
 
## 3. Attacker Profiles
 
### Profile 1 — Malicious End User
 
**Who:** An external user with direct access to the chat interface.
 
**Motivation:** Extract confidential system instructions, bypass content
restrictions, or manipulate model behaviour for personal gain.
 
**Capability:** Low to medium. No access to source code or infrastructure.
Operates exclusively through the chat input.
 
**Relevant attacks:** Direct prompt injection, jailbreaks, system prompt
extraction (SPE), identity confusion.
 
**MITRE ATLAS:** AML.T0051 — LLM Prompt Injection
 
---
 
### Profile 2 — Document Poisoner
 
**Who:** An attacker who can influence the content ingested into the RAG
knowledge base — via a shared upload interface, a compromised document
source, or a supply chain vector.
 
**Motivation:** Persistently manipulate model responses for all users by
corrupting the retrieval context.
 
**Capability:** Medium. Requires the ability to introduce content into the
ingestion pipeline, but no direct model or infrastructure access.
 
**Relevant attacks:** Document poisoning, indirect prompt injection via
retrieved content, context manipulation.
 
**MITRE ATLAS:** AML.T0020 — Poison Training Data (adapted for RAG)
 
---
 
### Profile 3 — Agent Hijacker
 
**Who:** An attacker who can influence the input to a tool-enabled agent —
either through direct input or via indirect injection embedded in tool
response content.
 
**Motivation:** Cause the agent to invoke tools outside its intended scope,
reach restricted internal resources, or escalate privileges across tool
boundaries.
 
**Capability:** Medium to high. May exploit both the model layer (injection)
and the tool layer (SSRF, path traversal).
 
**Relevant attacks:** Tool misuse, SSRF via HTTP tools, privilege escalation,
indirect injection via tool responses.
 
**MITRE ATLAS:** AML.T0043 — Craft Adversarial Data (agent context)
 
---
 
## 4. Threat Summary
 
| Threat | Attacker Profile | OWASP LLM | MITRE ATLAS | Likelihood | Impact |
|--------|-----------------|-----------|-------------|------------|--------|
| System prompt extraction | Malicious end user | LLM01 | AML.T0051 | High | High |
| Direct prompt injection | Malicious end user | LLM01 | AML.T0051 | High | High |
| Jailbreak / restriction bypass | Malicious end user | LLM01 | AML.T0051 | High | Medium |
| RAG document poisoning | Document poisoner | LLM03 | AML.T0020 | Medium | High |
| Indirect injection via retrieval | Document poisoner | LLM01 | AML.T0051 | Medium | High |
| Context manipulation | Document poisoner | LLM03 | AML.T0020 | Medium | Medium |
| Agent tool misuse | Agent hijacker | LLM08 | AML.T0043 | Medium | High |
| SSRF via HTTP tool | Agent hijacker | LLM08 | AML.T0043 | Medium | Critical |
| Privilege escalation via tool chain | Agent hijacker | LLM08 | AML.T0043 | Low | Critical |
 
---
 
## 5. Trust Boundaries
 
```
[ End user input ]
      ↓  ← injection boundary
[ LLM (system prompt + context) ]
      ↓  ← retrieval boundary
[ Vector store / ingested documents ]  ← poisoning boundary
      ↓  ← tool invocation boundary
[ External tools (HTTP, filesystem) ]  ← SSRF / escalation boundary
```
 
Each boundary represents a point where attacker-controlled data crosses
into a trusted execution context. Playbooks are organized around these
boundaries — one per trust boundary class.
 
---
 
## 6. Out of Scope
 
The following are not modelled in this lab:
 
- Authentication and authorisation bypasses at the infrastructure layer
- Denial of service against the OpenAI API
- Training data poisoning of the base LLM (pre-deployment)
- Supply chain attacks against Python dependencies
- Physical access or host OS compromise
 
---
 
## 7. References
 
- [OWASP Top 10 for LLM Applications (2025)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MITRE ATLAS](https://atlas.mitre.org/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- `methodology/attack-surface-map.md` — full OWASP × environment coverage matrix
- `methodology/rules-of-engagement.md` — authorised scope and data handling rules
 
