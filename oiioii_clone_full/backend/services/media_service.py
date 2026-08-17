"""MediaGenerationService — API-key backed image/video/audio client."""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class MediaRequest:
    kind: str
    prompt: str
    style: Optional[str] = None
    reference_urls: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MediaResult:
    ok: bool
    kind: str
    url: Optional[str] = None
    error: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)

class MediaGenerationService:
    def __init__(self):
        self.image_key = os.getenv("IMAGE_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
        self.video_key = os.getenv("VIDEO_API_KEY") or self.image_key
        self.audio_key = os.getenv("AUDIO_API_KEY") or self.image_key

    def generate(self, req: MediaRequest) -> MediaResult:
        key = {"image": self.image_key, "video": self.video_key, "audio": self.audio_key}.get(req.kind, "")
        if not key:
            return MediaResult(ok=False, kind=req.kind, error=f"{req.kind.upper()}_API_KEY not set")
        # TODO: wire real provider HTTP call here
        return MediaResult(ok=False, kind=req.kind, error="provider call not configured")
