"""Creative workflow orchestrator — script→character→scene→storyboard→render→sound."""
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, Optional
from backend.services.media_service import MediaGenerationService, MediaRequest

class WorkflowStage(str, Enum):
    SCRIPT = "script"
    CHARACTER = "character"
    SCENE = "scene"
    STORYBOARD = "storyboard"
    RENDER = "render"
    SOUND = "sound"
    DONE = "done"

class WorkflowService:
    def __init__(self, media: Optional[MediaGenerationService] = None):
        self.media = media or MediaGenerationService()

    def start(self, project_id: str, idea: str, style: Optional[str] = None) -> Dict[str, Any]:
        """Enqueue or run workflow. Returns run state."""
        return {
            "project_id": project_id,
            "idea": idea,
            "style": style,
            "stage": WorkflowStage.SCRIPT.value,
            "status": "queued",
        }

    def advance(self, run_id: str) -> Dict[str, Any]:
        """Advance one stage; call media service as needed."""
        raise NotImplementedError("implement stage machine + job updates")
