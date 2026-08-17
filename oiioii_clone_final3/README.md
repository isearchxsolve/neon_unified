# AI Animation Agent Platform (oiioii-style)

Full-stack AI animation agent platform with auth, projects, creative workflow orchestration (script → character → scene → storyboard → render → sound), job system, asset store, and MediaGenerationService integration.

## Features
- User authentication with JWT tokens
- Project management with user isolation
- Creative workflow pipeline (6 stages)
- Async job system with structured failure handling
- Asset gallery and storage
- Media generation via external APIs (NVIDIA NIM, ElevenLabs) using env keys
- Workspace UI with agent timeline

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, JWT, bcrypt
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Media APIs**: NVIDIA NIM, ElevenLabs

## Project Structure
```
backend/          # FastAPI backend
  auth/           # Authentication module
  projects/       # Project management
  workflows/      # Workflow orchestration
  jobs/           # Job queue and tracking
  assets/         # Asset store
  media/          # MediaGenerationService
frontend/         # React frontend
tests/            # Test suite
```

## Getting Started

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - JWT signing secret
- `NVIDIA_NIM_API_KEY` - NVIDIA NIM API key for image generation
- `ELEVENLABS_API_KEY` - ElevenLabs API key for voice synthesis

## Testing
```bash
pytest tests/
```
