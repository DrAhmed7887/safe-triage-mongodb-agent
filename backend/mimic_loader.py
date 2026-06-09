import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def load_demo_cases() -> List[Dict[str, Any]]:
    """Loads cases from the local demo_cases.json file."""
    # Look in the standard data/ directory relative to workspace root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "data", "demo_cases.json")
    
    if not os.path.exists(json_path):
        logger.error(f"Demo cases JSON not found at: {json_path}")
        return []
        
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            cases = json.load(f)
            return cases
    except Exception as e:
        logger.error(f"Error loading demo cases: {e}")
        return []
