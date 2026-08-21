"""FastAPI routes for auth, projects, workflows, jobs.

Token auth: every non-auth route requires `Authorization: Bearer <token>`
issued by POST /api/auth/login. Ownership is enforced for project-scoped
writes. All responses use the models' to_dict() shape.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from src.auth import AuthError, AuthService
from src.jobs import get_job_service
from src.models import PipelineStage
from src.projects import ProjectError, ProjectService
from src.workflows import get_workflow_service

router = APIRouter(prefix="/api")

_auth_service = AuthService()
_project_service = ProjectService()


# ── request models ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str = Field(min_length=1)
    email: str = Field(min_length=3)
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    username: str
    password: str


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str = ""


class WorkflowCreate(BaseModel):
    stages: Optional[List[str]] = None


class JobCreate(BaseModel):
    stage: str
    input_data: Dict[str, Any] = Field(default_factory=dict)


class JobComplete(BaseModel):
    output_data: Dict[str, Any] = Field(default_factory=dict)


class JobFail(BaseModel):
    error_message: str


# ── auth dependency ─────────────────────────────────────────────────────────

def current_user(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    user = _auth_service.verify_token(authorization[len("Bearer "):])
    if user is None:
        raise HTTPException(status_code=401, detail="invalid or expired token")
    return user


def _require_owner(project_id: str, user) -> Dict[str, Any]:
    project = _project_service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    if not _project_service.is_owner(project_id, user.id):
        raise HTTPException(status_code=403, detail="not the project owner")
    return project


def _parse_stage(raw: str) -> PipelineStage:
    try:
        return PipelineStage(raw)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"unknown stage: {raw}")


# ── auth routes ─────────────────────────────────────────────────────────────

@router.post("/auth/register", status_code=201)
def register(body: RegisterRequest):
    try:
        user = _auth_service.register(body.username, body.email, body.password)
    except AuthError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return user.to_dict()


@router.post("/auth/login")
def login(body: LoginRequest):
    try:
        token = _auth_service.login(body.username, body.password)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return {"token": token}


@router.post("/auth/logout", status_code=204)
def logout(user=Depends(current_user), authorization: str = Header(default="")):
    _auth_service.logout(authorization[len("Bearer "):])
    return None


# ── project routes ──────────────────────────────────────────────────────────

@router.get("/projects")
def list_projects(user=Depends(current_user)):
    return [p.to_dict() for p in _project_service.list_projects(user.id)]


@router.post("/projects", status_code=201)
def create_project(body: ProjectCreate, user=Depends(current_user)):
    try:
        project = _project_service.create_project(
            user.id, body.name, body.description)
    except ProjectError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return project.to_dict()


@router.get("/projects/{project_id}")
def get_project(project_id: str, user=Depends(current_user)):
    project = _project_service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    return project.to_dict()


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: str, user=Depends(current_user)):
    _require_owner(project_id, user)
    _project_service.delete_project(project_id)
    return None


# ── workflow routes ─────────────────────────────────────────────────────────

@router.post("/projects/{project_id}/workflows", status_code=201)
def create_workflow(project_id: str, body: WorkflowCreate, user=Depends(current_user)):
    _require_owner(project_id, user)
    stages = None
    if body.stages:
        stages = [_parse_stage(s) for s in body.stages]
    try:
        workflow = get_workflow_service().create_workflow(project_id, stages)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return workflow.to_dict()


@router.get("/workflows/{workflow_id}")
def get_workflow(workflow_id: str, user=Depends(current_user)):
    workflow = get_workflow_service().get_workflow(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="workflow not found")
    return workflow.to_dict()


@router.post("/workflows/{workflow_id}/advance")
def advance_workflow(workflow_id: str, user=Depends(current_user)):
    service = get_workflow_service()
    if service.get_workflow(workflow_id) is None:
        raise HTTPException(status_code=404, detail="workflow not found")
    new_stage = service.advance_workflow(workflow_id)
    return {"completed": new_stage is None,
            "current_stage": new_stage.value if new_stage else None}


# ── job routes ──────────────────────────────────────────────────────────────

@router.post("/projects/{project_id}/jobs", status_code=201)
def create_job(project_id: str, body: JobCreate, user=Depends(current_user)):
    _require_owner(project_id, user)
    stage = _parse_stage(body.stage)
    job = get_job_service().create_job(project_id, stage, body.input_data)
    return job.to_dict()


@router.get("/jobs/{job_id}")
def get_job(job_id: str, user=Depends(current_user)):
    job = get_job_service().get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job.to_dict()


@router.post("/jobs/{job_id}/start")
def start_job(job_id: str, user=Depends(current_user)):
    if not get_job_service().start_job(job_id):
        raise HTTPException(status_code=409, detail="job cannot be started")
    return get_job_service().get_job(job_id).to_dict()


@router.post("/jobs/{job_id}/complete")
def complete_job(job_id: str, body: JobComplete, user=Depends(current_user)):
    if not get_job_service().complete_job(job_id, body.output_data):
        raise HTTPException(status_code=409, detail="job cannot be completed")
    return get_job_service().get_job(job_id).to_dict()


@router.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: str, user=Depends(current_user)):
    if not get_job_service().cancel_job(job_id):
        raise HTTPException(status_code=409, detail="job cannot be cancelled")
    return get_job_service().get_job(job_id).to_dict()


def create_app() -> FastAPI:
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(title="oiioii clone final")
    app.add_middleware(CORSMiddleware, allow_origins=["*"],
                       allow_credentials=True, allow_methods=["*"],
                       allow_headers=["*"])

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    app.include_router(router)
    return app
