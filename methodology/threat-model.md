\# Threat Model

&#x20;

\*\*Lab:\*\* AI Security Training Lab

\*\*Scope:\*\* `environments/chatbot`, `environments/rag-pipeline`, `environments/agent`

\*\*Framework:\*\* OWASP Top 10 for LLM Applications (2025) + MITRE ATLAS

\*\*Last updated:\*\* 2025

&#x20;

\---

&#x20;

\## 1. System Overview

&#x20;

This lab simulates three production-representative AI deployment patterns,

each intentionally vulnerable to a distinct class of adversarial attack:

&#x20;

| Environment | Deployment Pattern | Primary Attack Surface |

|-------------|--------------------|------------------------|

| `chatbot` | Direct-access LLM with system prompt | Prompt injection, system prompt extraction |

| `rag-pipeline` | LLM + ChromaDB retrieval over ingested documents | Document poisoning, retrieval manipulation |

| `agent` | Tool-enabled LLM with HTTP and filesystem tools | Tool abuse, SSRF, privilege escalation |

&#x20;

All three environments are isolated to `localhost` and share no external

network access beyond the OpenAI API.

&#x20;

\---

&#x20;

\## 2. Assets at Risk

&#x20;

| Asset | Environment | Confidentiality | Integrity | Availability |

|-------|-------------|-----------------|-----------|--------------|

| System prompt | chatbot | High | High | Medium |

| Session memory (JSONL) | chatbot | Medium | High | Low |

| RAG vector store | rag-pipeline | Medium | High | Medium |

| Ingested documents | rag-pipeline | Medium | High | Low |

| Tool definitions + schemas | agent | Low | High | Medium |

| API key (`OPENAI\_API\_KEY`) | all | Critical | — | — |

| Model responses | all | Low | Medium | Low |

&#x20;

\---

&#x20;

\## 3. Attacker Profiles

&#x20;

\### Profile 1 — Malicious End User

&#x20;

\*\*Who:\*\* An external user with direct access to the chat interface.

&#x20;

\*\*Motivation:\*\* Extract confidential system instructions, bypass content

restrictions, or manipulate model behaviour for personal gain.

&#x20;

\*\*Capability:\*\* Low to medium. No access to source code or infrastructure.

Operates exclusively through the chat input.

&#x20;

\*\*Relevant attacks:\*\* Direct prompt injection, jailbreaks, system prompt

extraction (SPE), identity confusion.

&#x20;

\*\*MITRE ATLAS:\*\* AML.T0051 — LLM Prompt Injection

&#x20;

\---

&#x20;

\### Profile 2 — Document Poisoner

&#x20;

\*\*Who:\*\* An attacker who can influence the content ingested into the RAG

knowledge base — via a shared upload interface, a compromised document

source, or a supply chain vector.

&#x20;

\*\*Motivation:\*\* Persistently manipulate model responses for all users by

corrupting the retrieval context.

&#x20;

\*\*Capability:\*\* Medium. Requires the ability to introduce content into the

ingestion pipeline, but no direct model or infrastructure access.

&#x20;

\*\*Relevant attacks:\*\* Document poisoning, indirect prompt injection via

retrieved content, context manipulation.

&#x20;

\*\*MITRE ATLAS:\*\* AML.T0020 — Poison Training Data (adapted for RAG)

&#x20;

\---

&#x20;

\### Profile 3 — Agent Hijacker

&#x20;

\*\*Who:\*\* An attacker who can influence the input to a tool-enabled agent —

either through direct input or via indirect injection embedded in tool

response content.

&#x20;

\*\*Motivation:\*\* Cause the agent to invoke tools outside its intended scope,

reach restricted internal resources, or escalate privileges across tool

boundaries.

&#x20;

\*\*Capability:\*\* Medium to high. May exploit both the model layer (injection)

and the tool layer (SSRF, path traversal).

&#x20;

\*\*Relevant attacks:\*\* Tool misuse, SSRF via HTTP tools, privilege escalation,

indirect injection via tool responses.

&#x20;

\*\*MITRE ATLAS:\*\* AML.T0043 — Craft Adversarial Data (agent context)

&#x20;

\---

&#x20;

\## 4. Threat Summary

&#x20;

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

&#x20;

\---

&#x20;

\## 5. Trust Boundaries

&#x20;

```

\[ End user input ]

&#x20;     ↓  ← injection boundary

\[ LLM (system prompt + context) ]

&#x20;     ↓  ← retrieval boundary

\[ Vector store / ingested documents ]  ← poisoning boundary

&#x20;     ↓  ← tool invocation boundary

\[ External tools (HTTP, filesystem) ]  ← SSRF / escalation boundary

```

&#x20;

Each boundary represents a point where attacker-controlled data crosses

into a trusted execution context. Playbooks are organized around these

boundaries — one per trust boundary class.

&#x20;

\---

&#x20;

\## 6. Out of Scope

&#x20;

The following are not modelled in this lab:

&#x20;

\- Authentication and authorisation bypasses at the infrastructure layer

\- Denial of service against the OpenAI API

\- Training data poisoning of the base LLM (pre-deployment)

\- Supply chain attacks against Python dependencies

\- Physical access or host OS compromise

&#x20;

\---

&#x20;

\## 7. References

&#x20;

\- \[OWASP Top 10 for LLM Applications (2025)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

\- \[MITRE ATLAS](https://atlas.mitre.org/)

\- \[NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

\- `methodology/attack-surface-map.md` — full OWASP × environment coverage matrix

\- `methodology/rules-of-engagement.md` — authorised scope and data handling rules

