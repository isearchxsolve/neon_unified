# Architecture — AI Animation Agent Platform

## Overview
Creator platform that turns a plain-language idea into animation assets via a
multi-stage agent workflow, backed by external media model APIs.

## Components
- API (FastAPI): auth, projects, workflows, jobs, assets, media proxy
- Worker: executes workflow stages asynchronously
- MediaGenerationService: provider-agnostic image/video/audio client (API keys from env)
- Web app: project workspace, agent timeline, asset gallery, job status
- DB: users, projects, jobs, assets, workflow runs

## Data Flow
1. User creates project + idea
2. API enqueues workflow run
3. Worker advances stages: script → character → scene → storyboard → render → sound
4. Each stage writes Job rows + Asset rows
5. UI polls jobs and displays assets

## Tech Stack
- Backend: FastAPI, SQLAlchemy/Postgres, Redis queue (or in-process for MVP)
- Frontend: React/Next + design tokens + primitives
- Media: external APIs via MediaGenerationService

## Layering
- routers/ → thin HTTP
- services/workflow_service.py → orchestration
- services/media_service.py → API keys + providers
- repositories/ → persistence

## Auth & Security
- JWT auth
- API keys only from environment / secret store
- Per-user project isolation

## Failure Modes
- Media provider errors → job FAILED with structured error, retryable
- Partial stage success → assets kept, workflow resumable from failed stage
