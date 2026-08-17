## Overview
The _fleet_flutter_release_attempt2_20260817_ project is a habit tracker application consisting of a Flutter mobile client and a FastAPI backend. The system provides user authentication, habit management, daily habit completion tracking, and an aggregated dashboard. The backend strictly limits its API surface to health checks, authentication, and habit CRUD operations, delegating dashboard logic to the client via aggregation of the `/api/habits` endpoint.

## Components
* **Flutter Client (`fleet_app`)**: The single mobile application binary. Handles UI rendering, local state management, API communication, and dashboard calculation.
* **FastAPI Backend (`fleet_api`)**: The Python web server. Serves the defined API surface and interfaces with the database.
* **PostgreSQL DB**: The persistent datastore for user credentials and habit records.

## Data Flow
1. **Registration/Login**: User enters credentials in Flutter (`AuthScreen`) -> HTTP POST to `/api/auth/register` or `/api/auth/login` -> API validates and returns JWT.
2. **Habit Management**: User creates a habit in Flutter (`HabitListScreen`) -> HTTP POST to `/api/habits` -> API persists -> returns Habit object.
3. **Mark Complete**: User taps complete on a habit (`DashboardScreen` or `HabitDetailScreen`) -> HTTP PATCH to `/api/habits` -> API updates `HabitCompletion` timestamp -> returns updated Habit.
4. **Dashboard Rendering**: App fetches all habits via `GET /api/habits` -> Client-side `DashboardCalculator` computes current streaks based on `completed_dates` and renders the dashboard UI.

## Tech Stack
* **Client**: Flutter 3.x, `dio` (HTTP), `flutter_riverpod` (State Management), `flutter_secure_storage` (JWT storage), `go_router` (Navigation).
* **Server**: Python 3.11, FastAPI, Pydantic v2, Uvicorn.
* **Database**: PostgreSQL 15, `asyncpg` (Async DB driver), `SQLAlchemy 2.0` (ORM).

## Layering
Backend (Python package: `app/`)
* **API Layer**: `app/api/routers.py`. Defines FastAPI routes for `/api/health`, `/api/auth/*`, and `/api/habits`. Serializes/deserializes Pydantic models (`app/schemas.py`).
* **Service Layer**: `app/services/auth_service.py` (password hashing, JWT generation) and `app/services/habit_service.py` (habit creation logic, completion timestamp appending). Contains business rules.
* **Repository Layer**: `app/repositories/user_repo.py` and `app/repositories/habit_repo.py`. Encapsulates SQLAlchemy queries. Returns SQLAlchemy model instances.
* **Domain/DB Layer**: `app/models.py`. Defines `User` and `Habit` SQLAlchemy ORM models.
* **Dependency Injection**: `app/deps.py`. Provides database session (`get_db`) and current authenticated user (`get_current_user`) dependencies for the API layer.

Flutter Client (package: `fleet_app/`)
* **View Layer**: `lib/ui/screens/auth_screen.dart`, `lib/ui/screens/habit_list_screen.dart`, `lib/ui/screens/dashboard_screen.dart`. Consumes providers and renders widgets.
* **State/Service Layer**: `lib/state/auth_provider.dart`, `lib/state/habit_provider.dart`. Manages application state, triggers API calls, and holds UI state.
* **Data/Repository Layer**: `lib/data/api_client.dart` (Dio instance with interceptors for JWT injection), `lib/data/repositories/auth_repository.dart`, `lib/data/repositories/habit_repository.dart`.
* **Domain Layer**: `lib/domain/dashboard_calculator.dart` (pure Dart functions computing streaks from habit lists), `lib/domain/models/habit.dart` (UI data classes).

## Auth & Security
* Authentication is implemented via JSON Web Tokens (JWT).
* Passwords are hashed using `bcrypt` via `passlib` in `auth_service.py` before reaching the repository layer.
* JWTs are signed using a symmetric HS256 secret stored in server environment variables.
* API endpoints under `/api/habits` require the `Authorization: Bearer <token>` header. The `get_current_user` dependency in `app/deps.py` decodes the JWT, queries the `User` from `user_repo`, and injects it into the service layer.
* The Flutter client stores the JWT in `flutter_secure_storage` (iOS Keychain / Android Keystore) and injects it globally via a Dio Interceptor in `lib/data/api_client.dart`.
* Users can only access their own habits; `habit_service.py` explicitly filters all queries by the `user_id` derived from the JWT.

## Data Model
Defined in `app/models.py`:
* **`User`**:
  * `id` (UUID, Primary Key)
  * `email` (String, Unique, Indexed)
  * `hashed_password` (String)
  * `created_at` (Timestamp)
* **`Habit`**:
  * `id` (UUID, Primary Key)
  * `user_id` (UUID, Foreign Key -> `User.id`)
  * `name` (String)
  * `created_at` (Timestamp)
  * `completed_dates` (ARRAY of Date). Appended to when a habit is marked complete.

## Error Handling
* **Client**: Dio interceptor in `api_client.dart` catches 401 responses and triggers a redirect to `AuthScreen` via `go_router`, clearing the secure storage. Network errors are caught in `habit_provider.dart` and surfaced to the UI as generic `AsyncError` states via Riverpod.
* **Server**: FastAPI's `HTTPException` is raised in the Service or API layers.
  * `409 Conflict` for duplicate email registration.
  * `401 Unauthorized` for invalid credentials or expired JWTs.
  * `404 Not Found` if a user attempts to modify or mark complete a habit that does not belong to them.
  * `422 Unprocessable Entity` is automatically handled by FastAPI for malformed Pydantic payloads.
* Unhandled server exceptions are caught by a global FastAPI exception handler middleware added in `app/main.py` and returned as `500 Internal Server Error` without stack trace leakage.

## Background Work
None required. For this specific scope, dashboard analytics (like longest streak) are computed synchronously by the client upon retrieving the habit list via `GET /api/habits`. If streak aggregation becomes computationally heavy in the future, a scheduled background task (e.g., Celery beat) could be introduced to precompute aggregates nightly, but it is strictly unnecessary for the current allowed surface.

## Scalability Notes
* **Database**: The `completed_dates` array on the `Habit` table will grow indefinitely over years. For a 5-year habit, this is ~1800 dates, which is negligible for PostgreSQL. However, if high-frequency tracking (e.g., multiple times a day) is later introduced, this should be refactored to a separate `HabitCompletion` table with an index on `(habit_id, completed_at)`.
* **API**: FastAPI running on Uvicorn is asynchronous. `asyncpg` is used as the SQLAlchemy driver, allowing the single-threaded event loop to handle concurrent I/O-bound requests efficiently.
* **State**: The Flutter app uses Riverpod `AsyncNotifier`s to cache the list of habits. When a habit is marked complete, the provider optimistically updates the local state list and fires the API request in the background, preventing UI jank and unnecessary full reloads.

## Failure Modes
* **API Downtime**: If the FastAPI backend is unreachable, the Dio requests in the Flutter app will timeout. Riverpod will transition the `habit_provider` to the `AsyncError` state. The UI will display a retry button. Existing authenticated sessions and JWTs remain in secure storage, so no forced logouts occur.
* **Database Connection Pool Exhaustion**: Under heavy load, if the SQLAlchemy pool is exhausted, API requests will block or timeout. Configured via `create_async_engine` with `pool_size=10` and `max_overflow=20` in `app/database.py`. If exceeded, FastAPI will return `503 Service Unavailable` if a connection timeout is set, or the request will hang until client timeout.
* **Token Expiration**: If the JWT expires on the server while the app is open, the next `GET /api/habits` request will fail with `401`. The Dio interceptor catches this, deletes the local JWT, and redirects the user to the `AuthScreen` to re-authenticate.
* **Clock Skew**: When marking habits complete, the `habit_service.py` appends the `datetime.utcnow().date()` to the `completed_dates` array. If the Flutter device clock is significantly skewed, the UI might display dates that do not align with server records. To mitigate, completion dates are strictly derived server-side, and the server ignores any client-provided completion timestamps.