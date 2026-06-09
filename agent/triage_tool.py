import os
import json
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from agent.models import PatientInput, TriageResult, TriageLevel, Vitals

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Chief-complaint red-flag keyword sets (EN + Egyptian Arabic)
# Derived from esi_v5_engine.py safety floors and arabic_keywords_v2.py
# ---------------------------------------------------------------------------

# Cardiac / ACS: chest pain, pressure, tightness, radiation to arm/jaw
_RF_CARDIAC = {
    # English
    "chest pain", "chest pressure", "chest tightness", "chest discomfort",
    "chest ache", "angina",
    "radiating to arm", "radiating to left arm", "radiating to jaw",
    "radiation to arm", "radiation to jaw",
    "left arm pain", "left jaw pain",
    # Arabic (Egyptian + MSA)
    "صدري", "ألم صدر", "الم صدر", "وجع في الصدر", "وجع صدر",
    "وجع في صدري", "ضغط على صدري", "ضيقة في الصدر",
    "صدري بيضغط عليا", "حاسس بتقل على صدري",
    "الألم بيمشي لدراعي", "الألم بينتشر لدراعي",
    "صدري بيوجعني", "حرقان صدر",
}

# Stroke / FAST: face droop, arm weakness, slurred speech, sudden numbness
_RF_STROKE = {
    # English
    "face droop", "facial droop", "face drooping", "facial asymmetry",
    "facial droop", "arm weakness", "arm drift",
    "slurred speech", "speech difficulty", "difficulty speaking",
    "unable to speak", "can't speak", "aphasia", "dysarthria",
    "sudden numbness", "sudden weakness", "one side weakness",
    "hemiparesis", "hemiplegia",
    "stroke", "cva",
    # Arabic
    "وشه مايل", "وشي مايل", "وشه اتلوى", "وشي اتلوى",
    "مش قادر يرفع إيده", "مش قادر يرفع دراعه",
    "كلامه متلخبط", "لسانه تقيل", "مش قادر يتكلم",
    "مش عارف يتكلم", "بيتكلم غريب",
    "نص جسمي مش بيتحرك", "نص وشه",
    "ضعف في الجنب الشمال", "جلطة دماغية", "جلطة في المخ",
}

# Respiratory distress: severe shortness of breath, can't breathe
_RF_RESPIRATORY = {
    # English
    "can't breathe", "cannot breathe", "unable to breathe",
    "severe shortness of breath", "shortness of breath",
    "difficulty breathing", "respiratory distress", "choking",
    "airway obstruction",
    # Arabic
    "مش قادر يتنفس", "مش قادر أتنفس", "نفسه واقف",
    "مش قادر اخد نفس", "مش قادر أخد نفسي",
    "نفسي ضيق", "ضيق نفس",
    "مش عارف أتنفس", "بيتخنق", "كتمة",
    "النفس مقطوع", "نفسي واقف",
}

# Anaphylaxis / severe allergic reaction
_RF_ANAPHYLAXIS = {
    # English
    "throat swelling", "tongue swelling", "airway swelling",
    "anaphylaxis", "anaphylactic",
    "severe allergic", "allergic reaction",
    # Arabic
    "حساسية شديدة", "زوري بيقفل", "لساني ورم",
    "حساسية وضيق نفس", "تورم الحلق", "تورم اللسان",
}

# Severe abdominal pain — including the case 11/12 Egyptian idioms
_RF_ABDOMINAL_SEVERE = {
    # English
    "stomach burning", "burning stomach", "stomach cutting",
    "stomach is burning", "stomach is cutting", "burning inside",
    "severe abdominal pain", "severe stomach pain",
    # Arabic — case 11/12 idioms (substring match needed for some)
    "بطني بتولع", "بطني بتقطع", "معدتي بتقطع",
    "بطني نار", "مغص جامد", "بطني متحجرة",
    "بطني بتولع فيا",
}

# Active major hemorrhage
_RF_HEMORRHAGE = {
    # English
    "massive bleeding", "major hemorrhage", "active hemorrhage",
    "uncontrolled bleeding", "bleeding won't stop",
    "vomiting blood", "blood in vomit",
    # Arabic
    "نزيف مش بيوقف", "بستفرغ دم", "نزيف شديد",
    "دم ما يقفش",
}

# Altered mental status / loss of consciousness
_RF_AMS = {
    # English
    "altered mental status", "loss of consciousness", "unresponsive",
    "not responding", "syncope", "unconscious",
    # Arabic
    "أغمى عليا", "فقدت وعيي", "غيبوبة",
    "مش بيرد", "مش واعي",
}

# Suicidal / self-harm / overdose
_RF_SUICIDAL_OD = {
    # English
    "suicidal", "suicide attempt", "overdose", "took pills",
    "ingested pills", "self harm", "wants to die",
    # Arabic
    "عايز أموت", "بلعت حبوب", "شربت كلور", "محاولة انتحار",
    "أفكار انتحار",
}

# All red-flag sets mapped to a readable label (for reasoning strings)
_RED_FLAG_SETS: List[tuple] = [
    (_RF_CARDIAC,          "Cardiac / ACS red flag",          "علامة تحذيرية قلبية / متلازمة الشريان التاجي"),
    (_RF_STROKE,           "Stroke / FAST red flag",           "علامة تحذيرية سكتة دماغية / بروتوكول FAST"),
    (_RF_RESPIRATORY,      "Severe respiratory distress",      "ضائقة تنفسية شديدة"),
    (_RF_ANAPHYLAXIS,      "Anaphylaxis / severe allergic",    "صدمة تحسسية / حساسية شديدة"),
    (_RF_ABDOMINAL_SEVERE, "Severe abdominal pain red flag",   "ألم بطني شديد - علامة تحذيرية"),
    (_RF_HEMORRHAGE,       "Active major hemorrhage",          "نزيف حاد نشط"),
    (_RF_AMS,              "Altered mental status / LOC",      "اضطراب الوعي / فقدان الوعي"),
    (_RF_SUICIDAL_OD,      "Suicidal / overdose",              "أفكار انتحارية / جرعة زائدة"),
]

# System Prompts for Triage Reasoning (Gemini 2.0 Flash via Vertex AI)
SYSTEM_PROMPT = """You are an expert emergency department triage officer.
Your task is to analyze patient cases and provide clinical reasoning to assign an Emergency Severity Index (ESI) triage level (1 to 5).
You must follow the standard ESI v5 guidelines:
- ESI 1: Requires immediate life-saving intervention (e.g. cardiac arrest, respiratory arrest, severe trauma, anaphylaxis).
- ESI 2: High risk situation, confused/lethargic/disoriented, or severe pain/distress.
- ESI 3: Stable, but requires multiple resources (e.g. labs + ECG + imaging).
- ESI 4: Stable, requires one resource (e.g. x-ray or sutures).
- ESI 5: Stable, requires no resources (e.g. prescription refill, stitch removal).

You MUST output your clinical reasoning and recommended ESI level strictly in JSON format matching the schema requested.

SAFETY DISCLAIMER (MUST BE AT THE END OF EVERY RESPONSE):
Disclaimer: This is a research prototype only. It is not a certified medical device and has not been cleared for clinical diagnostic use. Clinicians retain final authority over all triage assessments.
"""

class TriageTool:
    """
    Triage Tool implementing Gemini 2.0 Flash via Vertex AI.
    Conforms to ESI v5 standards and applies safety ceilings/guardrails.
    """
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_LOCATION", "us-central1")
        self.model_name = "gemini-2.0-flash"
        self._initialized = False
        self._model = None
        
    def _initialize_vertex(self):
        if self._initialized:
            return
        if not self.project_id:
            logger.warning("GCP_PROJECT_ID env var not set. Vertex AI client will not be initialized.")
            return
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            vertexai.init(project=self.project_id, location=self.location)
            self._model = GenerativeModel(self.model_name)
            self._initialized = True
            logger.info(f"Vertex AI initialized with model {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")

    def evaluate_case(self, patient: PatientInput) -> Dict[str, Any]:
        """
        Evaluates a patient's triage case using Vertex AI + Gemini 2.0 Flash.
        """
        self._initialize_vertex()
        
        # Prepare vitals and clinical payload
        payload = {
            "age": patient.age,
            "gender": patient.gender,
            "chief_complaint": patient.chief_complaint_text,
            "vitals": patient.vitals.model_dump() if patient.vitals else {},
            "history_cardiac": patient.history_cardiac,
            "history_stroke": patient.history_stroke,
            "is_pregnant": patient.is_pregnant,
            "gestational_weeks": patient.gestational_weeks,
            "pregnancy_complaint": patient.pregnancy_complaint
        }
        
        prompt = f"""Analyze this emergency triage patient case:
Patient payload: {json.dumps(payload, ensure_ascii=False)}

Follow ESI v5 rules and provide:
1. "extracted_symptoms": List of key clinical symptoms.
2. "clinical_impression": Clinical assessment summary.
3. "recommended_esi": Recommended ESI level (1 to 5).
4. "reasoning_en": One-sentence clinical reasoning in English.
5. "reasoning_ar": One-sentence clinical reasoning in Arabic.
6. "expected_resources": List of expected resource categories likely needed (e.g. labs, ecg, imaging, iv_meds_or_fluids, procedure, specialty_consult, monitoring).
7. "safety_warning": Any specific red flags.

Output ONLY valid JSON:
{{
  "extracted_symptoms": [],
  "clinical_impression": "",
  "recommended_esi": 3,
  "reasoning_en": "",
  "reasoning_ar": "",
  "expected_resources": [],
  "safety_warning": ""
}}
"""
        
        # Default fallback
        result = {
            "extracted_symptoms": [patient.chief_complaint_text],
            "clinical_impression": "Triage evaluation completed via fallback",
            "recommended_esi": 3,
            "reasoning_en": "Standard baseline triage level 3 assigned.",
            "reasoning_ar": "تم تعيين مستوى الفرز القياسي الأساسي ٣.",
            "expected_resources": ["labs"],
            "safety_warning": "No specific red flags identified."
        }
        
        if self._initialized and self._model:
            try:
                response = self._model.generate_content(
                    f"{SYSTEM_PROMPT}\n\n{prompt}",
                    generation_config={"response_mime_type": "application/json"}
                )
                text = response.text.strip()
                result.update(json.loads(text))
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}. Using deterministic defaults.")
        
        # safety ceiling logic (e.g. ESI 5 for prescription refills)
        normalized_complaint = patient.chief_complaint_text.lower()
        if any(w in normalized_complaint for w in ["refill", "prescription", "تجديد روشتة", "روشتة"]):
            result["recommended_esi"] = 5
            result["reasoning_en"] = "Routine prescription refill requests do not require emergency department resources."
            result["reasoning_ar"] = "طلبات تجديد الوصفات الطبية الروتينية لا تتطلب موارد قسم الطوارئ."
            result["expected_resources"] = []
            
        elif any(w in normalized_complaint for w in ["stitch removal", "remove stitches", "فك غرز", "فك الغرز"]):
            result["recommended_esi"] = 5
            result["reasoning_en"] = "Routine stitch removal requests do not require acute emergency department resources."
            result["reasoning_ar"] = "طلبات إزالة الغرز الروتينية لا تتطلب موارد قسم الطوارئ الحادة."
            result["expected_resources"] = []

        # Vital-sign safety overrides (Level 1 & 2 floors)
        v = patient.vitals
        if v:
            if patient.age >= 14:
                # ESI 1 Vitals
                if (v.rr and (v.rr < 8 or v.rr > 36)) or \
                   (v.hr and (v.hr < 40 or v.hr > 150)) or \
                   (v.spo2 and v.spo2 < 90) or \
                   (v.gcs and v.gcs < 9) or \
                   (v.sbp and (v.sbp < 80 or v.sbp > 220)):
                    result["recommended_esi"] = 1
                    result["reasoning_en"] = "Immediate life-saving intervention indicated by critical vitals."
                    result["reasoning_ar"] = "التدخل الفوري لإنقاذ الحياة مطلوب بسبب العلامات الحيوية الخطجة."
                # ESI 2 Vitals
                elif result["recommended_esi"] > 2 and (
                     (v.rr and (v.rr < 10 or v.rr > 24)) or \
                     (v.hr and (v.hr < 50 or v.hr > 100)) or \
                     (v.spo2 and v.spo2 < 94) or \
                     (v.sbp and (v.sbp < 90 or v.sbp > 180)) or \
                     (v.temp and (v.temp < 36.0 or v.temp > 39.0))
                ):
                    result["recommended_esi"] = 2
                    result["reasoning_en"] = "High-risk condition indicated by abnormal vitals."
                    result["reasoning_ar"] = "حالة عالية الخطورة بسبب علامات حيوية غير طبيعية."

        # -----------------------------------------------------------------------
        # Chief-complaint red-flag floor pass (applied LAST so it always wins
        # over the ESI-5 ceilings above, but ESI-1 vital floors set above are
        # already 1 and will not be worsened by min()).
        # Rule: red-flag floor sets result to min(current, 2) — NEVER raises ESI.
        # Severe-pain floor: pain_score >= 7 also floors to ESI 2.
        # -----------------------------------------------------------------------
        result = self._apply_redflag_floors(patient, result)

        return result

    def _apply_redflag_floors(
        self, patient: PatientInput, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply chief-complaint red-flag ESI-2 floors and severe-pain floor.
        ONLY lowers ESI (more urgent). Never raises it.
        ESI-1 results from vital floors are preserved (min(1, 2) == 1).
        """
        complaint_lower = patient.chief_complaint_text.lower()

        # --- Severe-pain floor (pain_score from Vitals or pain_scale on PatientInput) ---
        pain_score = None
        if patient.vitals and patient.vitals.pain_score is not None:
            pain_score = patient.vitals.pain_score
        if pain_score is None and patient.pain_scale is not None:
            pain_score = patient.pain_scale

        if pain_score is not None and pain_score >= 7:
            if result["recommended_esi"] > 2:
                result["recommended_esi"] = min(result["recommended_esi"], 2)
                result["reasoning_en"] = (
                    f"Severe pain floor applied (pain score {pain_score}/10): "
                    "maximum ESI 2 per ESI v5 high-pain protocol."
                )
                result["reasoning_ar"] = (
                    f"تطبيق حد الألم الشديد (درجة الألم {pain_score}/10): "
                    "الحد الأقصى ESI 2 وفق بروتوكول الألم الشديد."
                )
                result["safety_warning"] = (
                    result.get("safety_warning", "") +
                    f" | Severe pain (score {pain_score}) — ESI 2 floor applied."
                ).lstrip(" | ")

        # --- Chief-complaint red-flag keyword floors ---
        for keyword_set, label_en, label_ar in _RED_FLAG_SETS:
            # Check each keyword; use substring matching so partial phrases match
            matched = next(
                (kw for kw in keyword_set if kw in complaint_lower),
                None,
            )
            if matched and result["recommended_esi"] > 2:
                result["recommended_esi"] = min(result["recommended_esi"], 2)
                result["reasoning_en"] = (
                    f"{label_en} detected in chief complaint "
                    f"('{matched}'): maximum ESI 2."
                )
                result["reasoning_ar"] = (
                    f"تم اكتشاف {label_ar} في الشكوى الرئيسية "
                    f"('{matched}'): الحد الأقصى ESI 2."
                )
                result["safety_warning"] = (
                    result.get("safety_warning", "") +
                    f" | {label_en} — ESI 2 floor applied."
                ).lstrip(" | ")
                # No break: let all matching floors run so reasoning reflects
                # the most recently matched (most specific) flag. ESI is
                # already at 2; subsequent matches only update the label.

        return result
