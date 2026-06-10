# SAFE-Triage Agent — HyperFrames (HeyGen) Prompt-to-Video Brief
# Paste this entire document into the HyperFrames agent prompt field.
# The VO script is embedded verbatim in Section 6 below.

---

## 1. PROJECT OVERVIEW

Create a ~2:50 submission video for SAFE-Triage Agent, a research-stage bilingual emergency-department triage system built for the Google Cloud Rapid Agent Hackathon (MongoDB track). The video is narrated, professionally paced, and ends on a live demo hosted on Google Cloud Run.

The final video must be under 3:00 hard cap.

---

## 2. BRAND IDENTITY

Apply these design tokens consistently across all text, backgrounds, overlays, and lower-thirds:

| Token | Value | Usage |
|---|---|---|
| Background | #0A0E14 (near-black) | All slide backgrounds, overlays |
| Primary accent | #14F1C8 (teal/cyan) | Headlines, active state highlights, progress bar |
| Secondary accent | #FFB020 (amber) | Data callouts, warning badges, stat cards |
| Danger red | #FF4444 | ESI 1 result card, "ESI 1 — RED" badge |
| Warning orange | #FF8C00 | ESI 2 result card, "ESI 2 — ORANGE" badge |
| Blue calm | #4A90D9 | ESI 5 result card, "ESI 5 — BLUE" badge |
| Body text | #C8D6E5 (light grey) | All body copy, captions |
| Monospace data | #14F1C8 on #0A0E14 | Code snippets, tool calls, status badges |
| Heading typeface | Space Grotesk Bold (or Inter Bold as fallback) | All headlines and segment titles |
| Data / code typeface | JetBrains Mono (or Roboto Mono as fallback) | MCP tool names, ESI classifications, tech labels |

No white backgrounds. No bright gradients. The aesthetic is a dark clinical AI console — precise, authoritative, futuristic but not frivolous.

---

## 3. NARRATOR

- Professional neutral male English voice. Calm, confident, clinical authority. Not overly enthusiastic.
- Pace: ~150 words per minute (measured, not rushed).
- Accent: Standard American English.
- Use the voiceover script verbatim as provided in Section 6 of this brief.
- Do NOT paraphrase or abbreviate the script.

---

## 4. VIDEO STRUCTURE — 7 SEGMENTS

Build the video in exactly 7 segments as described below. Each segment has a timecode, a visual brief, and corresponding VO text (see Section 6 for full script).

### SEGMENT 1 — Cold Open / Title Hook (0:00 – 0:12, ~12 seconds)

Visual: Full bleed #0A0E14 background. The "SAFE-Triage" logotype fades in centered, in Space Grotesk Bold teal (#14F1C8). Below it, after 2 seconds, the tagline animates in letter-by-letter: "A.I. Extracts. Rules Decide. Humans Confirm." in amber (#FFB020). Subtle particle or heartbeat-line animation in the background. No footage — motion-graphic title card only.

Lower-third: None for this segment.

---

### SEGMENT 2 — The Problem (0:12 – 0:32, ~20 seconds)

Visual: Split screen. Left half: abstract, desaturated image of a crowded emergency department (use a stock photo or illustrative graphic). Right half: the ESI 5-level color stack — five horizontal bars labeled ESI 1 RED / ESI 2 ORANGE / ESI 3 YELLOW / ESI 4 GREEN / ESI 5 BLUE — each bar in the corresponding brand color variant on the dark background. These bars animate in one by one from top to bottom as the narrator speaks. Text overlay at top: "The Emergency Severity Index — 5 Levels. Zero Margin for Error." in Space Grotesk Bold, teal.

Lower-third: "ESI v5 — The Global Standard" in amber.

---

### SEGMENT 3 — Solution + Golden Rule (0:32 – 0:48, ~16 seconds)

Visual: Architecture diagram slide (use the architecture diagram asset listed in Section 7 if provided, otherwise generate a three-node pipeline graphic). Three labeled nodes appear in sequence, each lighting up in teal as the narrator names it:

Node 1: "AI Extracts" — icon: brain / neural net
Node 2: "Rules Decide" — icon: checkmark / logic gate
Node 3: "Humans Confirm" — icon: clinician / stethoscope

Connecting arrows in teal. Below the pipeline: "Gemini 2.0 Flash via Vertex AI + Deterministic ESI v5 Rules Engine" in monospace teal text.

Lower-third: "The Golden Rule: A.I. Extracts → Rules Decide → Humans Confirm"

---

### SEGMENT 4 — Live Demo (0:48 – 2:08, ~80 seconds)

IMPORTANT — READ THIS SECTION CAREFULLY.

An 80-second real screen recording of the live product (demo_video.mp4) will be composited into this segment. Leave an explicit 80-second hole labeled [PRODUCT DEMO FOOTAGE — INSERT HERE] at timecode 0:48–2:08.

During the demo hole, overlay ONLY the following elements (do not obscure the UI):
- A thin teal border frame around the video viewport.
- In the top-left corner: a semi-transparent dark pill badge reading "LIVE — Cloud Run" in amber.
- At the bottom of the screen: animated lower-thirds that appear at the following sub-timecodes, each for approximately 15 seconds:

| Sub-timecode | Lower-third text | Accent color |
|---|---|---|
| 0:48 – 1:03 | "MCP: Connected | pymongo: Connected | Research Prototype" | Teal |
| 1:03 – 1:20 | "ESI 1 — RED — Resuscitation" | #FF4444 red |
| 1:20 – 1:37 | "ESI 2 — ORANGE — Emergent" | #FF8C00 orange |
| 1:37 – 1:54 | "ESI 2 — ORANGE — Emergent | بطني بتولع فيا" | #FF8C00 orange |
| 1:54 – 2:08 | "ESI 5 — BLUE — Non-Urgent | MCP Persistence Active" | #4A90D9 blue |

If the HeyGen agent cannot composite external footage, replace the 80-second hole with a slideshow of the four scenario screenshots (provided in Section 7 as ASSETS), one per sub-segment, each displayed for approximately 15 seconds with a subtle zoom-in Ken Burns effect. The lower-thirds above still apply to the corresponding screenshot.

VO for this segment is fully scripted in Section 6 (Segment 4, sub-segments 4a through 4e).

---

### SEGMENT 5 — Technology and MCP (2:08 – 2:30, ~22 seconds)

Visual: The architecture diagram asset (Section 7) displayed full-width. As the narrator names each component, a teal highlight or callout box animates around that component in sequence: Vertex AI / Gemini 2.0 Flash → Python Rules Engine → MongoDB MCP Server (stdio) → pymongo fallback → FastAPI → Cloud Run. Each label appears in monospace teal text as it is highlighted.

Lower-third: "Stack: Vertex AI · MongoDB MCP Server · FastAPI · Google Cloud Run"

---

### SEGMENT 6 — Impact + What Is Next (2:30 – 2:44, ~14 seconds)

Visual: Three stat cards animate in from left to right on the dark background, each with an amber border and teal headline value:

Card 1: "0%" headline / "Critical Under-Triage" subtext
Card 2: "EN + AR" headline / "Bilingual Dialect Support" subtext
Card 3: "LIVE" headline / "Google Cloud Run" subtext

After 8 seconds, cards fade and a "What's Next" roadmap row appears with three amber-labeled items:
- "Audio Input — Hands-Free Clinical Triage"
- "EHR Integration — MongoDB Time-Series"
- "Multi-Agent Consensus Verification"

Lower-third: "Verified: 0% Critical Under-Triage | Research Prototype Stage"

---

### SEGMENT 7 — Outro (2:44 – 2:55, ~11 seconds)

Visual: Return to the dark console aesthetic from Segment 1. Two lines of text appear centered:

Line 1 (teal, Space Grotesk Bold): "https://safe-triage-mongodb-api-566848331149.us-central1.run.app"
Line 2 (grey, smaller): "github.com/DrAhmed7887/safe-triage-mongodb-agent"

Below those, after 2 seconds: "Dr. Ahmed Zayed, MD — Physician & AI Engineer" in amber.

Final frame (last 3 seconds): tagline returns — "A.I. Extracts. Rules Decide. Humans Confirm." — teal, centered, fades to black.

Lower-third: None — let the URL and credits speak alone.

---

## 5. GLOBAL PRODUCTION NOTES

- Aspect ratio: 16:9, 1080p minimum.
- Transitions: cut or 12-frame cross-dissolve only. No wipes, no spins, no zoom-punch transitions. Clinical precision aesthetic.
- Background music (optional, low): ambient dark electronic instrumental, -18 dB under VO, fade out on outro. If no music is available, silence is preferred over inappropriate stock music.
- Captions: auto-generated captions from the VO script are acceptable but must be reviewed for accuracy on all abbreviations (E-S-I, M-C-P, G-C-S, A-C-S, E-H-R). Place captions at the bottom in JetBrains Mono, 90% opacity white text on a semi-transparent dark pill.
- No stock footage of hospitals, patients, or medical procedures. Stick to abstract or data-visualization-style visuals for all non-demo segments.
- The "Research Prototype — Not a Medical Device" disclaimer must be visible at least once on screen (it appears naturally in the demo footage; if using screenshots, display it as a text overlay during Segment 4a).

---

## 6. VOICEOVER SCRIPT (VERBATIM — DO NOT MODIFY)

---

### SEGMENT 1 (0:00 – 0:12)

Every emergency department in the world faces the same question the moment a patient walks through the door: how sick are they, and how fast do they need care? Get it wrong — and a patient dies in a waiting room. This is SAFE-Triage Agent.

---

### SEGMENT 2 (0:12 – 0:32)

The Emergency Severity Index — E-S-I — is the global standard for patient prioritization. Five levels, from immediate resuscitation down to non-urgent. But clinical complaints are messy, multilingual, and ambiguous. Raw large language models are powerful at reading text — but they hallucinate, they omit critical details, and they cannot be trusted to make a classification decision where under-triaging a critical patient has life-or-death consequences. You cannot hand that decision to an AI alone.

---

### SEGMENT 3 (0:32 – 0:48)

SAFE-Triage was built around a single, unbreakable golden rule: A.I. extracts. Rules decide. Humans confirm. Gemini 2.0 Flash, running on Google Cloud Vertex A.I., reads the patient complaint and structures it into clinical features. A deterministic E-S-I version 5 rules engine then makes the triage call — not the model. Vital-sign safety floors and red-flag keywords can only ever raise acuity, never lower it. The clinician confirms everything.

---

### SEGMENT 4a (0:48 – 1:03)

Here is the live system, deployed right now on Google Cloud Run. Notice two status badges at the top: M-C-P Connected — the MongoDB M-C-P Server is active over stdio — and pymongo Connected, the automatic fallback layer. And the disclaimer is right there: research prototype, not a medical device. The physician is always in charge.

---

### SEGMENT 4b (1:03 – 1:20)

Scenario one. A patient arrives with an ongoing seizure and a Glasgow Coma Scale score of 6 — deeply altered consciousness. The system applies vital-sign safety floors immediately. The result: E-S-I 1 — Resuscitation. Red. Immediate bedside response required. Zero ambiguity. Zero chance of under-triage.

---

### SEGMENT 4c (1:20 – 1:37)

Scenario two. Severe chest pain radiating to the left arm — a classic A-C-S presentation. Even if vitals appear marginally stable, the chief-complaint red-flag floor overrides any inference. E-S-I 2 — Emergent. Orange. The rule fires before the model even has a chance to soften the call.

---

### SEGMENT 4d (1:37 – 1:54)

Scenario three — bilingual. The patient's complaint is entered in Egyptian Arabic dialect: "بطني بتولع فيا" — "my stomach is burning." The interface automatically switches to right-to-left layout. Gemini extracts the symptom from the dialect. The rules engine recognizes severe abdominal distress and classifies E-S-I 2, with full bilingual reasoning returned in both English and Arabic.

---

### SEGMENT 4e (1:54 – 2:08)

Scenario four — the other end of the spectrum. A routine blood-pressure prescription refill. The system applies a resource-based ceiling and correctly assigns E-S-I 5, Non-Urgent, Blue. No over-escalation. No wasted resuscitation resources. The history panel below shows all four decisions just logged, each marked with the M-C-P persistence badge.

---

### SEGMENT 5 (2:08 – 2:30)

Under the hood: Gemini 2.0 Flash via Vertex A.I. with Application Default Credentials — no A.P.I. key exposed. The rules engine is pure Python, deterministic and auditable. Case persistence runs through the MongoDB M-C-P Server over standard input-output, calling insert-many, find, and count as native M-C-P tools. If that connection drops, the system silently fails over to pymongo. Everything is served from FastAPI on Google Cloud Run — containerized, stateless, globally available in seconds.

---

### SEGMENT 6 (2:30 – 2:44)

The verified result: zero percent critical under-triage across our safety test suite. Fully bilingual, with native Egyptian Arabic dialect support and automatic right-to-left interface. Running live and publicly accessible today. Next: hands-free audio input for busy clinicians, direct E-H-R integration via MongoDB time-series collections, and a multi-agent consensus layer where independent agents must agree before a borderline case is finalized.

---

### SEGMENT 7 (2:44 – 2:55)

SAFE-Triage Agent is live at the URL on screen. The full source code is open on GitHub. Built by Doctor Ahmed Zayed — physician and A.I. engineer. A.I. extracts. Rules decide. Humans confirm. Thank you.

---

## 7. ASSETS

Paste the public URLs into the slots below before submitting this brief to HyperFrames. All assets live in the demo_assets/ directory of the repository.

| Asset | Description | URL (paste here) |
|---|---|---|
| demo_video.mp4 | 77-second silent product demo recording | https://raw.githubusercontent.com/DrAhmed7887/safe-triage-mongodb-agent/main/demo_assets/demo_video.mp4 |
| empty_form.png | Console landing — MCP + pymongo badges visible | https://raw.githubusercontent.com/DrAhmed7887/safe-triage-mongodb-agent/main/demo_assets/Approved/empty_form.png |
| scenario_1_esi_1_seizure.png | Seizure ESI 1 RED result | https://raw.githubusercontent.com/DrAhmed7887/safe-triage-mongodb-agent/main/demo_assets/Approved/scenario_1_esi_1_seizure.png |
| scenario_2_esi_2_chest_pain.png | Chest Pain ESI 2 ORANGE result | https://raw.githubusercontent.com/DrAhmed7887/safe-triage-mongodb-agent/main/demo_assets/Approved/scenario_2_esi_2_chest_pain.png |
| scenario_3_esi_2_arabic_abdominal.png | Arabic RTL ESI 2 ORANGE result | https://raw.githubusercontent.com/DrAhmed7887/safe-triage-mongodb-agent/main/demo_assets/Approved/scenario_3_esi_2_arabic_abdominal.png |
| scenario_4_esi_5_bp_refill.png | BP Refill ESI 5 BLUE + history panel | https://raw.githubusercontent.com/DrAhmed7887/safe-triage-mongodb-agent/main/demo_assets/Approved/scenario_4_esi_5_bp_refill.png |
| architecture.png | Full system architecture diagram | https://raw.githubusercontent.com/DrAhmed7887/safe-triage-mongodb-agent/main/demo_assets/Approved/architecture.png |

Raw GitHub asset URLs follow the pattern:
https://raw.githubusercontent.com/DrAhmed7887/safe-triage-mongodb-agent/main/demo_assets/Approved/[filename]

The demo video raw URL:
https://raw.githubusercontent.com/DrAhmed7887/safe-triage-mongodb-agent/main/demo_assets/demo_video.mp4

---

## 8. FINAL DELIVERABLE SPEC

- Format: MP4, H.264, 1080p 16:9
- Duration: 2:50 – 3:00 (hard cap)
- Output filename: SAFE_Triage_Hackathon_Submission_v1.mp4
- End card must include: live URL + GitHub repo URL + creator credit
- Deliver one master file; no chapter markers needed

---

*Brief prepared for HyperFrames / HeyGen prompt-to-video pipeline.*
*SAFE-Triage is a research prototype. All claims in this brief are verified against the project's safety test suite and public codebase.*
*Dr. Ahmed Zayed, MD — Physician & AI Engineer.*
