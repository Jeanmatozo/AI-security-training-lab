# AI-security-training-lab
A professional AI security training lab for hands-on testing of LLM, RAG, and agent-based systems, with attack playbooks, evidence capture, and reporting workflows.

This lab focuses on real-world vulnerabilities found in:

- Large Language Models (LLMs)
- Retrieval-Augmented Generation (RAG) systems
- AI Agents and tool-enabled models

The project includes vulnerable AI applications, attack playbooks, testing tools, and evidence collection workflows aligned with the **OWASP Top 10 for LLM Applications** and emerging **AI security best practices**.

The goal is to provide a **repeatable environment for learning and practicing AI security testing**.

---

## Repository structure
```bash
AI-security-training-lab/
├── README.md 
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml # chatbot + rag-pipeline + agent
│
├── environments/
│ ├── chatbot/
│ │ ├── app.py
│ │ ├── Dockerfile
│ │ ├── requirements.txt
│ │ ├── prompts/
│ │ └── memory/ # Bind-mounted JSONL session store
│ │
│ ├── rag-pipeline/
│ │ ├── ingest.py
│ │ ├── rag_api.py
│ │ ├── Dockerfile
│ │ └── requirements.txt
│ │
│ └── agent/
│ ├── agent.py
│ ├── Dockerfile
│ ├── requirements.txt
│ └── tools/ # web_search.py + .schema.json
│
├── attacks/
│ ├── README.md # Schema + ID prefix table (single source of truth)
│ ├── prompt-injection/
│ │ ├── payloads.json # Covers: direct, indirect, jailbreak, SPE
│ │ └── payloads.md
│ │
│ ├── rag-attacks/
│ │ ├── payloads.json
│ │ └── payloads.md
│ │
│ └── agent-attacks/
│ ├── payloads.json
│ └── payloads.md
│
├── tools/
│ ├── fuzzer.py # payloads.json → artifacts/results/
│ └── collect_evidence.py # artifacts/results/ → evidence/transcripts/
│
├── playbooks/
│ ├── LLM01-prompt-injection.md
│ ├── LLM03-training-data-poisoning.md
│ ├── LLM08-excessive-agency.md
│ └── chains/
│ ├── chain-01-rag-exfiltration.md
│ └── chain-02-agent-escalation.md
│
├── methodology/
│ └── attack-surface-map.md # OWASP coverage matrix
│
├── artifacts/
│ └── results/ # Raw run outputs from the fuzzer
│
└── evidence/
└── transcripts/ # Curated evidence extracted from artifacts

```
---

## Quickstart
The quickest way to begin is to clone the repository and run one of the lab environments.

## Clone the repository
```bash
git clone https://github.com/YOUR-USERNAME/AI-security-training-lab.git
cd AI-security-training-lab
```
## Local Setup   
**1. Install dependencies**
```bash
pip install -r requirements.txt
```
**2. Configure your environment**
Create a .env file based on the example template.
```bash
cp .env.example .env
```
**3. Add your OpenAI API Key**
Edit the .env file and add your API key.
Example:
```bash
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4.1-mini
```
**4. Run the Vulnerable Chatbot environment**  
Navigate to the chatbot environment:
```bash
cd environments/chatbot
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Start the server:
```bash
uvicorn app:app --reload
```
Open your browser and go to(it will open the API interface):
```bash
http://127.0.0.1:8000/docs
```
  This will launch a vulnerable chatbot environment, a FastAPI interactive Swagger UI,  that can be used to practice prompt injection and system prompt extraction attacks.

## Docker Setup
The lab can also be run using Docker, which provides a consistent and isolated environment.

This is the recommended approach for security labs.

Start the lab environment
```bash
docker-compose up --build
```
This will start all configured lab environments including:
- Vulnerable chatbot
- RAG pipeline
- AI agent
- Admin panel
- Stop the environment

---
### Lab Topics Covered
This training lab includes exercises for:   
- **Prompt Injection** - Direct and indirect prompt injection attacks.   
- **RAG Exploitation** - Manipulating retrieval pipelines and poisoning documents.   
- **System Prompt Extraction** - Techniques used to recover hidden system prompts.   
- **Agent Tool Abuse** - Attacking tool-enabled agents through tool misuse and privilege escalation.   
- **Multi-Step Attack Chains** - Simulating realistic adversarial workflows across AI systems.   

---
## Tools Used
This lab uses a combination of modern AI and security tooling.

Core technologies include:
- Python
- FastAPI
- Docker
- LangChain
- ChromaDB
- OpenAI API

Security testing utilities include custom scripts for:
- Prompt fuzzing
- System prompt extraction
- RAG poisoning
- Agent tool enumeration

---
## Contribution Guidelines
Contributions are welcome and encouraged.
If you would like to contribute:
1. Fork the repository
2. Create a new branch
3. Make your changes
4. Commit your changes
5. Push your branch
6. Submit a Pull Request
---
## Responsible Use
This repository is intended for **educational and defensive security research purposes only**.

All testing should be conducted in controlled environments and with proper authorization.

Do not use these techniques against systems without explicit permission.

---
## License

This project is licensed under the **MIT License**.

See the LICENSE file for details.

## Acknowledgements

This project is inspired by research and frameworks from:
- OWASP Top 10 for LLM Applications
- AI Red Team practices
- Security research communities working on AI safety and model robustness

Built by [jeanmatozo](https://github.com/Jeanmatozo)
