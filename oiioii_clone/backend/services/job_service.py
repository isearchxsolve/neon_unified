"""Job queue abstractions and contract implementations."""
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
import threading
from datetime import datetime
from dataclasses import dataclass

class JobStatus(str, Enum):
    QUEUED = "queued"
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class StandardMediaResult:
    media_id: str
    status: str
    url: Optional[str] = None
    error: Optional[str] = None
    file_size_bytes: int = 0

class JobService:
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._counter = 0

    def enqueue(self, project_id: str, stage: str, payload: Dict[str, Any]) -> str:
        with self._lock:
            jid = uuid.uuid4().hex[:12]
            self._jobs[jid] = {
                "id": jid,
                "project_id": project_id,
                "stage": stage,
                "status": JobStatus.QUEUED.value,
                "payload": payload,
                "created_at": datetime.utcnow().isoformat(),
            }
            return jid

    def get(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._jobs.get(job_id)

    def list_for_project(self, project_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return [j for j in self._jobs.values() if j.get("project_id") == project_id]

    def create_job(self, payload: Dict[str, Any]) -> str:
        if not payload or not payload.get("source_url"):
            raise ValueError("VALIDATION_ERROR: missing source_url")
        with self._lock:
            self._counter += 1
            jid = f"job_{self._counter}"
            self._jobs[jid] = {
                "id": jid,
                "project_id": payload.get("project_id", "default"),
                "stage": payload.get("stage", "render"),
                "status": JobStatus.PENDING.value,
                "payload": payload,
                "created_at": datetime.utcnow().isoformat(),
            }
            return jid

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.get(job_id)

    def process_job(self, job_id: str) -> StandardMediaResult:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return StandardMediaResult(media_id="", status="FAILED", error="JOB_NOT_FOUND")
            
            payload = job.get("payload", {})
            if payload.get("simulated_failure"):
                job["status"] = JobStatus.FAILED.value
                return StandardMediaResult(
                    media_id=job_id,
                    status="FAILED",
                    error="PROCESSING_FAILED",
                    file_size_bytes=0
                )
            
            job["status"] = JobStatus.COMPLETED.value
            return StandardMediaResult(
                media_id=job_id,
                status="COMPLETED",
                url=f"https://storage.cdn.local/{job_id}.mp4",
                file_size_bytes=1024576
            )
