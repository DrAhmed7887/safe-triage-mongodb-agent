# Google Cloud Rapid Agent Hackathon — Submission Compliance Matrix

This document maps all hackathon rules and track requirements to the **SAFE-Triage Agent — MongoDB Track** project artifacts and checks compliance.

## 📋 Compliance Checklist

| Rule / Requirement | Project Implementation | Status | Details / Citations |
| :--- | :--- | :---: | :--- |
| **Public Repository** | [https://github.com/DrAhmed7887/safe-triage-mongodb-agent](https://github.com/DrAhmed7887/safe-triage-mongodb-agent) | **PASS** | Public repository with commit history, fully accessible. |
| **OSI-Approved License** | [LICENSE](../LICENSE) (MIT) | **PASS** | MIT License is present in the root and visible on GitHub. |
| **Live hosted URL** | [Live App](https://safe-triage-mongodb-api-566848331149.us-central1.run.app) | **PASS** | Deployed on Google Cloud Run; loads anonymously and serves both API and UI console. |
| **Demo Video** | Video link (YouTube/Vimeo) | **PENDING** | *User Action Required:* Record a $\le$3-min video showcasing the console using the [DEMO_SCRIPT.md](./DEMO_SCRIPT.md). |
| **Required Story Sections** | [DEVPOST_STORY.md](./DEVPOST_STORY.md) | **PASS** | Project description conforms to the exact Devpost prompts (Inspiration, What it does, How we built it, Challenges, Accomplishments, Learnings, Next steps). |
| **Google Cloud AI Only** | [triage_tool.py](../agent/triage_tool.py) | **PASS** | Uses **Gemini 2.0 Flash via Vertex AI** exclusively. Zero dependency on `google.generativeai`, `GEMINI_API_KEY`, or non-Google AI SDKs. |
| **Partner MCP Integration** | [mongodb_mcp_client.py](../agent/mongodb_mcp_client.py) | **PASS** | Integrates **MongoDB MCP Server** for triage cases logging and querying via `insert-many`, `find`, and `count` tools. |
| **Supported Platforms** | [index.html](../frontend/index.html) | **PASS** | Responsive Web App console UI optimized for desktop and mobile browsers. |
| **Selected Track** | Devpost Form selection | **PASS** | "MongoDB Track" selected in the Devpost submission project draft. |
| **No Committed Secrets** | Git check & `.env` verification | **PASS** | The Atlas connection URI resides in the Cloud Run configuration and gitignored local `.env`. No secrets are tracked. |

---

## 🔍 Specific Rule Verifications

### 1. Open Source License
* **Rule**: Submissions must license Non-Proprietary Aspects and source code under an OSI-approved license that does not limit commercial use.
* **Verification**: We have selected the **MIT License** (registered in [LICENSE](../LICENSE)). This is an OSI-approved permissive license that permits commercial reuse.

### 2. Live hosted URL
* **Rule**: Submission must include a live hosted, testable hosted URL.
* **Verification**: The console UI and the FastAPI backend are served under the single URL: `https://safe-triage-mongodb-api-566848331149.us-central1.run.app`. The page loads and runs triage cases without authentication.

### 3. Google Cloud / Vertex AI Usage
* **Rule**: Must use Google Cloud AI (Vertex AI / Gemini) only.
* **Verification**: `backend/main.py` and `agent/triage_tool.py` import `vertexai` to initialize and interact with Gemini 2.0 Flash. No prohibited API keys or alternative LLM providers are referenced.

### 4. MongoDB MCP Server Integration
* **Rule**: Integrate a Partner MCP server (MongoDB).
* **Verification**: The FastAPI backend acts as an MCP Host calling the MongoDB MCP server via the Python `mcp` SDK to write (`insert-many`) and query (`find` / `count`) triage logs.
