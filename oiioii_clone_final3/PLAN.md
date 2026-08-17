# AI Animation Agent Platform (oiioii-style) - Project Plan

## Requirements
### Core Features
- User authentication and project management
- Creative workflow orchestration (script -> character -> scene -> storyboard -> render -> sound)
- Job system with media failure handling
- Asset store with MediaGenerationService
- MediaGenerationService using API keys from env
- Workflow/jobs/assets APIs
- Polished workspace UI with agent timeline and asset gallery

## Risks
- External API rate limits and outages for media generation (NVIDIA NIM, ElevenLabs)
- Sensitive API key exposure - must use environment variables only, never commit
- Media generation can be slow / timeout - need structured job failures and retries
- Cost overruns from unlimited generation - need rate limiting and quotas per user
- Large media files - need storage abstraction and CDN considerations
- Auth security - JWT secret rotation, password hashing, session management
- Frontend state sync with long-running async jobs - need polling or SSE/WebSocket

## Acceptance Criteria
- [scaffold] Project scaffold exists with backend (FastAPI) and frontend (React) directories
- [architecture] ARCHITECTURE.md documents system design, data models, API surface
- [tests] Test suite exists and passes (pytest for backend, vitest/jest for frontend)
- [auth] User signup/login endpoints with JWT, password hashing (bcrypt)
- [projects] CRUD for animation projects per user
- [workflow] Pipeline that chains script -> character -> scene -> storyboard -> render -> sound
- [jobs] Async job queue with status tracking and structured failure handling
- [assets] Asset store with download/upload, integrated into MediaGenerationService
- [ui] Workspace page with agent timeline visualization and asset gallery
- [secrets] All API keys loaded from environment, never hardcoded

## Requirements
### Core Features
- User authentication and project management
- Job system with media failure handling
- Asset store with MediaGenerationService