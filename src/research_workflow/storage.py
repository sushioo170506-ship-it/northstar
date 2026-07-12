"""Relational workflow state plus a persistent vector context index."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import uuid
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import ContextItem, NodeStatus, ReportConfig, WorkflowStatus


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SQLiteStateStore:
    """Durable source of truth for configuration, runs and chunked artifacts."""

    def __init__(self, path: str | Path, chunk_size: int = 16_384) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.chunk_size = chunk_size
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _init_schema(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY, config_json TEXT NOT NULL,
                    status TEXT NOT NULL, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS node_runs (
                    workflow_id TEXT NOT NULL, node_id TEXT NOT NULL,
                    status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
                    input_json TEXT NOT NULL DEFAULT '{}', output_artifact_id TEXT,
                    error TEXT, updated_at TEXT NOT NULL,
                    PRIMARY KEY (workflow_id, node_id),
                    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
                );
                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL,
                    node_id TEXT NOT NULL, artifact_type TEXT NOT NULL,
                    checksum TEXT NOT NULL, metadata_json TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL, created_at TEXT NOT NULL,
                    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
                );
                CREATE TABLE IF NOT EXISTS artifact_chunks (
                    artifact_id TEXT NOT NULL, chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    PRIMARY KEY (artifact_id, chunk_index),
                    FOREIGN KEY (artifact_id) REFERENCES artifacts(id)
                );
                CREATE TABLE IF NOT EXISTS user_operations (
                    id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL,
                    node_id TEXT, operation TEXT NOT NULL, payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS confirmations (
                    workflow_id TEXT NOT NULL, checkpoint_id TEXT NOT NULL,
                    approved INTEGER NOT NULL, comment TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (workflow_id, checkpoint_id)
                );
                CREATE INDEX IF NOT EXISTS idx_artifacts_workflow_node
                    ON artifacts(workflow_id, node_id, created_at);
                """
            )

    def create_workflow(self, config: ReportConfig, workflow_id: str | None = None) -> str:
        workflow_id = workflow_id or str(uuid.uuid4())
        now = utc_now()
        with self._connect() as db:
            db.execute(
                "INSERT INTO workflows VALUES (?, ?, ?, ?, ?)",
                (workflow_id, json.dumps(config.to_dict(), ensure_ascii=False),
                 WorkflowStatus.RUNNING, now, now),
            )
        return workflow_id

    def config(self, workflow_id: str) -> ReportConfig:
        with self._connect() as db:
            row = db.execute(
                "SELECT config_json FROM workflows WHERE id=?", (workflow_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"工作流不存在: {workflow_id}")
        return ReportConfig.from_dict(json.loads(row["config_json"]))

    def update_config(self, workflow_id: str, config: ReportConfig) -> None:
        with self._connect() as db:
            cursor = db.execute(
                "UPDATE workflows SET config_json=?, updated_at=? WHERE id=?",
                (json.dumps(config.to_dict(), ensure_ascii=False), utc_now(), workflow_id),
            )
        if cursor.rowcount != 1:
            raise KeyError(f"工作流不存在: {workflow_id}")

    def workflow_status(self, workflow_id: str) -> WorkflowStatus:
        with self._connect() as db:
            row = db.execute("SELECT status FROM workflows WHERE id=?", (workflow_id,)).fetchone()
        if row is None:
            raise KeyError(f"工作流不存在: {workflow_id}")
        return WorkflowStatus(row["status"])

    def set_workflow_status(self, workflow_id: str, status: WorkflowStatus) -> None:
        with self._connect() as db:
            db.execute(
                "UPDATE workflows SET status=?, updated_at=? WHERE id=?",
                (status, utc_now(), workflow_id),
            )

    def node(self, workflow_id: str, node_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT * FROM node_runs WHERE workflow_id=? AND node_id=?",
                (workflow_id, node_id),
            ).fetchone()
        return dict(row) if row else None

    def set_node(
        self,
        workflow_id: str,
        node_id: str,
        status: NodeStatus,
        *,
        inputs: dict[str, Any] | None = None,
        output_artifact_id: str | None = None,
        error: str | None = None,
        increment_attempt: bool = False,
    ) -> None:
        previous = self.node(workflow_id, node_id)
        attempts = (previous["attempts"] if previous else 0) + int(increment_attempt)
        input_json = json.dumps(inputs or {}, ensure_ascii=False)
        with self._connect() as db:
            db.execute(
                """
                INSERT INTO node_runs
                    (workflow_id,node_id,status,attempts,input_json,output_artifact_id,error,updated_at)
                VALUES (?,?,?,?,?,?,?,?)
                ON CONFLICT(workflow_id,node_id) DO UPDATE SET
                    status=excluded.status, attempts=excluded.attempts,
                    input_json=excluded.input_json,
                    output_artifact_id=excluded.output_artifact_id,
                    error=excluded.error, updated_at=excluded.updated_at
                """,
                (workflow_id, node_id, status, attempts, input_json,
                 output_artifact_id, error, utc_now()),
            )

    def add_artifact(
        self,
        workflow_id: str,
        node_id: str,
        artifact_type: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        artifact_id = str(uuid.uuid4())
        chunks = [content[i:i + self.chunk_size] for i in range(0, len(content), self.chunk_size)]
        chunks = chunks or [""]
        now = utc_now()
        with self._connect() as db:
            db.execute(
                "INSERT INTO artifacts VALUES (?,?,?,?,?,?,?,?)",
                (artifact_id, workflow_id, node_id, artifact_type, checksum(content),
                 json.dumps(metadata or {}, ensure_ascii=False), len(chunks), now),
            )
            db.executemany(
                "INSERT INTO artifact_chunks VALUES (?,?,?)",
                [(artifact_id, index, chunk) for index, chunk in enumerate(chunks)],
            )
        return artifact_id

    def artifact(self, artifact_id: str) -> dict[str, Any]:
        with self._connect() as db:
            row = db.execute("SELECT * FROM artifacts WHERE id=?", (artifact_id,)).fetchone()
            if row is None:
                raise KeyError(f"产物不存在: {artifact_id}")
            chunks = db.execute(
                "SELECT content FROM artifact_chunks WHERE artifact_id=? ORDER BY chunk_index",
                (artifact_id,),
            ).fetchall()
        result = dict(row)
        result["content"] = "".join(chunk["content"] for chunk in chunks)
        result["metadata"] = json.loads(result.pop("metadata_json"))
        if checksum(result["content"]) != result["checksum"]:
            raise ValueError(f"产物校验失败: {artifact_id}")
        return result

    def node_artifact(
        self, workflow_id: str, node_id: str, *, internal: bool = False
    ) -> dict[str, Any] | None:
        if (
            node_id == "review"
            and not internal
            and self.workflow_status(workflow_id) != WorkflowStatus.COMPLETED
        ):
            raise PermissionError("终稿尚未通过质量门")
        node = self.node(workflow_id, node_id)
        if not node or not node["output_artifact_id"]:
            return None
        return self.artifact(node["output_artifact_id"])

    def record_operation(
        self, workflow_id: str, operation: str, payload: dict[str, Any], node_id: str | None = None
    ) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO user_operations VALUES (?,?,?,?,?,?)",
                (str(uuid.uuid4()), workflow_id, node_id, operation,
                 json.dumps(payload, ensure_ascii=False), utc_now()),
            )

    def feedback(self, workflow_id: str, node_id: str) -> tuple[str, ...]:
        with self._connect() as db:
            rows = db.execute(
                """
                SELECT payload_json FROM user_operations
                WHERE workflow_id=? AND node_id=? AND operation='modify'
                ORDER BY created_at
                """,
                (workflow_id, node_id),
            ).fetchall()
        return tuple(json.loads(row["payload_json"])["feedback"] for row in rows)

    def confirm(self, workflow_id: str, checkpoint_id: str, comment: str = "") -> None:
        with self._connect() as db:
            db.execute(
                """
                INSERT INTO confirmations VALUES (?,?,?,?,?)
                ON CONFLICT(workflow_id,checkpoint_id) DO UPDATE SET
                    approved=1, comment=excluded.comment, created_at=excluded.created_at
                """,
                (workflow_id, checkpoint_id, 1, comment, utc_now()),
            )
        self.record_operation(
            workflow_id, "confirm", {"checkpoint_id": checkpoint_id, "comment": comment},
            checkpoint_id,
        )

    def is_confirmed(self, workflow_id: str, checkpoint_id: str) -> bool:
        with self._connect() as db:
            row = db.execute(
                "SELECT approved FROM confirmations WHERE workflow_id=? AND checkpoint_id=?",
                (workflow_id, checkpoint_id),
            ).fetchone()
        return bool(row and row["approved"])

    def clear_confirmations(self, workflow_id: str, checkpoint_ids: set[str]) -> None:
        if not checkpoint_ids:
            return
        placeholders = ",".join("?" for _ in checkpoint_ids)
        with self._connect() as db:
            db.execute(
                f"DELETE FROM confirmations WHERE workflow_id=? AND checkpoint_id IN ({placeholders})",
                (workflow_id, *sorted(checkpoint_ids)),
            )

    def snapshot(self, workflow_id: str) -> dict[str, Any]:
        with self._connect() as db:
            workflow = db.execute("SELECT * FROM workflows WHERE id=?", (workflow_id,)).fetchone()
            nodes = db.execute(
                "SELECT * FROM node_runs WHERE workflow_id=? ORDER BY updated_at", (workflow_id,)
            ).fetchall()
            operations = db.execute(
                "SELECT * FROM user_operations WHERE workflow_id=? ORDER BY created_at",
                (workflow_id,),
            ).fetchall()
        if workflow is None:
            raise KeyError(f"工作流不存在: {workflow_id}")
        return {
            "workflow": dict(workflow),
            "nodes": [dict(row) for row in nodes],
            "operations": [dict(row) for row in operations],
        }


class SQLiteVectorStore:
    """Small embedded vector database with deterministic sparse embeddings."""

    def __init__(self, path: str | Path, dimensions: int = 512) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.dimensions = dimensions
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS context_vectors (
                    id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, node_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL, content TEXT NOT NULL,
                    vector_json TEXT NOT NULL, metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1
                );
                """
            )
            columns = {
                row["name"] for row in db.execute("PRAGMA table_info(context_vectors)").fetchall()
            }
            if "active" not in columns:
                db.execute(
                    "ALTER TABLE context_vectors ADD COLUMN active INTEGER NOT NULL DEFAULT 1"
                )
            db.execute("DROP INDEX IF EXISTS idx_context_scope")
            db.execute(
                """
                CREATE INDEX idx_context_scope
                ON context_vectors(workflow_id,node_id,artifact_type,active)
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _tokens(self, text: str) -> list[str]:
        normalized = text.lower()
        words = re.findall(r"[a-z0-9_]+|[\u3400-\u9fff]", normalized)
        cjk = "".join(char for char in normalized if "\u3400" <= char <= "\u9fff")
        return words + [cjk[i:i + 2] for i in range(max(0, len(cjk) - 1))]

    def embed(self, text: str) -> dict[int, float]:
        counts: Counter[int] = Counter()
        for token in self._tokens(text):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            counts[int.from_bytes(digest, "big") % self.dimensions] += 1
        norm = math.sqrt(sum(value * value for value in counts.values())) or 1.0
        return {key: value / norm for key, value in counts.items()}

    @staticmethod
    def _similarity(left: dict[int, float], right: dict[int, float]) -> float:
        if len(left) > len(right):
            left, right = right, left
        return sum(value * right.get(key, 0.0) for key, value in left.items())

    def upsert_chunks(
        self,
        *,
        workflow_id: str,
        node_id: str,
        artifact_type: str,
        artifact_id: str,
        content: str,
        chunk_size: int = 2_000,
        overlap: int = 200,
    ) -> None:
        if overlap >= chunk_size:
            raise ValueError("overlap 必须小于 chunk_size")
        step = chunk_size - overlap
        chunks = [content[i:i + chunk_size] for i in range(0, len(content), step)] or [""]
        now = utc_now()
        records = []
        for index, chunk in enumerate(chunks):
            item_id = f"{artifact_id}:{index}"
            vector = {str(k): v for k, v in self.embed(chunk).items()}
            metadata = {"artifact_id": artifact_id, "chunk_index": index, "chunk_count": len(chunks)}
            records.append(
                (item_id, workflow_id, node_id, artifact_type, chunk,
                 json.dumps(vector), json.dumps(metadata), now)
            )
        with self._connect() as db:
            db.execute(
                "UPDATE context_vectors SET active=0 WHERE workflow_id=? AND node_id=?",
                (workflow_id, node_id),
            )
            db.executemany(
                """
                INSERT OR REPLACE INTO context_vectors
                    (id,workflow_id,node_id,artifact_type,content,vector_json,
                     metadata_json,created_at,active)
                VALUES (?,?,?,?,?,?,?,?,1)
                """,
                records,
            )

    def deactivate_nodes(self, workflow_id: str, node_ids: set[str]) -> None:
        if not node_ids:
            return
        placeholders = ",".join("?" for _ in node_ids)
        with self._connect() as db:
            db.execute(
                f"""
                UPDATE context_vectors SET active=0
                WHERE workflow_id=? AND node_id IN ({placeholders})
                """,
                (workflow_id, *sorted(node_ids)),
            )

    def query(
        self,
        workflow_id: str,
        query: str,
        *,
        node_ids: set[str] | None = None,
        artifact_types: set[str] | None = None,
        limit: int = 12,
    ) -> tuple[ContextItem, ...]:
        clauses = ["workflow_id=?", "active=1"]
        params: list[Any] = [workflow_id]
        if node_ids:
            placeholders = ",".join("?" for _ in node_ids)
            clauses.append(f"node_id IN ({placeholders})")
            params.extend(sorted(node_ids))
        if artifact_types:
            placeholders = ",".join("?" for _ in artifact_types)
            clauses.append(f"artifact_type IN ({placeholders})")
            params.extend(sorted(artifact_types))
        with self._connect() as db:
            rows = db.execute(
                f"SELECT * FROM context_vectors WHERE {' AND '.join(clauses)}", params
            ).fetchall()
        query_vector = self.embed(query)
        ranked: list[ContextItem] = []
        for row in rows:
            vector = {int(k): v for k, v in json.loads(row["vector_json"]).items()}
            ranked.append(
                ContextItem(
                    id=row["id"], workflow_id=row["workflow_id"], node_id=row["node_id"],
                    artifact_type=row["artifact_type"], content=row["content"],
                    created_at=row["created_at"], metadata=json.loads(row["metadata_json"]),
                    score=self._similarity(query_vector, vector),
                )
            )
        ranked.sort(key=lambda item: (item.score, item.created_at), reverse=True)
        return tuple(ranked[:limit])
