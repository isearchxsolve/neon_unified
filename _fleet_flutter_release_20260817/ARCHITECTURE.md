## Overview
`fleet_flutter_release_20260817` is a habit tracking application consisting of a Flutter mobile client and a FastAPI backend. The system provides user authentication, habit management (CRUD), daily habit completion tracking, and an aggregated dashboard. The architecture follows a strict layered design to ensure separation of concerns, testability, and maintainability. State is managed locally on the device and synchronized with the backend via RESTful JSON APIs secured by JWT.

## Components
*   **Flutter Client (`fleet_app`)**: The front-end application. Built with a feature-first directory structure. Core components include `AuthNotifier` (Riverpod state manager for auth), `HabitsRepository` (local API client), and `DashboardScreen`.
*   **FastAPI Backend (`fleet_api`)**: The Python RESTful API server. Handles HTTP request parsing, JWT validation, and HTTP response generation.
*   **PostgreSQL Database**: The primary persistent data store for users, habits, and completion logs.
*   **Redis**: The rate-limiting and token-blacklist store (for logging out/invalidating JWTs before expiry).

## Data Flow
1.  **Authentication**: User enters credentials in `flutter:ui/screens/auth_screen.dart`. `flutter:features/auth/notifiers/auth_notifier.dart` calls `flutter:core/network/api_client.dart`, which sends a POST to `/api/auth/login`. FastAPI's `AuthController` routes the request to `auth_service.py`, which verifies the password hash via `user_repository.py` and returns a JWT.
2.  **Habit Completion**: User taps "Complete" on `flutter:ui/screens/habit_detail_screen.dart`. `flutter:features/habits/notifiers/habit_detail_notifier.dart` sends a POST to `/api/habits/{habit_id}/complete`. The API's `HabitController` delegates to `habit_service.py`, which uses `habit_repository.py` to insert a record into the `habit_completions` table.
3.  **Dashboard Load**: User navigates to the Dashboard tab. `flutter:features/dashboard/notifiers/dashboard_notifier.dart` requests GET `/api/habits`. `HabitController` calls `habit_service.py` to fetch habits and join them with recent completions, returning a unified payload for the UI to render streaks and statuses.

## Tech Stack
*   **Mobile**: Flutter 3.x, Riverpod (state management), Dio (HTTP), GoRouter (navigation), Hive (local offline cache).
*   **Backend**: Python 3.11, FastAPI, Pydantic V2, SQLAlchemy 2.0 (async), Alembic (migrations), Uvicorn (ASGI server).
*   **Database**: PostgreSQL 15.
*   **Cache/State**: Redis 7.
*   **Infrastructure**: Docker, Docker Compose.

## Layering
The system strictly adheres to the API -> Service -> Repository/Domain pattern. 

**Backend (FastAPI - `app/`)**:
*   **API Layer**: `app/api/routers/`
    *   `health.py`: Handles GET `/api/health`.
    *   `auth.py`: Handles `/api/auth/register` and `/api/auth/login`.
    *   `habits.py`: Handles GET, POST, PUT, DELETE for `/api/habits`, and completion actions. Validates JWT dependencies.
*   **Service Layer**: `app/services/`
    *   `auth_service.py`: Password hashing, JWT generation, blacklisting logic.
    *   `habit_service.py`: Orchestrates habit creation, streak calculation, and completion logic.
    *   `dashboard_service.py`: Aggregates habit and completion data for the unified dashboard response.
*   **Repository/Domain Layer**: `app/repositories/`
    *   `user_repository.py`: Direct SQLAlchemy `User` model queries (CREATE, GET BY EMAIL).
    *   `habit_repository.py`: Direct SQLAlchemy `Habit` and `HabitCompletion` queries. Contains atomic transaction logic for adding completions and ensuring constraints (e.g., one completion per day).
*   **Models/Schemas**: `app/models/` (SQLAlchemy ORM), `app/schemas/` (Pydantic models for request/response validation).

**Client (Flutter - `lib/`)**:
*   **UI Layer**: `lib/ui/screens/` (Strictly renders state, contains no business logic).
*   **Notifier Layer (Controller)**: `lib/features/*/notifiers/` (Riverpod state management, calls repositories, holds view state).
*   **Repository Layer**: `lib/core/repositories/` (Wraps API calls, handles offline fallback via Hive cache).

## Auth & Security
*   **Password Security**: Passwords are hashed using `bcrypt` via `passlib` in `auth_service.py`. Plaintext passwords are never logged or persisted.
*   **JWT Authentication**: FastAPI uses OAuth2 with JWT Bearer tokens. Tokens are signed using an HMAC secret stored in server environment variables. Token lifespan is 24 hours.
*   **Authorization Middleware**: `app/core/security.py` contains the `get_current_user` dependency. It decodes the JWT, checks the Redis blacklist, and queries the database. This dependency is injected into all `/api/habits` endpoints.
*   **Data Isolation**: All queries in `habit_repository.py` are parameterized and explicitly filtered by `user_id = current_user.id` to prevent Insecure Direct Object Reference (IDOR) vulnerabilities.

## Data Model
*   **`users`** (Table)
    *   `id` (UUID, PK)
    *   `email` (VARCHAR, UNIQUE, NOT NULL)
    *   `hashed_password` (VARCHAR, NOT NULL)
    *   `created_at` (TIMESTAMP)
*   **`habits`** (Table)
    *   `id` (UUID, PK)
    *   `user_id` (UUID, FK -> users.id)
    *   `name` (VARCHAR, NOT NULL)
    *   `frequency` (ENUM: DAILY, WEEKLY)
    *   `target_count` (INT, default 1)
    *   `created_at` (TIMESTAMP)
*   **`habit_completions`** (Table)
    *   `id` (UUID, PK)
    *   `habit_id` (UUID, FK -> habits.id, ON DELETE CASCADE)
    *   `completed_date` (DATE, NOT NULL)
    *   `created_at` (TIMESTAMP)
    *   *Constraint*: UNIQUE (`habit_id`, `completed_date`) to prevent double-completion per day.

## Error Handling
*   **Backend**: FastAPI utilizes custom exception handlers in `app/core/exceptions.py`.
    *   `NotFoundException`: Returns 404 (e.g., habit not found or belongs to another user).
    *   `ConflictException`: Returns 409 (e.g., API call attempts to mark a habit complete twice on the same day).
    *   `ValidationException`: Returns 422 (handled natively by FastAPI/Pydantic).
    *   All expected errors return a structured JSON response: `{"error": {"code": "NOT_FOUND", "message": "Habit not found"}}`.
*   **Client**: `lib/core/network/api_client.dart` intercepts Dio errors. If a 401 Unauthorized is returned, Riverpod's `AuthNotifier` intercepts the event and triggers a global logout, routing the user to `AuthScreen`. Network timeouts display a persistent snackbar via a global GoRouter observer.

## Background Work
None required. Habit completion tracking requires immediate user feedback and relies on synchronous API calls. Streak calculations are simple aggregations executed on-the-fly during the dashboard read request, negating the need for background workers or scheduled cron jobs for this version.

## Scalability Notes
*   **Database**: The `habit_completions` table will grow linearly with user activity. A composite index on `(habit_id, completed_date)` ensures fast lookups for streak calculations. 
*   **Connection Pooling**: SQLAlchemy is configured with `AsyncAdaptedQueuePool` to manage database connections efficiently.
*   **Statelessness**: The FastAPI backend is completely stateless. JWTs mean the API can scale horizontally across multiple containers with no sticky-session requirements. Redis is used as a centralized JWT blacklist store so blacklisted tokens are recognized across all API instances.

## Failure Modes
*   **Database Unavailable**: FastAPI's asyncpg connection will timeout. The API returns HTTP 503 Service Unavailable. Flutter's Dio interceptor catches 503s and displays an offline banner, falling back to locally cached habits stored in Hive.
*   **Stale Cache on Device**: If the user completes a habit on another device, the current device's local Hive cache may be stale. Flutter handles this by clearing the local cache cache on application resume/pull-to-refresh and performing a fresh `GET /api/habits`.
*   **Rate Limiting**: If the user spams the API, FastAPI's slowapi middleware returns 429 Too Many Requests. The Flutter UI handles this by throttling UI interactions and showing a brief "Too many actions" toast.