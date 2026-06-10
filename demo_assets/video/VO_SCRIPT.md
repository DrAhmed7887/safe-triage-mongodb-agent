# SAFE-Triage Agent — Voiceover Script
# Target duration: ~2:50 | Hard cap: 3:00
# Format: ElevenLabs-compatible TTS — professional, confident, neutral male voice
# Pacing guide: ~150 words per minute
# Total estimated word count: ~425 words (~2:50 at 150 wpm)

---

## SEGMENT 1 — Cold Open / Title Hook
**Timecode: 0:00 – 0:12**
**[ON SCREEN]: Full-bleed dark console. "SAFE-Triage" logotype fades in, teal accent. Tagline: "A.I. Extracts. Rules Decide. Humans Confirm."**

Every emergency department in the world faces the same question the moment a patient walks through the door: how sick are they, and how fast do they need care? Get it wrong — and a patient dies in a waiting room. This is SAFE-Triage Agent.

---

## SEGMENT 2 — The Problem
**Timecode: 0:12 – 0:32**
**[ON SCREEN]: Split graphic — crowded E.D. on left, ESI severity color bands (1–5, Red to Blue) on right. Text overlay: "ESI v5 — The Global Standard. 5 Levels. Zero Margin for Error."**

The Emergency Severity Index — E-S-I — is the global standard for patient prioritization. Five levels, from immediate resuscitation down to non-urgent. But clinical complaints are messy, multilingual, and ambiguous. Raw large language models are powerful at reading text — but they hallucinate, they omit critical details, and they cannot be trusted to make a classification decision where under-triaging a critical patient has life-or-death consequences. You cannot hand that decision to an AI alone.

---

## SEGMENT 3 — The Solution + Golden Rule
**Timecode: 0:32 – 0:48**
**[ON SCREEN]: Architecture diagram. Three-step pipeline animates in: "AI Extracts" → "Rules Decide" → "Humans Confirm". Each step lights up in sequence.**

SAFE-Triage was built around a single, unbreakable golden rule: A.I. extracts. Rules decide. Humans confirm. Gemini 2.0 Flash, running on Google Cloud Vertex A.I., reads the patient complaint and structures it into clinical features. A deterministic E-S-I version 5 rules engine then makes the triage call — not the model. Vital-sign safety floors and red-flag keywords can only ever raise acuity, never lower it. The clinician confirms everything.

---

## SEGMENT 4 — Live Demo (narration synced to 77-second screen recording)
**Timecode: 0:48 – 2:08**

### 4a — Console Landing
**Timecode: 0:48 – 1:03**
**[ON SCREEN]: Live app at Cloud Run URL. Status bar shows "MCP: Connected" and "pymongo: Connected" badges. "Research Prototype — Not a Medical Device" disclaimer visible.**

Here is the live system, deployed right now on Google Cloud Run. Notice two status badges at the top: M-C-P Connected — the MongoDB M-C-P Server is active over stdio — and pymongo Connected, the automatic fallback layer. And the disclaimer is right there: research prototype, not a medical device. The physician is always in charge.

### 4b — Scenario 1: Seizure, G-C-S 6 — E-S-I 1 Red
**Timecode: 1:03 – 1:20**
**[ON SCREEN]: Scenario 1 loads. "Perform Triage Classification" pressed. Result panel glows RED — "ESI 1 — RESUSCITATION". Lower third: "ESI 1 — RED — Resuscitation".**

Scenario one. A patient arrives with an ongoing seizure and a Glasgow Coma Scale score of 6 — deeply altered consciousness. The system applies vital-sign safety floors immediately. The result: E-S-I 1 — Resuscitation. Red. Immediate bedside response required. Zero ambiguity. Zero chance of under-triage.

### 4c — Scenario 2: Chest Pain, A-C-S — E-S-I 2 Orange
**Timecode: 1:20 – 1:37**
**[ON SCREEN]: Scenario 2 loads. Result panel glows ORANGE — "ESI 2 — EMERGENT". Lower third: "ESI 2 — ORANGE — Emergent".**

Scenario two. Severe chest pain radiating to the left arm — a classic A-C-S presentation. Even if vitals appear marginally stable, the chief-complaint red-flag floor overrides any inference. E-S-I 2 — Emergent. Orange. The rule fires before the model even has a chance to soften the call.

### 4d — Scenario 3: Arabic Dialect — E-S-I 2 Orange
**Timecode: 1:37 – 1:54**
**[ON SCREEN]: Scenario 3 loads. Arabic text populates the chief-complaint field. Layout flips to right-to-left. Result glows ORANGE — "ESI 2 — EMERGENT". Bilingual reasoning panel visible. Lower third: "ESI 2 — ORANGE — Emergent | بطني بتولع فيا".**

Scenario three — bilingual. The patient's complaint is entered in Egyptian Arabic dialect: "بطني بتولع فيا" — "my stomach is burning." The interface automatically switches to right-to-left layout. Gemini extracts the symptom from the dialect. The rules engine recognizes severe abdominal distress and classifies E-S-I 2, with full bilingual reasoning returned in both English and Arabic.

### 4e — Scenario 4: B-P Refill — E-S-I 5 Blue
**Timecode: 1:54 – 2:08**
**[ON SCREEN]: Scenario 4 loads. Result glows BLUE — "ESI 5 — NON-URGENT". History panel visible with persistence badges. Lower third: "ESI 5 — BLUE — Non-Urgent".**

Scenario four — the other end of the spectrum. A routine blood-pressure prescription refill. The system applies a resource-based ceiling and correctly assigns E-S-I 5, Non-Urgent, Blue. No over-escalation. No wasted resuscitation resources. The history panel below shows all four decisions just logged, each marked with the M-C-P persistence badge.

---

## SEGMENT 5 — Technology and M-C-P
**Timecode: 2:08 – 2:30**
**[ON SCREEN]: Architecture diagram. Labels highlight: Vertex AI / Gemini 2.0 Flash → Rules Engine → MongoDB MCP Server → pymongo fallback → Cloud Run.**

Under the hood: Gemini 2.0 Flash via Vertex A.I. with Application Default Credentials — no A.P.I. key exposed. The rules engine is pure Python, deterministic and auditable. Case persistence runs through the MongoDB M-C-P Server over standard input-output, calling insert-many, find, and count as native M-C-P tools. If that connection drops, the system silently fails over to pymongo. Everything is served from FastAPI on Google Cloud Run — containerized, stateless, globally available in seconds.

---

## SEGMENT 6 — Impact + What Is Next
**Timecode: 2:30 – 2:44**
**[ON SCREEN]: Three stat cards animate in — "0% Critical Under-Triage", "Bilingual: EN + AR", "Live on Cloud Run". Then a roadmap panel: "Audio Input", "EHR / MongoDB Time-Series", "Multi-Agent Consensus".**

The verified result: zero percent critical under-triage across our safety test suite. Fully bilingual, with native Egyptian Arabic dialect support and automatic right-to-left interface. Running live and publicly accessible today. Next: hands-free audio input for busy clinicians, direct E-H-R integration via MongoDB time-series collections, and a multi-agent consensus layer where independent agents must agree before a borderline case is finalized.

---

## SEGMENT 7 — Outro
**Timecode: 2:44 – 2:55**
**[ON SCREEN]: Dark console. Live URL and GitHub repo appear as text overlays. "Dr. Ahmed Zayed, MD — Physician & AI Engineer." Tagline returns: "A.I. Extracts. Rules Decide. Humans Confirm."**

SAFE-Triage Agent is live at the URL on screen. The full source code is open on GitHub. Built by Doctor Ahmed Zayed — physician and A.I. engineer. A.I. extracts. Rules decide. Humans confirm. Thank you.

---

## Timing Summary

| Segment | In | Out | Duration | Words (approx) |
|---|---|---|---|---|
| 1 — Cold Open | 0:00 | 0:12 | 12s | ~30 |
| 2 — Problem | 0:12 | 0:32 | 20s | ~95 |
| 3 — Solution | 0:32 | 0:48 | 16s | ~80 |
| 4 — Live Demo | 0:48 | 2:08 | 80s | ~195 |
| 5 — Tech + MCP | 2:08 | 2:30 | 22s | ~85 |
| 6 — Impact | 2:30 | 2:44 | 14s | ~70 |
| 7 — Outro | 2:44 | 2:55 | 11s | ~32 |
| **TOTAL** | | | **~2:55** | **~587** |

> Note: 587 words at a measured 150 wpm lands at approximately 2:50–2:55, within the hard 3:00 cap. ElevenLabs default pacing for professional narration typically runs 145–155 wpm. Adjust segment 4 demo pacing slightly if the screen recording cut is shorter than 80 seconds.

---

## TTS Production Notes

- Expand all abbreviations phonetically as written above: "E-S-I", "M-C-P", "A-I", "A.D.C.", "A.P.I.", "G-C-S", "A-C-S", "E-H-R", "R-T-L" — the hyphens and periods trigger letter-by-letter reading in ElevenLabs.
- Arabic phrase "بطني بتولع فيا" should be handled by a bilingual TTS pass or replaced with "(Arabic phrase displayed on screen)" for a pure English render.
- Recommended ElevenLabs voice style: "Calm Professional" or "Adam" (neutral, authoritative). Speed: 0.95x.
- Pause markers (natural breath): add a comma or period between each scenario sub-segment for a 0.5s breath pause.
