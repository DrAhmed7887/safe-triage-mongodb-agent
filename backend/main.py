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
from agent.mongodb_mcp_client import MongoDBMCPClient, MongoDBMCPError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SAFE-Triage Agent API — MongoDB Track",
    description="Emergency department triage system integrated with Google Cloud Agent Builder and MongoDB Atlas",
    version="1.0.0"
)

# Initialize Tooling and Connections
triage_tool = TriageTool()
mongo_client = MongoDBClient()
mcp_client = MongoDBMCPClient()  # MongoDB MCP Server client (primary persistence)

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
    """Returns the system health status, including MongoDB MCP and pymongo states."""
    db_status = "connected" if mongo_client.is_connected() else "disconnected"
    mcp_health = mcp_client.health()
    return {
        "status": "healthy",
        "mongodb_mcp_server": mcp_health,
        "mongodb_pymongo": db_status,
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
        
        # Build the case record for persistence
        record = {
            "patient": patient.model_dump(),
            "triage_result": result,
            "timestamp": mongo_client.get_timestamp().isoformat()
        }

        # Persist via MongoDB MCP Server (primary); fall back to pymongo
        persistence_source = "mongodb_mcp_server"
        try:
            inserted_id = mcp_client.save_case(record)
            if not inserted_id:
                raise MongoDBMCPError("MCP server returned empty insertedId")
            logger.info("Case persisted via MongoDB MCP Server, id=%s", inserted_id)
        except MongoDBMCPError as mcp_err:
            logger.warning(
                "MongoDB MCP Server unavailable (%s) — falling back to pymongo", mcp_err
            )
            persistence_source = "pymongo_fallback"
            record["timestamp"] = mongo_client.get_timestamp()  # pymongo accepts datetime
            inserted_id = mongo_client.insert_case(record)
            logger.info("Case persisted via pymongo fallback, id=%s", inserted_id)

        result["case_id"] = inserted_id
        result["persistence"] = persistence_source

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
        # Retrieve via MongoDB MCP Server (primary); fall back to pymongo
        persistence_source = "mongodb_mcp_server"
        try:
            records = mcp_client.get_cases(limit=limit, esi=esi)
            logger.info("Cases retrieved via MongoDB MCP Server (count=%d)", len(records))
        except MongoDBMCPError as mcp_err:
            logger.warning(
                "MongoDB MCP Server unavailable (%s) — falling back to pymongo", mcp_err
            )
            persistence_source = "pymongo_fallback"
            records = mongo_client.get_cases(limit=limit, esi=esi)

        return {"count": len(records), "cases": records, "persistence": persistence_source}
    except Exception as e:
        logger.error(f"Failed to fetch cases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failure: {str(e)}"
        )
