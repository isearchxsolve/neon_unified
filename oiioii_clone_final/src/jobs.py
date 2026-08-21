"""
Job management module for AI Animation Agent Platform.

Provides JobService for creating, tracking, and managing async jobs
for media generation, script processing, rendering, etc.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import threading

from src.models import Job, JobStatus, PipelineStage

class JobService:
    """Thread-safe service for managing jobs in the animation pipeline."""

    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.RLock()

    def create_job(
        self,
        project_id: str,
        stage: PipelineStage,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Job:
        """Create a new job for a project at a given stage."""
        with self._lock:
            job = Job(
                project_id=project_id,
                stage=stage,
                input_data=input_data or {},
                status=JobStatus.PENDING
            )
            self._jobs[job.id] = job
            return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Retrieve a job by ID."""
        with self._lock:
            return self._jobs.get(job_id)

    def list_jobs(
        self,
        project_id: Optional[str] = None,
        status: Optional[JobStatus] = None,
        stage: Optional[PipelineStage] = None,
        limit: int = 100
    ) -> List[Job]:
        """List jobs with optional filtering."""
        with self._lock:
            jobs = list(self._jobs.values())

            if project_id:
                jobs = [j for j in jobs if j.project_id == project_id]
            if status:
                jobs = [j for j in jobs if j.status == status]
            if stage:
                jobs = [j for j in jobs if j.stage == stage]

            return jobs[:limit]

    def start_job(self, job_id: str) -> bool:
        """Mark a job as started."""
        with self._lock:
            job = self.get_job(job_id)
            if job and job.status == JobStatus.PENDING:
                job.mark_started()
                return True
            return False

    def complete_job(
        self,
        job_id: str,
        output_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Mark a job as completed with output data."""
        with self._lock:
            job = self.get_job(job_id)
            if job and job.status == JobStatus.RUNNING:
                job.mark_completed(output_data)
                return True
            return False

    def fail_job(self, job_id: str, error_message: str) -> bool:
        """Mark a job as failed with an error message."""
        with self._lock:
            job = self.get_job(job_id)
            if job and job.status == JobStatus.RUNNING:
                job.mark_failed(error_message)
                return True
            return False

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job."""
        with self._lock:
            job = self.get_job(job_id)
            if job and job.status in (JobStatus.PENDING, JobStatus.RUNNING):
                job.status = JobStatus.CANCELLED
                job.completed_at = datetime.utcnow()
                return True
            return False

    def delete_job(self, job_id: str) -> bool:
        """Delete a job from storage."""
        with self._lock:
            if job_id in self._jobs:
                del self._jobs[job_id]
                return True
            return False

    def retry_job(self, job_id: str) -> Optional[Job]:
        """Retry a failed job by resetting it to pending."""
        with self._lock:
            job = self.get_job(job_id)
            if job and job.status == JobStatus.FAILED:
                job.status = JobStatus.PENDING
                job.error_message = None
                job.started_at = None
                job.completed_at = None
                job.output_data = None
                return job
            return None

# Global job service instance
_job_service: Optional[JobService] = None
_service_lock = threading.Lock()

def get_job_service(reset: bool = False) -> JobService:
    """Get or create the global job service instance."""
    global _job_service
    with _service_lock:
        if _job_service is None or reset:
            _job_service = JobService()
        return _job_service
