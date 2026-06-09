import argparse
import os
import sys
import logging
from typing import List, Dict, Any

# Ensure repo root is on sys.path for absolute package imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.mongodb_client import MongoDBClient
from backend.mimic_loader import load_demo_cases

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


def dry_run():
    """Validates demo_cases.json and prints a summary without touching MongoDB."""
    logger.info("Loading demo cases from file (dry-run — no DB connection)...")
    cases = load_demo_cases()
    if not cases:
        logger.error("No demo cases loaded. Check data/demo_cases.json.")
        sys.exit(1)

    print(f"\nDRY RUN: {len(cases)} case(s) WOULD be seeded into MongoDB.\n")
    print(f"{'case_id':<10} {'expected_level':<16} chief_complaint")
    print("-" * 70)
    for c in cases:
        case_id = c.get("case_id", "?")
        level = c.get("expected_level", "?")
        complaint = c.get("chief_complaint", "")
        print(f"{str(case_id):<10} {str(level):<16} {complaint}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed SAFE-Triage demo cases into MongoDB Atlas."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Validate and print cases that WOULD be seeded without connecting "
            "to MongoDB or inserting any data."
        ),
    )
    args = parser.parse_args()

    if args.dry_run:
        dry_run()
    else:
        seed()
