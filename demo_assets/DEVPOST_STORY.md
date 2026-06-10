# SAFE-Triage Agent — Devpost Hackathon Story

**Live Demo URL:** [https://safe-triage-mongodb-api-566848331149.us-central1.run.app](https://safe-triage-mongodb-api-566848331149.us-central1.run.app)  
**GitHub Repository:** [https://github.com/DrAhmed7887/safe-triage-mongodb-agent](https://github.com/DrAhmed7887/safe-triage-mongodb-agent)

## 🩺 Inspiration
In emergency departments, triage is the thin line between life and death. The Emergency Severity Index (ESI) is the standard 5-level protocol used to prioritize patients. While Large Language Models (LLMs) excel at processing complex unstructured complaints in native dialects, using raw AI for clinical classification introduces unacceptable risks of hallucination, omission, and under-triage. 

We built **SAFE-Triage Agent** to bridge this gap: combining the natural language extraction power of Google Cloud's Vertex AI (Gemini 2.0 Flash) with a deterministic ESI v5 rules engine. By enforcing clinical "safety floors", rules always override the AI. This guarantees that critical presentations (like cardiac arrests or strokes) are never under-triaged, even if the patient's description is vague or written in Egyptian Arabic dialect.

## 🧠 What it does
SAFE-Triage Agent processes patient clinical data (age, gender, unstructured chief complaint, and vital signs) and outputs:
1. **ESI Triage Level (1-5)** with corresponding safety coloring (Red, Orange, Yellow, Green, Blue).
2. **Bilingual Clinical Reasoning** (English + Egyptian Arabic).
3. **Safety Warnings & Floors** triggered by vital signs or specific red-flag keywords.
4. **Expected Resources** (e.g. labs, ECG, imaging) predicted for the clinical track.
5. A prominent **Clinician Authority Override Disclaimer** enforcing the system's role as a clinical assistant, not a final decision-maker.

The system features an active status dashboard and logs every triage record to a database using the **MongoDB MCP Server** with automatic, seamless fallback to native **pymongo**.

## 🛠️ How we built it
* **AI Feature Extraction**: We integrated **Gemini 2.0 Flash via Vertex AI** using Application Default Credentials (ADC), restricting the model's role strictly to symptom extraction and translation into bilingual reasoning.
* **Deterministic Rules Engine**: Created a hybrid engine implementing the standard ESI v5 guidelines. We added vital-sign safety floors (such as bradycardia/tachycardia, hypoxia, high blood pressure, and low GCS) and severe-pain protocols that automatically ceil ESI to levels 1 or 2.
* **Dialect NLP**: Built keyword matching for common Egyptian Arabic idioms representing critical symptoms (e.g., "بطني بتولع فيا" - *my stomach is burning* or "معدتي بتقطع" - *my stomach is cutting*).
* **MCP Integration**: Designed case persistence and lookup around the new **MongoDB MCP Server** protocol running over stdio, using the official Python MCP SDK to call `insert-many`, `find`, and `count` tools.
* **Graceful Fallbacks**: Created a multi-tier database fallback system. If the MCP Server stdio connection drops or is unconfigured, the system automatically routes queries through a native **pymongo** driver, and further down to an in-memory/mock handler if database access is fully offline.
* **Backend & Frontend**: Implemented using **FastAPI** in Python and a responsive, high-fidelity dark-mode clinical dashboard in HTML/JS.

## ⚠️ Challenges we ran into
A key challenge was compiling complex dependencies in standard cloud builder steps while ensuring the solution runs with zero compilation errors on newer Python installations. Another challenge was ensuring that the AI can never override a deterministic rule. To address this, we implemented the pipeline rule: **AI Extracts, Rules Decide, Humans Confirm**. The AI outputs features and structured descriptions, but the final ESI assignment is calculated deterministically via local Python rule sets.

## 🏆 Accomplishments that we're proud of
* **0% Critical Under-Triage**: Verified through our safety test suite running clinical cases; no critical patient (ESI 1 or 2) was ever downgraded.
* **Bilingual Arabic Dialect Handling**: Robust handling of Arabic symptoms and automatic RTL interface alignment.
* **Production-Grade MCP Integration**: Demonstrating a functional use case for the Model Context Protocol in clinical automation.

## 🎓 What we learned
We learned the power of standardizing agentic communication through MCP. Wrapping database drivers behind standard tool schemas enables decoupled, maintainable integrations that fit perfectly within broader agent workflows.

## 🚀 What's next for SAFE-Triage
In future iterations, we plan to support audio recording transcription for hands-free clinical input, direct integration with Electronic Health Records (EHR) schemas via MongoDB Time-Series collections, and multi-agent clinical consensus verification.

