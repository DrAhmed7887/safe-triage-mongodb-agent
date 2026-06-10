"""
MongoDB MCP Client — SAFE-Triage Agent
======================================
Persists and retrieves triage cases through the MongoDB MCP Server
(github.com/mongodb-js/mongodb-mcp-server) over stdio, using the
official Python MCP SDK (mcp>=1.0.0).

Satisfies the Google Cloud Rapid Agent Hackathon — MongoDB Track
requirement: partner MCP server integration.

MCP tools used (confirmed against live cluster):
  • insert-many  — persist a new triage case record
  • find         — retrieve recent cases (sorted by timestamp desc) or by _id
  • count        — health probe

Fallback: if Node/npx is missing, the MCP import fails, or the MCP
handshake errors, a MongoDBMCPError is raised so the caller can fall
back gracefully to pymongo.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import threading
from typing import Any
import anyio

logger = logging.getLogger(__name__)

# ── typed error callers can catch ─────────────────────────────────────────────


class MongoDBMCPError(RuntimeError):
    """Raised when the MongoDB MCP client cannot complete an operation."""


# ── lazy import guard ─────────────────────────────────────────────────────────

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False
    logger.warning(
        "mcp Python SDK not installed — MongoDB MCP client unavailable. "
        "Install with: pip install 'mcp>=1.0.0'"
    )


# ── async helper ──────────────────────────────────────────────────────────────


async def _call_mcp_tool(
    server_params: StdioServerParameters,
    tool_name: str,
    tool_args: dict[str, Any],
) -> Any:
    """Open a fresh MCP session, call one tool, return the parsed result."""
    result_val = None
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=tool_args)
                # result.content is a list of TextContent / ImageContent blocks
                if result.content:
                    text = result.content[0].text if hasattr(result.content[0], "text") else str(result.content[0])
                    try:
                        result_val = json.loads(text)
                    except (json.JSONDecodeError, TypeError):
                        result_val = text
    except Exception as exc:
        is_harmless = False
        if isinstance(exc, BaseExceptionGroup):
            match, rest = exc.split(anyio.BrokenResourceError)
            if match is not None:
                if rest is None:
                    is_harmless = True
                else:
                    is_harmless = True
        
        if is_harmless and result_val is not None:
            logger.debug("Ignored BrokenResourceError ExceptionGroup in MCP stdio client exit since we have a result.")
        else:
            raise
    return result_val


# ── singleton background event loop ──────────────────────────────────────────
# We run a single asyncio loop in a daemon thread so each sync call does not
# spawn a new loop (which would re-launch the Node process every call).

_loop: asyncio.AbstractEventLoop | None = None
_loop_lock = threading.Lock()


def _get_or_create_loop() -> asyncio.AbstractEventLoop:
    global _loop
    with _loop_lock:
        if _loop is None or _loop.is_closed():
            _loop = asyncio.new_event_loop()
            t = threading.Thread(target=_loop.run_forever, daemon=True, name="mcp-loop")
            t.start()
        return _loop


def _run_async(coro) -> Any:
    """Submit a coroutine to the background loop and block until done."""
    loop = _get_or_create_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=30)


# ── public client class ───────────────────────────────────────────────────────


class MongoDBMCPClient:
    """
    Synchronous facade over the MongoDB MCP Server for triage case
    persistence and retrieval.

    Environment variables:
      MDB_MCP_CONNECTION_STRING  — Atlas URI for the MCP server process
                                   (falls back to MONGODB_URI if unset)
      MONGODB_DB_NAME            — database name (default: safe_triage)
    """

    _TOOL_INSERT = "insert-many"
    _TOOL_FIND = "find"
    _TOOL_COUNT = "count"
    _COLLECTION = "triage_cases"

    def __init__(self) -> None:
        conn = os.getenv("MDB_MCP_CONNECTION_STRING") or os.getenv("MONGODB_URI", "")
        self._db_name = os.getenv("MONGODB_DB_NAME", "safe_triage")
        self._conn_string = conn

        if not _MCP_AVAILABLE:
            logger.warning("MongoDBMCPClient: mcp SDK unavailable at import time.")
            self._server_params = None
            return

        if not conn:
            logger.warning(
                "MongoDBMCPClient: neither MDB_MCP_CONNECTION_STRING nor MONGODB_URI "
                "is set — MCP operations will fail with MongoDBMCPError."
            )
            self._server_params = None
            return

        # Prefer a baked-in `mongodb-mcp-server` binary (installed globally in the
        # Docker image) so cold starts don't trigger a runtime `npx` download;
        # fall back to `npx -y mongodb-mcp-server` on dev machines without it.
        if shutil.which("mongodb-mcp-server"):
            command, args = "mongodb-mcp-server", []
        else:
            command, args = "npx", ["-y", "mongodb-mcp-server"]

        # Pass the Atlas URI via the server's env var (MDB_MCP_CONNECTION_STRING)
        # rather than argv, so the secret is not exposed in process listings.
        # The stdio process is launched per-call (short-lived) by _call_mcp_tool.
        self._server_params = StdioServerParameters(
            command=command,
            args=args,
            env={**os.environ, "MDB_MCP_CONNECTION_STRING": conn},
        )

    # ── private helper ─────────────────────────────────────────────────────────

    def _require_ready(self) -> None:
        if not _MCP_AVAILABLE:
            raise MongoDBMCPError("mcp Python SDK is not installed.")
        if self._server_params is None:
            raise MongoDBMCPError(
                "No MongoDB connection string configured. "
                "Set MDB_MCP_CONNECTION_STRING or MONGODB_URI."
            )

    def _call(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        self._require_ready()
        try:
            return _run_async(
                _call_mcp_tool(self._server_params, tool_name, tool_args)
            )
        except MongoDBMCPError:
            raise
        except Exception as exc:
            raise MongoDBMCPError(f"MCP tool '{tool_name}' failed: {exc}") from exc

    # ── public API ─────────────────────────────────────────────────────────────

    def save_case(self, record: dict[str, Any]) -> str:
        """
        Insert a triage case record via MCP insert-many.
        Returns the inserted document ID string.
        """
        import secrets
        
        # Determine or pre-generate the case_id
        if "_id" in record:
            val = record["_id"]
            if isinstance(val, dict) and "$oid" in val:
                case_id = val["$oid"]
            else:
                case_id = str(val)
        else:
            case_id = secrets.token_hex(12)
            record["_id"] = {"$oid": case_id}

        result = self._call(
            self._TOOL_INSERT,
            {
                "database": self._db_name,
                "collection": self._COLLECTION,
                "documents": [record],
            },
        )
        # Handle different response shapes from different MCP server versions
        if isinstance(result, dict) and "insertedIds" in result:
            ids = result["insertedIds"]
            return ids[0] if ids else ""
        elif isinstance(result, str) and "inserted successfully" in result:
            return case_id
            
        logger.warning("MongoDBMCPClient.save_case: unexpected result shape: %r", result)
        return ""

    def get_recent_cases(self, limit: int = 20) -> list[dict[str, Any]]:
        """
        Retrieve the most recent triage cases, sorted by timestamp descending,
        via MCP find.
        """
        result = self._call(
            self._TOOL_FIND,
            {
                "database": self._db_name,
                "collection": self._COLLECTION,
                "filter": {},
                "sort": {"timestamp": -1},
                "limit": limit,
            },
        )
        if isinstance(result, list):
            return result
        # Some MCP server versions wrap results
        if isinstance(result, dict) and "documents" in result:
            return result["documents"]
        logger.warning("MongoDBMCPClient.get_recent_cases: unexpected shape: %r", result)
        return []

    def get_case_by_id(self, case_id: str) -> dict[str, Any] | None:
        """
        Retrieve a single triage case by its _id string via MCP find.
        """
        result = self._call(
            self._TOOL_FIND,
            {
                "database": self._db_name,
                "collection": self._COLLECTION,
                "filter": {"_id": {"$oid": case_id}},
                "limit": 1,
            },
        )
        docs: list = []
        if isinstance(result, list):
            docs = result
        elif isinstance(result, dict) and "documents" in result:
            docs = result["documents"]
        return docs[0] if docs else None

    def get_cases(
        self, limit: int = 20, esi: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Retrieve triage cases with an optional ESI level filter,
        sorted by timestamp descending, via MCP find.
        """
        query_filter: dict[str, Any] = {}
        if esi is not None:
            query_filter["triage_result.level"] = esi
        result = self._call(
            self._TOOL_FIND,
            {
                "database": self._db_name,
                "collection": self._COLLECTION,
                "filter": query_filter,
                "sort": {"timestamp": -1},
                "limit": limit,
            },
        )
        if isinstance(result, list):
            return result
        if isinstance(result, dict) and "documents" in result:
            return result["documents"]
        logger.warning("MongoDBMCPClient.get_cases: unexpected shape: %r", result)
        return []

    def health(self) -> dict[str, Any]:
        """
        Probe MCP connectivity by counting documents in triage_cases.
        Returns a dict with 'status' and optional 'count'.
        """
        if not _MCP_AVAILABLE:
            return {"status": "unavailable", "reason": "mcp SDK not installed"}
        if self._server_params is None:
            return {"status": "unavailable", "reason": "no connection string configured"}
        try:
            result = self._call(
                self._TOOL_COUNT,
                {
                    "database": self._db_name,
                    "collection": self._COLLECTION,
                },
            )
            count: int | None = None
            if isinstance(result, dict):
                count = result.get("count")
            elif isinstance(result, (int, float)):
                count = int(result)
            return {"status": "connected", "collection": self._COLLECTION, "count": count}
        except MongoDBMCPError as exc:
            return {"status": "unavailable", "reason": str(exc)}
