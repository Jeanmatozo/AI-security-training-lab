# AI-security-training-lab

This is a professional AI security training lab for hands-on testing of LLM, RAG,
and agent-based systems with structured attack playbooks, an evidence
capture pipeline, and consulting-grade reporting workflows.

This lab focuses on real-world vulnerabilities found in:

- Large Language Models (LLMs)
- Retrieval-Augmented Generation (RAG) systems
- AI Agents and tool-enabled models

Attack coverage is aligned with the **[OWASP Top 10 for LLM Applications (2025)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)** and mapped to **[MITRE ATLAS](https://atlas.mitre.org/)** adversarial technique IDs.

The goal is a **repeatable, evidence-backed framework**, not a collection
of prompts. Every attack produces a signed artifact that traces forward to
a finding report.

~~~bash
environments → attacks → tools → artifacts → evidence → reports
                         ↘ playbooks
                         ↘ methodology

~~~

---

## Where to Start

| I want to...                          | Go to                                     |
|---------------------------------------|-------------------------------------------|
| Get the lab running                   | [Quickstart](#quickstart) (below)         |
| Run my first attack                   | `playbooks/LLM01-prompt-injection.md`     |
| Understand the full attack pipeline   | `playbooks/README.md`                     |
| Read the threat model                 | `methodology/threat-model.md`             |
| Document a finding                    | `reports/templates/finding-template.md`   |

---

## Implementation status

| Component | Status | Notes |
|---|---|---|
| `environments/chatbot` | ✅ Functional | FastAPI, intentionally vulnerable |
| `environments/rag-pipeline` | ✅ Functional | LangChain + ChromaDB, named volume |
| `environments/agent` | ✅ Functional | Tool-enabled, SSRF vector present |
| `attacks/prompt-injection` | ✅ Functional | Direct, indirect, jailbreak, SPE payloads |
| `attacks/rag-attacks` | ✅ Functional | Poisoning + context manipulation |
| `attacks/agent-attacks` | ✅ Functional | Tool abuse + privilege escalation |
| `tools/fuzzer.py` | ✅ Functional | Runs all payloads.json files |
| `tools/evidence_promoter.py` | ✅ Functional | SHA-256 + Ed25519 signing, evidence promotion |
| `tools/keygen.py` | ✅ Functional | Ed25519 keypair generation |
| `tools/verify_evidence.py` | ✅ Functional | Transcript integrity + signature verification |
| `playbooks/` | ✅ Complete | LLM01, LLM03, LLM08 + 2 attack chains |
| `reports/findings/` | ✅ Complete | AI-SEC-2026-001, 002, 003 documented |

---

## Repository structure

```bash
AI-security-training-lab/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml          # chatbot + rag-pipeline + agent
│                               # lab-internal + lab-external networks
│                               # rag-vector-store named volume
│
├── environments/
│   ├── chatbot/
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── rag-pipeline/
│   │   ├── rag_api.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── agent/
│       ├── agent_api.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── attacks/
│   ├── README.md               # Payload schema + ID prefix table
│   ├── prompt-injection/
│   │   ├── payloads.json       # Direct, indirect, jailbreak, SPE
│   │   └── payloads.md
│   ├── rag-attacks/
│   │   ├── payloads.json
│   │   └── payloads.md
│   └── agent-attacks/
│       ├── payloads.json
│       └── payloads.md
│
├── tools/
│   ├── fuzzer.py               # payloads.json → artifacts/results/
│   ├── evidence_promoter.py    # artifacts/results/ → evidence/transcripts/
│   ├── keygen.py               # Ed25519 keypair generation (one-time)
│   └── verify_evidence.py      # transcript integrity + signature verification
│
├── keys/                       # signing_key.pem is .gitignored
│   ├── signing_key.pem         # ← never commit
│   ├── signing_key.pub.pem
│   └── signing_key.pub.sha256
│
├── playbooks/
│   ├── LLM01-prompt-injection.md
│   ├── LLM03-training-data-poisoning.md
│   ├── LLM08-excessive-agency.md
│   └── chains/
│       ├── chain-01-rag-exfiltration.md
│       └── chain-02-agent-escalation.md
│
├── methodology/
│   ├── attack-surface-map.md   # OWASP coverage matrix + NIST AI RMF mapping
│   ├── threat-model.md
│   └── rules-of-engagement.md
│
├── artifacts/
│   └── results/                # Raw fuzzer output — never cited directly in reports
│
├── evidence/
│   └── transcripts/            # SHA-256 + Ed25519 signed, promoted by evidence_promoter.py
│
└── reports/
    ├── templates/
    │   └── finding-template.md
    └── findings/               # Completed reports: AI-SEC-YYYY-NNN.md
```

---

## Evidence pipeline

Raw artifacts are never cited directly in reports. They must be promoted
through the evidence pipeline first:

```
attacks/*/payloads.json
  → tools/fuzzer.py
  → artifacts/results/          ← raw output, never cited directly
  → tools/evidence_promoter.py  ← SHA-256 hashed + Ed25519 signed
  → evidence/transcripts/       ← tamper-evident, reportable
  → reports/findings/           ← cites evidence ID
```

Each promoted transcript is integrity-protected at two levels: a SHA-256
hash of both the source artifact and the transcript file, and an optional
Ed25519 detached signature. All evidence is indexed in
`evidence/transcripts/MANIFEST.json`. Use `tools/verify_evidence.py` to
confirm integrity before citing a transcript in a report.

See `playbooks/README.md` for full pipeline commands.

---

## Quickstart

### Clone the repository
```bash
git clone https://github.com/Jeanmatozo/AI-security-training-lab.git
cd AI-security-training-lab
```

### Option A — Docker (recommended)
Best for running all three environments simultaneously with consistent,
reproducible behaviour across machines.

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)
(macOS / Windows) or Docker Engine (Linux), running before you continue.

**1. Copy and configure the environment file**
```bash
cp .env.example .env
```

Open `.env` and set your API key before starting the containers:
```bash
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4.1-mini
```

**2. Build and start all environments**
```bash
docker-compose up --build
```

When all three services are ready you will see lines similar to:
```
chatbot      | INFO:     Uvicorn running on http://0.0.0.0:8000
rag-pipeline | INFO:     Uvicorn running on http://0.0.0.0:8001
agent        | INFO:     Uvicorn running on http://0.0.0.0:8002
```

The three lab environments are now running at:

- Chatbot — `http://localhost:8000/docs`
- RAG pipeline — `http://localhost:8001/docs`
- Agent — `http://localhost:8002/docs`

**3. Stop the environment**
```bash
docker-compose down        # stops containers, preserves RAG vector store
docker-compose down -v     # stops containers AND wipes the vector store
```

> Use `down -v` to reset the RAG knowledge base to a clean state between
> test sessions. Use `down` to preserve any poisoned state across restarts.

---

### Option B — Local, single environment (no Docker required)
Best for inspecting code behaviour, debugging vulnerabilities, and iterating
on attack scenarios before moving to the full Docker setup.

**Prerequisites:** Python 3.10 or higher
> **Tip:** Start here with `environments/chatbot` to sanity-check the raw
> environment and understand the code. Once comfortable, move to Option A
> for the RAG and Agent environments — those involve more moving parts
> (vector databases, inter-service networking) that are much harder to
> manage manually.

**1. Copy the environment file**

```bash
cp .env.example .env
```

Open `.env` and set your API key:

```env
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4.1-mini
```

**2. Create a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
cd environments/chatbot
pip install -r requirements.txt
```

**4. Start the server**
```bash
uvicorn app:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

**5. Open the attack interface**

Go to `http://127.0.0.1:8000/docs` — this opens the FastAPI Swagger UI
where you can send prompts manually and observe model responses.

You are now ready to run the prompt injection playbook:
`playbooks/LLM01-prompt-injection.md`

---

## Lab Topics

| Topic | Coverage |
|-------|----------|
| Prompt injection | Direct injection, indirect injection via RAG, jailbreaks, system prompt extraction |
| RAG exploitation | Document poisoning, context manipulation, retrieval abuse |
| Agent tool abuse | Tool misuse, SSRF via HTTP tools, privilege escalation |
| Multi-step attack chains | Realistic adversarial sequences across environments |

---

## Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.10+ |
| API framework | FastAPI |
| Containerisation | Docker + Docker Compose |
| LLM orchestration | LangChain |
| Vector store | ChromaDB |
| LLM provider | OpenAI API (`gpt-4.1-mini`) |
| Attack runner | `tools/fuzzer.py` (custom) |
| Evidence pipeline | `tools/evidence_promoter.py` + `tools/verify_evidence.py` (custom) |
| Signing | Ed25519 via `cryptography` library |

---

## Responsible use

This repository is intended for **educational and defensive security
research purposes only**.

All testing must be conducted in isolated, controlled environments with
explicit authorisation. Do not use these techniques against systems you
do not own or have permission to test.

---

## License

MIT License — see `LICENSE` for details.

---

## Acknowledgements

- [OWASP Top 10 for LLM Applications (2025)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MITRE ATLAS](https://atlas.mitre.org/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

Built by [jeanmatozo](https://github.com/Jeanmatozo)