import os
import json
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from models import PatientInput, TriageResult, TriageLevel, Vitals

logger = logging.getLogger(__name__)

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

        return result
