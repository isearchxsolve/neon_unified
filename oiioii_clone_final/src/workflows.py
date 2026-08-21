"""Workflow orchestration module.

Thread-safe WorkflowService over the shared workflows_store, driving the
stage pipeline defined on the Workflow model.
"""

from datetime import datetime
from typing import List, Optional
import threading

from src.models import Workflow, PipelineStage
from src.storage import workflows_store


class WorkflowService:
    """Service for creating and advancing project workflows."""

    def __init__(self):
        self._workflows = workflows_store
        self._lock = threading.RLock()

    def create_workflow(
        self,
        project_id: str,
        stages: Optional[List[PipelineStage]] = None,
    ) -> Workflow:
        if not project_id:
            raise ValueError("project_id is required")
        with self._lock:
            workflow = Workflow(project_id=project_id)
            if stages:
                workflow.stages = list(stages)
                workflow.current_stage = workflow.stages[0]
            self._workflows.add(workflow.id, workflow)
            return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self._workflows.get(workflow_id)

    def list_workflows(self, project_id: Optional[str] = None) -> List[Workflow]:
        workflows = self._workflows.all()
        if project_id:
            workflows = [w for w in workflows if w.project_id == project_id]
        return workflows

    def advance_workflow(self, workflow_id: str) -> Optional[PipelineStage]:
        """Advance to the next stage. Returns the new stage, or None when the
        pipeline is complete (workflow deactivated)."""
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow or not workflow.is_active:
                return None
            new_stage = workflow.advance_stage()
            workflow.updated_at = datetime.utcnow()
            if new_stage is None:
                workflow.is_active = False
            return new_stage

    def attach_job(self, workflow_id: str, job_id: str) -> bool:
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow or not job_id:
                return False
            if job_id not in workflow.jobs:
                workflow.jobs.append(job_id)
            workflow.updated_at = datetime.utcnow()
            return True

    def deactivate(self, workflow_id: str) -> bool:
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow:
                return False
            workflow.is_active = False
            workflow.updated_at = datetime.utcnow()
            return True


_workflow_service: Optional[WorkflowService] = None


def get_workflow_service(reset: bool = False) -> WorkflowService:
    global _workflow_service
    if _workflow_service is None or reset:
        _workflow_service = WorkflowService()
    return _workflow_service
