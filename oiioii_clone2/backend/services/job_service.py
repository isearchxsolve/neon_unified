"""Job queue abstractions."""
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

class JobService:
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def enqueue(self, project_id: str, stage: str, payload: Dict[str, Any]) -> str:
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
        return self._jobs.get(job_id)

    def list_for_project(self, project_id: str) -> List[Dict[str, Any]]:
        return [j for j in self._jobs.values() if j["project_id"] == project_id]
