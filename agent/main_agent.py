import os
import sys
import logging
from typing import Dict, Any

# Ensure correct import paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from triage_tool import TriageTool
from models import PatientInput

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main_agent")

def run_agent_triage(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Google Cloud Agent Builder Entrypoint.
    Receives standard JSON payload, validates, evaluates using Gemini 2.0 Flash via Vertex AI,
    and returns ESI triage level with a safety disclaimer.
    """
    logger.info("Initializing Agent Builder Triage Request")
    try:
        # Validate input payload using Pydantic PatientInput
        patient = PatientInput(**payload)
        
        # Initialize TriageTool
        tool = TriageTool()
        
        # Evaluate case
        result = tool.evaluate_case(patient)
        
        # Format the final response with safety authority disclaimer
        response = {
            "esi_level": result["recommended_esi"],
            "reasoning_en": result["reasoning_en"],
            "reasoning_ar": result["reasoning_ar"],
            "extracted_symptoms": result["extracted_symptoms"],
            "expected_resources": result["expected_resources"],
            "safety_warning": result.get("safety_warning", ""),
            "safety_disclaimer": "Disclaimer: This is a research prototype only. It is not a certified medical device and has not been cleared for clinical diagnostic use. Clinicians retain final authority over all triage assessments."
        }
        return response
    except Exception as e:
        logger.error(f"Agent Builder evaluation error: {e}")
        return {
            "error": "Invalid patient payload or internal evaluation failure",
            "details": str(e),
            "safety_disclaimer": "Disclaimer: This is a research prototype only. It is not a certified medical device and has not been cleared for clinical diagnostic use. Clinicians retain final authority over all triage assessments."
        }

if __name__ == "__main__":
    # Test script run
    test_payload = {
        "age": 45,
        "gender": "male",
        "chief_complaint_text": "Severe crushing chest pain radiating to left jaw, sweating",
        "vitals": {
            "hr": 110,
            "rr": 20,
            "spo2": 95,
            "temp": 37.0,
            "sbp": 140,
            "dbp": 90
        }
    }
    print("Testing main_agent.py with sample payload:")
    print(json.dumps(run_agent_triage(test_payload), indent=2, ensure_ascii=False))
