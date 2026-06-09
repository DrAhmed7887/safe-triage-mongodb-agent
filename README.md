# SAFE-Triage Agent — MongoDB Track

A complete, submission-ready project for the **Google Cloud Rapid Agent Hackathon — MongoDB Track**. 
This codebase houses a hybrid clinical decision support system (CDSS) for emergency department triage, integrating standard ESI v5 guidelines, Vertex AI (Gemini 2.0 Flash) reasoning models, and MongoDB Atlas persistence.

---

### Tech Stack & Architecture
1. **Clinical Layer**: ESI v5 + NEWS2 clinical override rules.
2. **AI Layer**: Gemini 2.0 Flash via **Vertex AI** for advanced clinical reasoning.
3. **Database Layer**: **MongoDB Atlas** for secure patient triage history logging, querying, and seeding.
4. **API Gateway**: **FastAPI** backend supporting POST `/triage`, GET `/cases`, and GET `/health` endpoints.
5. **Deployment**: Prepared configuration for **Google Cloud Run** with custom substitutions.
6. **Frontend**: Clean, single-page reactive dashboard with CSS variables, gradient headers, and visual ESI metrics.

---

### Clinical Safety & Legal Disclaimer
> [!IMPORTANT]
> **RESEARCH PROTOTYPE ONLY**
> This system is built as a research prototype and demonstration of agentic AI technology. It is **not a certified medical device**, has not been cleared for diagnostic use by the FDA or the Egyptian Ministry of Health, and must never be used as a standalone decision-maker. The **clinician retains final authority and absolute oversight** over all emergency department triage levels assigned to patients.

---

### Getting Started

#### 1. Setup Environment
Copy the example environment config and fill in your details:
```bash
cp .env.example .env
```
Ensure you provide your Vertex AI credentials (via `gcloud auth application-default login` or service account keys), GCP Project ID, and your MongoDB Atlas Connection URI.

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Run FastAPI Locally
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
```

#### 4. Seed MongoDB
Run the seeding script to load standard test scenarios into MongoDB:
```bash
python scripts/seed_mongodb.py
```
---

### Submission File Registry

| File / Folder Path | Description | Size |
|---|---|---|
| `agent/main_agent.py` | Google Cloud Agent Builder entrypoint | 1.8 KB |
| `agent/triage_tool.py` | Core Gemini triage evaluation logic + safety floors | 5.2 KB |
| `agent/prompts.py` | Vertex AI Generative Model system prompt and disclaimer | 0.8 KB |
| `backend/main.py` | FastAPI app gateway (triage, cases database query, health checks) | 4.5 KB |
| `backend/models.py` | Shared clinical and identification schemas | 8.5 KB |
| `backend/mongodb_client.py` | Connection client with pymongo commands | 3.5 KB |
| `backend/mimic_loader.py` | Parser helper for demo dataset | 0.6 KB |
| `data/demo_cases.json` | 12 real clinical scenarios (including 2 Arabic dialect cases) | 4.8 KB |
| `frontend/index.html` | Pure CSS + HTML5 responsive triage console UI | 11.2 KB |
| `scripts/seed_mongodb.py` | Command line script to seed cases to MongoDB | 0.8 KB |
| `Dockerfile` | Multi-stage image build config for Cloud Run deployment | 0.4 KB |
| `cloudbuild.yaml` | Cloud Build automation steps | 0.7 KB |
| `requirements.txt` | Pinned python libraries | 0.2 KB |
| `LICENSE` | Open-source MIT template | 1.1 KB |
