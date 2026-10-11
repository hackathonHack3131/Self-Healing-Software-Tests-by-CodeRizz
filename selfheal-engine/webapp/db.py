"""MongoDB client and persistence layer for SelfHeal test runs, recipes, and intents."""

from datetime import datetime, timezone
import logging
import os
from typing import Any, Dict, List, Optional
import pymongo
from pymongo.errors import ConnectionFailure, PyMongoError

logger = logging.getLogger("selfheal.db")

# Default MongoDB URI connecting to local MongoDB with auth or fallback
DEFAULT_MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://admin:disaster_secret_pass@localhost:27017/selfheal?authSource=admin",
)
FALLBACK_MONGO_URI = "mongodb://localhost:27017/selfheal"
DB_NAME = os.getenv("MONGO_DB_NAME", "selfheal")


class DatabaseManager:
    """Manages connection to MongoDB with graceful fallback to in-memory store."""

    def __init__(self, uri: str = DEFAULT_MONGO_URI, db_name: str = DB_NAME):
        self.uri = uri
        self.db_name = db_name
        self.client: Optional[pymongo.MongoClient] = None
        self.db = None
        self.is_connected: bool = False
        self.error_message: Optional[str] = None
        self._in_memory_runs: List[Dict[str, Any]] = []
        self._connect()

    def _connect(self) -> None:
        """Attempt connection to MongoDB; try primary URI, then fallback URI."""
        uris_to_try = [self.uri]
        if FALLBACK_MONGO_URI not in uris_to_try:
            uris_to_try.append(FALLBACK_MONGO_URI)

        for candidate_uri in uris_to_try:
            try:
                client = pymongo.MongoClient(candidate_uri, serverSelectionTimeoutMS=2000)
                # Ping server to verify connectivity
                client.admin.command("ping")
                self.client = client
                self.db = self.client[self.db_name]
                self.is_connected = True
                self.error_message = None
                self.uri = candidate_uri

                # Setup indexes
                self.db.runs.create_index([("created_at", pymongo.DESCENDING)])
                self.db.runs.create_index([("run_id", pymongo.ASCENDING)], unique=True)
                self.db.recipes.create_index([("intent_id", pymongo.ASCENDING), ("version", pymongo.ASCENDING)])
                logger.info("Connected to MongoDB successfully at %s (db: %s)", candidate_uri, self.db_name)
                return
            except (ConnectionFailure, PyMongoError, Exception) as exc:
                logger.warning("MongoDB connection failed for %s: %s", candidate_uri, exc)
                self.error_message = str(exc)

        self.is_connected = False
        logger.warning("Using in-memory fallback store because MongoDB connection was unsuccessful.")

    def get_status(self) -> Dict[str, Any]:
        """Return connectivity details and database metrics."""
        # Re-check ping if client exists
        if self.client:
            try:
                self.client.admin.command("ping")
                self.is_connected = True
            except Exception as e:
                self.is_connected = False
                self.error_message = str(e)

        runs_count = 0
        recipes_count = 0
        if self.is_connected and self.db is not None:
            try:
                runs_count = self.db.runs.count_documents({})
                recipes_count = self.db.recipes.count_documents({})
            except Exception:
                runs_count = len(self._in_memory_runs)
        else:
            runs_count = len(self._in_memory_runs)

        # Mask sensitive password in URI before returning status
        masked_uri = self.uri
        if "@" in masked_uri:
            proto, rest = masked_uri.split("://", 1)
            auth, host_part = rest.split("@", 1)
            masked_uri = f"{proto}://***:***@{host_part}"

        return {
            "connected": self.is_connected,
            "backend": "mongodb" if self.is_connected else "in_memory_fallback",
            "uri": masked_uri,
            "database": self.db_name,
            "runs_count": runs_count,
            "recipes_count": recipes_count,
            "error": self.error_message if not self.is_connected else None,
        }

    # -------------------------------------------------------------
    # Runs Collection Operations
    # -------------------------------------------------------------
    def save_run(self, run_doc: Dict[str, Any]) -> str:
        """Insert or replace a run document."""
        if "created_at" not in run_doc:
            run_doc["created_at"] = datetime.now(timezone.utc).isoformat()

        if self.is_connected and self.db is not None:
            try:
                self.db.runs.update_one(
                    {"run_id": run_doc["run_id"]},
                    {"$set": run_doc},
                    upsert=True,
                )
                return run_doc["run_id"]
            except Exception as exc:
                logger.error("Failed to save run to MongoDB: %s", exc)

        # Fallback to in-memory
        self._in_memory_runs = [r for r in self._in_memory_runs if r.get("run_id") != run_doc["run_id"]]
        self._in_memory_runs.insert(0, run_doc)
        return run_doc["run_id"]

    def get_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent runs ordered by creation timestamp descending."""
        if self.is_connected and self.db is not None:
            try:
                cursor = self.db.runs.find({}, {"_id": 0}).sort("created_at", pymongo.DESCENDING).limit(limit)
                return list(cursor)
            except Exception as exc:
                logger.error("Failed to query runs from MongoDB: %s", exc)

        return self._in_memory_runs[:limit]

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Find a single run document by run_id."""
        if self.is_connected and self.db is not None:
            try:
                doc = self.db.runs.find_one({"run_id": run_id}, {"_id": 0})
                if doc:
                    return doc
            except Exception as exc:
                logger.error("Failed to find run %s in MongoDB: %s", run_id, exc)

        for r in self._in_memory_runs:
            if r.get("run_id") == run_id:
                return r
        return None

    def clear_runs(self) -> int:
        """Clear all historical runs."""
        count = 0
        if self.is_connected and self.db is not None:
            try:
                res = self.db.runs.delete_many({})
                count = res.deleted_count
            except Exception as exc:
                logger.error("Failed to clear runs in MongoDB: %s", exc)

        count += len(self._in_memory_runs)
        self._in_memory_runs.clear()
        return count

    # -------------------------------------------------------------
    # Recipes Collection Operations
    # -------------------------------------------------------------
    def save_recipe(self, recipe_doc: Dict[str, Any]) -> None:
        """Insert or update a recipe version record."""
        if self.is_connected and self.db is not None:
            try:
                self.db.recipes.update_one(
                    {"intent_id": recipe_doc["intent_id"], "version": recipe_doc["version"]},
                    {"$set": recipe_doc},
                    upsert=True,
                )
            except Exception as exc:
                logger.error("Failed to save recipe to MongoDB: %s", exc)

    def get_recipes(self, intent_id: str = "checkout") -> List[Dict[str, Any]]:
        """Fetch all stored recipes for an intent."""
        if self.is_connected and self.db is not None:
            try:
                cursor = self.db.recipes.find({"intent_id": intent_id}, {"_id": 0}).sort("version", pymongo.ASCENDING)
                return list(cursor)
            except Exception as exc:
                logger.error("Failed to get recipes from MongoDB: %s", exc)
        return []

    def save_contact(self, contact_doc: Dict[str, Any]) -> str:
        """Save a contact or feedback submission to MongoDB."""
        contact_doc.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        if self.is_connected and self.db is not None:
            try:
                res = self.db.contacts.insert_one(contact_doc)
                return str(res.inserted_id)
            except Exception as exc:
                logger.warning("Failed to save contact to MongoDB: %s", exc)
        return "stored_offline"

    def get_contacts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent contact inquiries."""
        if self.is_connected and self.db is not None:
            try:
                cursor = self.db.contacts.find({}, {"_id": 0}).sort("created_at", pymongo.DESCENDING).limit(limit)
                return list(cursor)
            except Exception as exc:
                logger.warning("Failed to fetch contacts: %s", exc)
        return []


# Global singleton database instance
db_manager = DatabaseManager()
