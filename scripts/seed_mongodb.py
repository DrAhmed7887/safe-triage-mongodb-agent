import os
import sys
import logging
from typing import List, Dict, Any

# Ensure we can import from backend
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from mongodb_client import MongoDBClient
from mimic_loader import load_demo_cases

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_mongodb")

def seed():
    """Seeds demo cases from data/demo_cases.json into MongoDB Atlas."""
    client = MongoDBClient()
    logger.info("Connecting to MongoDB Atlas...")
    if not client.connect():
        logger.error("Failed to connect to MongoDB Atlas. Exiting seed script.")
        sys.exit(1)
        
    logger.info("Loading demo cases from file...")
    cases = load_demo_cases()
    if not cases:
        logger.error("No demo cases loaded. Exiting seed script.")
        sys.exit(1)
        
    logger.info(f"Loaded {len(cases)} cases. Seeding...")
    seeded = client.seed_cases(cases)
    logger.info(f"Successfully seeded {seeded} cases into MongoDB Atlas!")

if __name__ == "__main__":
    seed()
