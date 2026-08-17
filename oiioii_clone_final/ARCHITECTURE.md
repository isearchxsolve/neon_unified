# AI Animation Agent Platform (oiioii-style) - Architecture Document

## Components

### Frontend Workspace UI
- React-based dashboard with timeline and asset gallery
- Real-time job status updates via WebSocket
- Drag-and-drop asset management

### Backend API Layer
- FastAPI RESTful endpoints for all services
- JWT-based authentication with API key support
- CORS and rate limiting middleware

### Authentication Service
- User registration and login endpoints
- API key generation and rotation
- Token-based session management

### Project Management Service
- CRUD operations for animation projects
- Project metadata and settings storage
- Version control integration

### Creative Workflow Engine
- Script stage: Text-based storyboarding
- Character stage: AI-generated character design
- Scene stage: Environment creation
- Storyboard stage: Visual sequence planning
- Render stage: Final animation rendering
- Sound stage: Audio generation and sync

### Job Processing System
- Asynchronous task queue with Redis
- Media generation job tracking
- Failure handling and retry logic

### Asset Store Service
- Centralized media repository
- Character, scene, and asset management
- Metadata indexing and search

### MediaGenerationService
- NVIDIA NIM API integration
- External AI service connectors
- API key management from environment

## Data Flow

1. User authenticates via API key -> receives JWT token
2. User creates project -> project stored in database
3. User initiates workflow -> workflow engine orchestrates stages
4. Each stage creates job -> job queued for async processing
5. Job processor calls MediaGenerationService -> external API invoked
6. Media generated and stored in asset store
7. Job status updated -> UI receives real-time update
8. User accesses generated assets via gallery

## Tech Stack
- Backend: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
- Frontend: React 18, TypeScript, Tailwind CSS
- Queue: Redis, RQ (Redis Queue)
- Auth: JWT, OAuth2
- Media: NVIDIA NIM API, FFmpeg
- Deployment: Docker, Docker Compose, Nginx