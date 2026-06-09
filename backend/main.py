import os
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from backend.models import PatientInput, TriageResult, TriageLevel
from agent.triage_tool import TriageTool
from backend.mongodb_client import MongoDBClient
from backend.mimic_loader import load_demo_cases

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SAFE-Triage Agent API — MongoDB Track",
    description="Emergency department triage system integrated with Google Cloud Agent Builder and MongoDB Atlas",
    version="1.0.0"
)

# Initialize Tooling and Connection
triage_tool = TriageTool()
mongo_client = MongoDBClient()

@app.on_event("startup")
async def startup_event():
    # Attempt to seed MongoDB with demo cases on startup
    try:
        mongo_client.connect()
        cases = load_demo_cases()
        seeded_count = mongo_client.seed_cases(cases)
        logger.info(f"MongoDB seeded with {seeded_count} demo cases on startup.")
    except Exception as e:
        logger.error(f"Failed to seed MongoDB on startup: {e}")

@app.get("/health", tags=["System"])
def health_check():
    """Returns the system health status, including MongoDB connection state."""
    db_status = "connected" if mongo_client.is_connected() else "disconnected"
    return {
        "status": "healthy",
        "mongodb": db_status,
        "gcp_project_id": os.getenv("GCP_PROJECT_ID", "not-configured")
    }

@app.post("/triage", response_model=Dict[str, Any], tags=["Triage"])
def post_triage(patient: PatientInput):
    """
    Performs triage classification on a patient's case.
    Saves the triage case record in MongoDB.
    """
    try:
        # Run AI/Deterministic hybrid triage evaluation
        evaluation = triage_tool.evaluate_case(patient)
        
        # Build standard triage result dictionary
        result = {
            "level": evaluation["recommended_esi"],
            "esi_level": evaluation["recommended_esi"],
            "color_code": {
                1: "red",
                2: "orange",
                3: "yellow",
                4: "green",
                5: "blue"
            }.get(evaluation["recommended_esi"], "gray"),
            "label_en": {
                1: "Resuscitation",
                2: "Emergent",
                3: "Urgent",
                4: "Less Urgent",
                5: "Non-Urgent"
            }.get(evaluation["recommended_esi"], "Unknown"),
            "label_ar": {
                1: "إنعاش",
                2: "طارئ",
                3: "عاجل",
                4: "أقل عجلة",
                5: "غير عاجل"
            }.get(evaluation["recommended_esi"], "غير معروف"),
            "extraction_method": "gemini_online",
            "reasoning_en": evaluation["reasoning_en"],
            "reasoning_ar": evaluation["reasoning_ar"],
            "expected_resources": evaluation["expected_resources"],
            "safety_warning": evaluation["safety_warning"],
            "requires_review": evaluation["recommended_esi"] in [1, 2],
            "disclaimer": "Disclaimer: This is a research prototype only. It is not a certified medical device and has not been cleared for clinical diagnostic use. Clinicians retain final authority over all triage assessments.",
            "safety_disclaimer": "Disclaimer: This is a research prototype only. It is not a certified medical device and has not been cleared for clinical diagnostic use. Clinicians retain final authority over all triage assessments."
        }
        
        # Save case & result to MongoDB
        record = {
            "patient": patient.model_dump(),
            "triage_result": result,
            "timestamp": mongo_client.get_timestamp()
        }
        inserted_id = mongo_client.insert_case(record)
        result["case_id"] = inserted_id
        
        return result
    except Exception as e:
        logger.error(f"Triage processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Triage process failure: {str(e)}"
        )

@app.get("/cases", tags=["Triage"])
def get_cases(limit: int = 20, esi: Optional[int] = None):
    """
    Retrieves previous triage case records from MongoDB.
    Optionally queries/filters by ESI level using MongoDB queries.
    """
    try:
        records = mongo_client.get_cases(limit=limit, esi=esi)
        return {"count": len(records), "cases": records}
    except Exception as e:
        logger.error(f"Failed to fetch cases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failure: {str(e)}"
        )
