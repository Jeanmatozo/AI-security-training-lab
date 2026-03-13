# AI-security-training-lab

A professional AI security training lab for hands-on testing of LLM, RAG,
and agent-based systems — with structured attack playbooks, an evidence
capture pipeline, and consulting-grade reporting workflows.

This lab focuses on real-world vulnerabilities found in:

- Large Language Models (LLMs)
- Retrieval-Augmented Generation (RAG) systems
- AI Agents and tool-enabled models

Attack coverage is aligned with the **OWASP Top 10 for LLM Applications
(2025)** and mapped to **MITRE ATLAS** adversarial technique IDs.

The goal is a **repeatable, evidence-backed framework** — not a collection
of prompts. Every attack produces a signed artifact that traces forward to
a finding report.

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
| `tools/collect_evidence.py` | ✅ Functional | SHA-256 signing, evidence promotion |
| `playbooks/` | ✅ Complete | LLM01, LLM03, LLM08 + 2 attack chains |
| `reports/findings/` | 🔄 In progress | First finding being documented |

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
│   │   ├── requirements.txt
│   │   ├── prompts/
│   │   └── memory/             # Bind-mounted JSONL session store
│   │
│   ├── rag-pipeline/
│   │   ├── ingest.py
│   │   ├── rag_api.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── agent/
│       ├── agent.py
│       ├── Dockerfile
│       ├── requirements.txt
│       └── tools/              # tool.py + tool.schema.json pairs
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
│   └── collect_evidence.py     # artifacts/results/ → evidence/transcripts/
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
│   ├── transcripts/            # SHA-256 signed, promoted by collect_evidence.py
│   └── screenshots/
│
└── reports/
    ├── templates/
    │   └── finding-template.md
    └── findings/               # Completed reports: AI-SEC-YYYY-NNN.md
```

---

## Evidence pipeline

Automated output and audit-ready evidence are kept strictly separate:
```
attacks/*/payloads.json
  → tools/fuzzer.py
  → artifacts/results/          ← raw output, never cited directly
  → tools/collect_evidence.py   ← SHA-256 hash + metadata header
  → evidence/transcripts/       ← signed, reportable
  → reports/findings/           ← cites evidence ID
```

`collect_evidence.py` is the only mechanism that writes to `evidence/`.
Raw artifacts stay in `artifacts/results/` until reviewed and promoted.

---

## Quickstart

### Clone the repository
```bash
git clone https://github.com/Jeanmatozo/AI-security-training-lab.git
cd AI-security-training-lab
```

### Option 1 — Docker (recommended)

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

### Option 2 — Local, single environment (no Docker required)

**Prerequisites:** Python 3.10 or higher

**1. Copy the environment file**

From the repo root:
```bash
cp .env.example .env
```

Open `.env` and set your API key:
```bash
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

## Running attacks
```bash
# Run all prompt injection payloads against the chatbot
python tools/fuzzer.py \
  --payloads attacks/prompt-injection/payloads.json \
  --output   artifacts/results/PI_$(date +%Y%m%d_%H%M%S).json

# Promote results to signed evidence
python tools/collect_evidence.py \
  --input  artifacts/results/PI_20250115_143022.json \
  --output evidence/transcripts/
```

---

## Lab topics covered

- **Prompt injection** — direct injection, indirect injection via RAG, jailbreaks
- **RAG exploitation** — document poisoning, context manipulation, retrieval abuse
- **Agent tool abuse** — tool misuse, SSRF via HTTP tools, privilege escalation
- **Multi-step attack chains** — realistic adversarial sequences across environments

---

## Tools used

| Category | Technology |
|---|---|
| Language | Python |
| API framework | FastAPI |
| Containerisation | Docker + Docker Compose |
| LLM orchestration | LangChain |
| Vector store | ChromaDB |
| LLM provider | OpenAI API |
| Attack runner | `tools/fuzzer.py` (custom) |
| Evidence pipeline | `tools/collect_evidence.py` (custom) |

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
- [NIST AI Risk Management Framework](https://www.nist.gov/system/files/documents/2023/01/26/AI%20RMF%201.0.pdf)

Built by [jeanmatozo](https://github.com/Jeanmatozo)
