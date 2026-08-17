"""Workflow + job HTTP API."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(tags=["workflows"])

class StartWorkflowIn(BaseModel):
    idea: str = Field(..., min_length=3)
    style: Optional[str] = None

@router.post("/projects/{project_id}/workflows")
def start_workflow(project_id: str, body: StartWorkflowIn):
    # Wire to WorkflowService.start
    return {"project_id": project_id, "idea": body.idea, "style": body.style, "status": "queued"}

@router.get("/projects/{project_id}/jobs")
def list_jobs(project_id: str):
    return {"project_id": project_id, "jobs": []}
