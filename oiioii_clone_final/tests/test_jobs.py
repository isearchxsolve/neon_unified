"""
Tests for Job management module.
"""

import pytest
from datetime import datetime

from src.models import Job, JobStatus, PipelineStage
from src.jobs import JobService, get_job_service


class TestJobService:
    """Test cases for JobService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = JobService()
    
    def test_create_job_creates_job_with_defaults(self):
        """Test that creating a job sets correct defaults."""
        job = self.service.create_job(project_id="proj-123", stage=PipelineStage.SCRIPT)
        
        assert job.id is not None
        assert job.project_id == "proj-123"
        assert job.stage == PipelineStage.SCRIPT
        assert job.status == JobStatus.PENDING
        assert job.input_data == {}
        assert job.error_message is None
    
    def test_create_job_with_input_data(self):
        """Test that creating a job stores input data."""
        input_data = {"script": "Hello world", "duration": 10}
        job = self.service.create_job(
            project_id="proj-123",
            stage=PipelineStage.RENDER,
            input_data=input_data
        )
        
        assert job.input_data == input_data
    
    def test_get_job_returns_existing_job(self):
        """Test that get_job returns the correct job."""
        job = self.service.create_job(project_id="proj-123", stage=PipelineStage.SCRIPT)
        
        retrieved = self.service.get_job(job.id)
        
        assert retrieved is not None
        assert retrieved.id == job.id
    
    def test_get_job_returns_none_for_unknown_job(self):
        """Test that get_job returns None for unknown job ID."""
        result = self.service.get_job("nonexistent-id")
        
        assert result is None
    
    def test_list_jobs_returns_all_jobs(self):
        """Test that list_jobs returns all jobs when no filters."""
        job1 = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        job2 = self.service.create_job(project_id="proj-2", stage=PipelineStage.CHARACTER)
        
        jobs = self.service.list_jobs()
        
        assert len(jobs) == 2
        assert job1.id in [j.id for j in jobs]
        assert job2.id in [j.id for j in jobs]
    
    def test_list_jobs_filters_by_project(self):
        """Test that list_jobs filters by project_id."""
        job1 = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        job2 = self.service.create_job(project_id="proj-2", stage=PipelineStage.CHARACTER)
        
        jobs = self.service.list_jobs(project_id="proj-1")
        
        assert len(jobs) == 1
        assert jobs[0].id == job1.id
    
    def test_list_jobs_filters_by_status(self):
        """Test that list_jobs filters by status."""
        job1 = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        job2 = self.service.create_job(project_id="proj-2", stage=PipelineStage.CHARACTER)
        self.service.start_job(job1.id)
        
        pending_jobs = self.service.list_jobs(status=JobStatus.PENDING)
        running_jobs = self.service.list_jobs(status=JobStatus.RUNNING)
        
        assert len(pending_jobs) == 1
        assert len(running_jobs) == 1
    
    def test_list_jobs_filters_by_stage(self):
        """Test that list_jobs filters by stage."""
        job1 = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        job2 = self.service.create_job(project_id="proj-2", stage=PipelineStage.CHARACTER)
        
        script_jobs = self.service.list_jobs(stage=PipelineStage.SCRIPT)
        
        assert len(script_jobs) == 1
        assert script_jobs[0].id == job1.id
    
    def test_list_jobs_respects_limit(self):
        """Test that list_jobs respects the limit parameter."""
        for i in range(10):
            self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        
        jobs = self.service.list_jobs(limit=5)
        
        assert len(jobs) == 5
    
    def test_start_job_transitions_to_running(self):
        """Test that start_job transitions job to running state."""
        job = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        
        result = self.service.start_job(job.id)
        
        assert result is True
        assert job.status == JobStatus.RUNNING
        assert job.started_at is not None
    
    def test_start_job_fails_for_nonexistent_job(self):
        """Test that start_job returns False for nonexistent job."""
        result = self.service.start_job("nonexistent-id")
        
        assert result is False
    
    def test_start_job_fails_for_completed_job(self):
        """Test that start_job returns False for already completed job."""
        job = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        self.service.complete_job(job.id, {"output": "data"})
        
        result = self.service.start_job(job.id)
        
        assert result is False
    
    def test_complete_job_transitions_to_completed(self):
        """Test that complete_job transitions job to completed state."""
        job = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        self.service.start_job(job.id)
        output_data = {"result": "success"}
        
        result = self.service.complete_job(job.id, output_data)
        
        assert result is True
        assert job.status == JobStatus.COMPLETED
        assert job.output_data == output_data
        assert job.completed_at is not None
    
    def test_complete_job_fails_for_non_running_job(self):
        """Test that complete_job returns False for non-running job."""
        job = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        
        result = self.service.complete_job(job.id, {"output": "data"})
        
        assert result is False
    
    def test_fail_job_transitions_to_failed(self):
        """Test that fail_job transitions job to failed state."""
        job = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        self.service.start_job(job.id)
        error_msg = "Something went wrong"
        
        result = self.service.fail_job(job.id, error_msg)
        
        assert result is True
        assert job.status == JobStatus.FAILED
        assert job.error_message == error_msg
        assert job.completed_at is not None
    
    def test_fail_job_fails_for_non_running_job(self):
        """Test that fail_job returns False for non-running job."""
        job = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        
        result = self.service.fail_job(job.id, "error")
        
        assert result is False
    
    def test_cancel_job_transitions_to_cancelled(self):
        """Test that cancel_job transitions job to cancelled state."""
        job = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        
        result = self.service.cancel_job(job.id)
        
        assert result is True
        assert job.status == JobStatus.CANCELLED
        assert job.completed_at is not None
    
    def test_cancel_job_fails_for_completed_job(self):
        """Test that cancel_job returns False for completed job."""
        job = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        self.service.complete_job(job.id, {"output": "data"})
        
        result = self.service.cancel_job(job.id)
        
        assert result is False
    
    def test_delete_job_removes_job(self):
        """Test that delete_job removes job from storage."""
        job = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        
        result = self.service.delete_job(job.id)
        
        assert result is True
        assert self.service.get_job(job.id) is None
    
    def test_delete_job_fails_for_nonexistent_job(self):
        """Test that delete_job returns False for nonexistent job."""
        result = self.service.delete_job("nonexistent-id")
        
        assert result is False
    
    def test_retry_job_resets_failed_job(self):
        """Test that retry_job resets a failed job to pending."""
        job = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        self.service.start_job(job.id)
        self.service.fail_job(job.id, "error")
        
        result = self.service.retry_job(job.id)
        
        assert result is not None
        assert job.status == JobStatus.PENDING
        assert job.error_message is None
        assert job.started_at is None
        assert job.completed_at is None
    
    def test_retry_job_returns_none_for_non_failed_job(self):
        """Test that retry_job returns None for non-failed job."""
        job = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        
        result = self.service.retry_job(job.id)
        
        assert result is None
    
    def test_job_to_dict(self):
        """Test that Job.to_dict returns correct dictionary."""
        job = self.service.create_job(project_id="proj-1", stage=PipelineStage.SCRIPT)
        self.service.start_job(job.id)
        
        result = job.to_dict()
        
        assert result["id"] == job.id
        assert result["project_id"] == "proj-1"
        assert result["stage"] == "script"
        assert result["status"] == "running"
        assert "created_at" in result
        assert "started_at" in result
        assert "completed_at" in result


class TestJobModel:
    """Test cases for Job model."""
    
    def test_job_creation_with_defaults(self):
        """Test Job creation with default values."""
        job = Job()
        
        assert job.id is not None
        assert job.status == JobStatus.PENDING
        assert job.stage == PipelineStage.SCRIPT
        assert job.input_data == {}
    
    def test_job_mark_started(self):
        """Test Job.mark_started method."""
        job = Job()
        
        job.mark_started()
        
        assert job.status == JobStatus.RUNNING
        assert job.started_at is not None
    
    def test_job_mark_completed(self):
        """Test Job.mark_completed method."""
        job = Job()
        job.mark_started()
        output = {"result": "success"}
        
        job.mark_completed(output)
        
        assert job.status == JobStatus.COMPLETED
        assert job.output_data == output
        assert job.completed_at is not None
    
    def test_job_mark_failed(self):
        """Test Job.mark_failed method."""
        job = Job()
        job.mark_started()
        error = "Something went wrong"
        
        job.mark_failed(error)
        
        assert job.status == JobStatus.FAILED
        assert job.error_message == error
        assert job.completed_at is not None


class TestGetJobService:
    """Test cases for get_job_service singleton."""
    
    def test_get_job_service_returns_singleton(self):
        """Test that get_job_service returns the same instance."""
        service1 = get_job_service()
        service2 = get_job_service()
        
        assert service1 is service2