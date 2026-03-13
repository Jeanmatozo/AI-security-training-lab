# AI-security-training-lab
A professional AI security training lab for hands-on testing of LLM, RAG, and agent-based systems, with attack playbooks, evidence capture, and reporting workflows.

---

## Repository structure
```bash
AI-security-training-lab/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
│
├── environments/
│   ├── chatbot/
│   ├── rag-pipeline/
│   ├── agent/
│   └── admin-panel/
│
├── methodology/
│   ├── attack-surface-map.md
│   ├── threat-model.md
│   ├── testing-phases.md
│   └── rules-of-engagement.md
│
├── playbooks/
│   ├── LLM01-prompt-injection.md
│   ├── LLM02-insecure-output.md
│   ├── LLM03-data-poisoning.md
│   ├── LLM06-sensitive-disclosure.md
│   ├── LLM07-plugin-insecurity.md
│   ├── LLM08-excessive-agency.md
│   └── chains/
│       ├── chain-01-rag-exfil.md
│       ├── chain-02-agent-escalation.md
│       └── chain-03-memory-poison.md
│
├── attacks/
│   ├── prompt-injection/
│   ├── jailbreaks/
│   ├── system-prompt-extraction/
│   ├── rag-attacks/
│   └── agent-attacks/
│
├── evidence/
│   ├── transcripts/
│   ├── screenshots/
│   ├── logs/
│   └── collect_evidence.py
│
├── reports/
│   ├── templates/
│   ├── findings/
│   └── retest/
│
└── tools/
    ├── fuzzer.py
    ├── extractor.py
    ├── rag_poisoner.py
    └── agent_probe.py

```
