"""
Data models for AI Animation Agent Platform.

Defines core entities: User, Project, Workflow, Job, Asset, Script, Storyboard, Render.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field
import uuid


class JobStatus(Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineStage(Enum):
    """Creative pipeline stages."""
    SCRIPT = "script"
    CHARACTER = "character"
    SCENE = "scene"
    STORYBOARD = "storyboard"
    RENDER = "render"
    SOUND = "sound"


@dataclass
class User:
    """User entity with authentication support."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    api_key: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }


@dataclass
class Project:
    """Animation project entity."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    user_id: str = ""
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "user_id": self.user_id,
            "settings": self.settings,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active
        }


@dataclass
class Script:
    """Script/storyboard text entity."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    title: str = ""
    content: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class Character:
    """Character design entity."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    name: str = ""
    description: str = ""
    image_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image_url,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Scene:
    """Scene/environment entity."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    name: str = ""
    description: str = ""
    background_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "background_url": self.background_url,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Storyboard:
    """Storyboard sequence entity."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    script_id: Optional[str] = None
    scenes: List[str] = field(default_factory=list)  # List of scene IDs
    frames: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "script_id": self.script_id,
            "scenes": self.scenes,
            "frames": self.frames,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class Render:
    """Final render entity."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    storyboard_id: Optional[str] = None
    output_url: Optional[str] = None
    duration: float = 0.0
    resolution: str = "1920x1080"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "storyboard_id": self.storyboard_id,
            "output_url": self.output_url,
            "duration": self.duration,
            "resolution": self.resolution,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Asset:
    """Asset in the asset store."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    asset_type: str = ""  # character, scene, audio, video, etc.
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_public: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "asset_type": self.asset_type,
            "url": self.url,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "is_public": self.is_public
        }


@dataclass
class Job:
    """Job entity for async processing."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    stage: PipelineStage = PipelineStage.SCRIPT
    status: JobStatus = JobStatus.PENDING
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "stage": self.stage.value,
            "status": self.status.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    def mark_started(self):
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()

    def mark_completed(self, output_data: Optional[Dict[str, Any]] = None):
        self.status = JobStatus.COMPLETED
        self.output_data = output_data
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error_message: str):
        self.status = JobStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()


@dataclass
class Workflow:
    """Workflow orchestration entity."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    stages: List[PipelineStage] = field(default_factory=lambda: list(PipelineStage))
    current_stage: PipelineStage = PipelineStage.SCRIPT
    jobs: List[str] = field(default_factory=list)  # List of job IDs
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "stages": [s.value for s in self.stages],
            "current_stage": self.current_stage.value,
            "jobs": self.jobs,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active
        }

    def advance_stage(self) -> Optional[PipelineStage]:
        """Advance to the next stage. Returns the new stage or None if complete."""
        try:
            current_idx = self.stages.index(self.current_stage)
            if current_idx + 1 < len(self.stages):
                self.current_stage = self.stages[current_idx + 1]
                self.updated_at = datetime.utcnow()
                return self.current_stage
        except ValueError:
            pass
        return None

    def is_complete(self) -> bool:
        """Check if workflow has completed all stages."""
        return self.current_stage == PipelineStage.SOUND