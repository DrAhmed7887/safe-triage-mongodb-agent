import os
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MongoDBClient:
    """
    MongoDB Atlas Connection and Operations Client.
    Integrates with the MongoDB MCP server conventions for querying.
    """
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI")
        self.db_name = os.getenv("MONGODB_DB_NAME", "safe_triage")
        self.collection_name = "triage_cases"
        self._client = None
        self._db = None
        self._collection = None

    def connect(self) -> bool:
        """Connects to the MongoDB Atlas database instance."""
        if self._client:
            return True
        if not self.uri:
            logger.error("MONGODB_URI env var is not set. MongoDB client cannot connect.")
            return False
        try:
            from pymongo import MongoClient
            self._client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self._db = self._client[self.db_name]
            self._collection = self._db[self.collection_name]
            # Verify connectivity
            self._client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas!")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB Atlas: {e}")
            return False

    def is_connected(self) -> bool:
        """Checks connection status."""
        try:
            if self._client:
                self._client.admin.command('ping')
                return True
        except Exception:
            pass
        return False

    def get_timestamp(self) -> datetime:
        """Utility to get timezone-aware timestamp."""
        return datetime.utcnow()

    def insert_case(self, record: Dict[str, Any]) -> str:
        """Inserts a triage case record into MongoDB."""
        if not self.connect():
            raise RuntimeError("Database connection not available.")
        try:
            res = self._collection.insert_one(record)
            return str(res.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert case record: {e}")
            raise e

    def get_cases(self, limit: int = 20, esi: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieves triage case records with optional filters."""
        if not self.connect():
            return []
        try:
            query = {}
            if esi is not None:
                query["triage_result.level"] = esi
                
            cursor = self._collection.find(query).sort("timestamp", -1).limit(limit)
            records = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                # Serialize timestamps for JSON compatibility
                if "timestamp" in doc and isinstance(doc["timestamp"], datetime):
                    doc["timestamp"] = doc["timestamp"].isoformat()
                records.append(doc)
            return records
        except Exception as e:
            logger.error(f"Failed to query cases: {e}")
            return []

    def seed_cases(self, cases: List[Dict[str, Any]]) -> int:
        """Seeds standard demo cases if collection is empty."""
        if not self.connect():
            return 0
        try:
            # Check if cases already seeded
            if self._collection.count_documents({}) > 0:
                logger.info("MongoDB collection already has cases. Skipping seed.")
                return 0
            
            records = []
            for c in cases:
                records.append({
                    "patient": {
                        "age": c["age"],
                        "gender": c["sex"],
                        "chief_complaint_text": c["chief_complaint"],
                        "chief_complaint_ar": c.get("chief_complaint_ar", ""),
                        "vitals": c["vitals"]
                    },
                    "triage_result": {
                        "level": c["expected_level"],
                        "esi_level": c["expected_level"],
                        "color_code": {
                            1: "red", 2: "orange", 3: "yellow", 4: "green", 5: "blue"
                        }.get(c["expected_level"], "gray"),
                        "label_en": {
                            1: "Resuscitation", 2: "Emergent", 3: "Urgent", 4: "Less Urgent", 5: "Non-Urgent"
                        }.get(c["expected_level"], "Unknown"),
                        "label_ar": {
                            1: "إنعاش", 2: "طارئ", 3: "عاجل", 4: "أقل عجلة", 5: "غير عاجل"
                        }.get(c["expected_level"], "غير معروف"),
                        "extraction_method": "seed_loader",
                        "reasoning_en": "Pre-seeded clinical test case for system validation.",
                        "reasoning_ar": "حالة اختبار سريرية تم بذرها مسبقًا للتحقق من صحة النظام.",
                        "expected_resources": [],
                        "disclaimer": "Disclaimer: This is a research prototype only. It is not a certified medical device."
                    },
                    "timestamp": self.get_timestamp()
                })
            res = self._collection.insert_many(records)
            return len(res.inserted_ids)
        except Exception as e:
            logger.error(f"Failed to seed demo cases: {e}")
            return 0
