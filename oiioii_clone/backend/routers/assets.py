"""Asset gallery API."""
from __future__ import annotations
from fastapi import APIRouter

router = APIRouter(tags=["assets"])

@router.get("/projects/{project_id}/assets")
def list_assets(project_id: str):
    return {"project_id": project_id, "assets": []}
