# AI Animation Agent Platform Architecture (oiioii-style) - System Design Document

## Overview
A full-stack AI animation agent platform that orchestrates creative workflows from script to rendered animation with integrated media generation services.

## Components

### Backend (FastAPI)
- **Auth Service**: User authentication, JWT token management, password hashing with bcrypt
- **Project Service**: CRUD operations for animation projects, user isolation
- **Workflow Service**: Pipeline orchestration (script → character → scene → storyboard → render → sound)
- **Job Service**: Async job queue with status tracking, retries, and structured failure handling
- **Asset Service**: Media asset storage, upload/download, CDN integration
- **MediaGenerationService**: Integration with NVIDIA NIM, ElevenLabs APIs, environment-based API keys

### Frontend (React)
- **Auth Pages**: Login, signup, session management
- **Workspace**: Agent timeline visualization, asset gallery
- **Project Dashboard**: Project list and management
- **Media Viewer**: Asset preview and playback

### Data Models
- **User**: id, email, password_hash, created_at
- **Project**: id, user_id, name, description, created_at, updated_at
- **Asset**: id, project_id, type, url, metadata, created_at
- **Job**: id, project_id, type, status, input, output, error, created_at, updated_at
- **WorkflowStep**: id, job_id, step_name, status, created_at

## Data Flow
1. User authenticates → JWT token issued
2. User creates project → Project record created
3. User uploads script → Job created for script processing
4. Workflow orchestrates steps: script → character → scene → storyboard → render → sound
5. Each step creates jobs, assets stored in asset service
6. MediaGenerationService handles external API calls with env-based keys
7. Failures captured as structured job errors with retry logic

## API Surface
- POST /auth/signup, POST /auth/login
- GET/POST/PUT/DELETE /projects
- GET/POST /workflows
- GET/POST /jobs
- GET/POST /assets
- GET /assets/{id}/download

## Tech Stack
- Backend: FastAPI, SQLAlchemy, PostgreSQL, Redis (job queue), JWT, bcrypt
- Frontend: React, TypeScript, Vite, Tailwind CSS
- Media: NVIDIA NIM API, ElevenLabs API
- Storage: Local filesystem abstraction, S3/CDN for production