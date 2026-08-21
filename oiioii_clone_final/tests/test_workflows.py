"""WorkflowService unit tests."""

import pytest

from src.models import PipelineStage
from src.storage import reset_all_stores
from src.workflows import get_workflow_service


@pytest.fixture()
def service():
    reset_all_stores()
    return get_workflow_service(reset=True)


def test_create_workflow_defaults_to_full_pipeline(service):
    wf = service.create_workflow("proj-1")
    assert wf.project_id == "proj-1"
    assert wf.stages == list(PipelineStage)
    assert wf.current_stage == PipelineStage.SCRIPT
    assert wf.is_active is True


def test_create_workflow_requires_project_id(service):
    with pytest.raises(ValueError):
        service.create_workflow("")


def test_create_workflow_with_custom_stages(service):
    wf = service.create_workflow("proj-1",
                                 stages=[PipelineStage.SCRIPT, PipelineStage.RENDER])
    assert wf.stages == [PipelineStage.SCRIPT, PipelineStage.RENDER]
    assert wf.current_stage == PipelineStage.SCRIPT


def test_advance_walks_then_completes(service):
    wf = service.create_workflow("proj-1",
                                 stages=[PipelineStage.SCRIPT, PipelineStage.RENDER])
    assert service.advance_workflow(wf.id) == PipelineStage.RENDER
    assert service.advance_workflow(wf.id) is None
    assert service.get_workflow(wf.id).is_active is False
    assert service.advance_workflow(wf.id) is None


def test_list_filters_by_project(service):
    service.create_workflow("proj-1")
    service.create_workflow("proj-2")
    assert len(service.list_workflows()) == 2
    assert len(service.list_workflows("proj-1")) == 1


def test_attach_job_dedupes(service):
    wf = service.create_workflow("proj-1")
    assert service.attach_job(wf.id, "job-1") is True
    assert service.attach_job(wf.id, "job-1") is True
    assert service.get_workflow(wf.id).jobs == ["job-1"]
    assert service.attach_job("missing", "job-1") is False


def test_deactivate(service):
    wf = service.create_workflow("proj-1")
    assert service.deactivate(wf.id) is True
    assert service.get_workflow(wf.id).is_active is False
    assert service.deactivate("missing") is False
