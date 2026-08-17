## Overview

This document describes the architecture for a notes application with authentication, built as a Flutter frontend communicating with a FastAPI backend. The system follows a clean layered architecture on both client and server, with clear separation between API, service, and repository layers. Authentication uses JWT tokens with refresh token rotation. Notes are scoped to authenticated users.

---

## Components

### Backend (FastAPI) — `backend/`

| Module | Path | Responsibility |
|--------|------|----------------|
| **App Entry** | `backend/app/main.py` | FastAPI app factory, middleware, router registration, lifespan events |
| **Config** | `backend/app/core/config.py` | Pydantic Settings: DB URL, JWT secret, token TTL, CORS origins |
| **Database** | `backend/app/core/database.py` | SQLAlchemy async engine, sessionmaker, `get_db` dependency |
| **Security** | `backend/app/core/security.py` | Password hashing (bcrypt), JWT encode/decode, token verification |
| **Exceptions** | `backend/app/core/exceptions.py` | Custom exception classes + global exception handlers |
| **Health Router** | `backend/app/api/v1/health.py` | `GET /api/health` — liveness/readiness |
| **Auth Router** | `backend/app/api/v1/auth.py` | `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/refresh` |
| **Notes Router** | `backend/app/api/v1/notes.py` | `GET /api/notes`, `POST /api/notes`, `GET /api/notes/{id}`, `PATCH /api/notes/{id}`, `DELETE /api/notes/{id}` |
| **Auth Service** | `backend/app/services/auth_service.py` | User registration, login, token pair generation, refresh logic |
| **Note Service** | `backend/app/services/note_service.py` | CRUD operations, ownership validation, pagination |
| **User Repository** | `backend/app/repositories/user_repository.py` | User CRUD, lookup by email, password verification |
| **Note Repository** | `backend/app/repositories/note_repository.py` | Note CRUD, list with pagination, ownership filtering |
| **Models** | `backend/app/models/` | SQLAlchemy models: `User`, `Note` |
| **Schemas** | `backend/app/schemas/` | Pydantic models for request/response validation |
| **Dependencies** | `backend/app/api/deps.py` | `get_current_user`, `get_current_active_user`, pagination params |

### Frontend (Flutter) — `frontend/lib/`

| Module | Path | Responsibility |
|--------|------|----------------|
| **App Entry** | `frontend/lib/main.dart` | App initialization, router, theme, provider setup |
| **Routing** | `frontend/lib/core/router/app_router.dart` | GoRouter config: auth guard, routes for login, register, notes list, note detail |
| **API Client** | `frontend/lib/core/network/api_client.dart` | Dio instance with base URL, interceptors for auth header, token refresh |
| **Token Storage** | `frontend/lib/core/storage/token_storage.dart` | Secure storage (flutter_secure_storage) for access/refresh tokens |
| **Auth Repository** | `frontend/lib/features/auth/data/auth_repository.dart` | Calls `/api/auth/*`, returns `AuthResult` (tokens + user) |
| **Auth Service** | `frontend/lib/features/auth/domain/auth_service.dart` | Business logic: login, register, logout, token refresh, auth state stream |
| **Auth Notifier** | `frontend/lib/features/auth/presentation/auth_notifier.dart` | Riverpod `StateNotifier` exposing `AuthState` (unauthenticated, authenticated, loading) |
| **Note Repository** | `frontend/lib/features/notes/data/note_repository.dart` | Calls `/api/notes/*`, maps DTOs to domain models |
| **Note Service** | `frontend/lib/features/notes/domain/note_service.dart` | Business logic: list, create, update, delete, optimistic updates |
| **Notes Notifier** | `frontend/lib/features/notes/presentation/notes_notifier.dart` | Riverpod `StateNotifier` for `AsyncValue<List<Note>>` with pagination |
| **Note Detail Notifier** | `frontend/lib/features/notes/presentation/note_detail_notifier.dart` | Riverpod `StateNotifier` for single note CRUD |
| **Models** | `frontend/lib/features/*/domain/models.dart` | Freezed/JSON-serializable: `User`, `Note`, `AuthTokens` |
| **DTOs** | `frontend/lib/features/*/data/dtos.dart` | Request/response DTOs matching backend schemas |
| **UI Screens** | `frontend/lib/features/*/presentation/screens/` | LoginScreen, RegisterScreen, NotesListScreen, NoteDetailScreen, NoteFormScreen |
| **UI Widgets** | `frontend/lib/features/*/presentation/widgets/` | Reusable: NoteTile, LoadingOverlay, ErrorBanner, AuthTextField |

---

## Data Flow

### Authentication Flow (Login)
```
Flutter UI (LoginScreen)
    → AuthNotifier.login(email, password)
    → AuthService.login(email, password)
    → AuthRepository.login(email, password)  [POST /api/auth/login]
    → FastAPI Auth Router → AuthService.login()
    → UserRepository.get_by_email() → verify password
    → AuthService.create_token_pair(user_id)
    → Returns {access_token, refresh_token, user}
    → AuthRepository stores tokens in TokenStorage
    → AuthService emits AuthState.authenticated(user)
    → AuthNotifier updates state → UI navigates to NotesListScreen
```

### Note List Flow
```
Flutter UI (NotesListScreen)
    → NotesNotifier.loadNotes(page=1)
    → NoteService.listNotes(page, pageSize)
    → NoteRepository.listNotes(page, pageSize)  [GET /api/notes?page=1&size=20]
    → FastAPI Notes Router → NoteService.list_notes(user_id, page, size)
    → NoteRepository.list_by_user(user_id, offset, limit)
    → Returns List[Note] + total count
    → NoteRepository maps DTOs → domain models
    → NotesNotifier updates state with AsyncValue.data(notes)
    → UI renders ListView.builder with NoteTile widgets
```

### Token Refresh Flow (Automatic)
```
API Client (Dio Interceptor) receives 401 on any request
    → Checks if refresh token exists in TokenStorage
    → Calls POST /api/auth/refresh with refresh token
    → FastAPI validates refresh token, issues new access + refresh pair
    → API Client updates TokenStorage with new tokens
    → Retries original request with new access token
    → On refresh failure → clears tokens → emits unauthenticated state
```

---

## Tech Stack

| Layer | Technology | Version Constraint |
|-------|------------|-------------------|
| **Backend Framework** | FastAPI | 0.110+ |
| **Async ORM** | SQLAlchemy | 2.0+ (async) |
| **Database** | PostgreSQL | 15+ (production), SQLite (dev) |
| **Migration** | Alembic | 1.13+ |
| **Validation** | Pydantic | 2.7+ |
| **Auth** | python-jose (JWT), passlib[bcrypt] | Latest |
| **Testing** | pytest, pytest-asyncio, httpx | Latest |
| **Frontend Framework** | Flutter | 3.22+ (Dart 3.4+) |
| **State Management** | Riverpod | 2.5+ (codegen: riverpod_generator) |
| **Routing** | GoRouter | 14.2+ |
| **Networking** | Dio | 5.4+ |
| **Secure Storage** | flutter_secure_storage | 9.2+ |
| **Serialization** | Freezed + json_serializable | Latest |
| **DI/Service Locator** | get_it | 7.6+ |
| **Testing** | flutter_test, mocktail, patrol (e2e) | Latest |

---

## Layering

### Backend Layering (Enforced by Import Rules)

```
app/
├── main.py                    # Composition root
├── core/                      # Cross-cutting concerns
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   └── exceptions.py
├── api/
│   └── v1/                    # HTTP layer only — thin, no business logic
│       ├── health.py
│       ├── auth.py
│       ├── notes.py
│       └── deps.py            # FastAPI dependencies (current_user, pagination)
├── services/                  # Business logic — no HTTP, no DB directly
│   ├── auth_service.py
│   └── note_service.py
├── repositories/              # Data access — SQLAlchemy only
│   ├── user_repository.py
│   └── note_repository.py
├── models/                    # SQLAlchemy ORM models
│   ├── user.py
│   └── note.py
└── schemas/                   # Pydantic request/response models
    ├── auth.py
    ├── note.py
    └── user.py
```

**Import Rules** (enforced by `ruff`/`mypy`):
- `api` → `services`, `schemas`, `deps`
- `services` → `repositories`, `models`, `schemas`, `core/security`
- `repositories` → `models`, `core/database`
- `models` → no internal imports
- `schemas` → no internal imports

### Frontend Layering (Feature-First + Clean Architecture)

```
lib/
├── main.dart
├── core/                      # Shared infrastructure
│   ├── network/api_client.dart
│   ├── storage/token_storage.dart
│   ├── router/app_router.dart
│   ├── di/service_locator.dart      # get_it registration
│   └── utils/extensions.dart
├── features/
│   ├── auth/
│   │   ├── data/
│   │   │   ├── auth_repository.dart
│   │   │   └── dtos.dart
│   │   ├── domain/
│   │   │   ├── models.dart          # User, AuthTokens (Freezed)
│   │   │   ├── auth_service.dart
│   │   │   └── auth_failure.dart    # Freezed sealed class
│   │   └── presentation/
│   │       ├── auth_notifier.dart
│   │       ├── screens/login_screen.dart
│   │       ├── screens/register_screen.dart
│   │       └── widgets/auth_text_field.dart
│   └── notes/
│       ├── data/
│       │   ├── note_repository.dart
│       │   └── dtos.dart
│       ├── domain/
│       │   ├── models.dart          # Note (Freezed)
│       │   ├── note_service.dart
│       │   └── note_failure.dart
│       └── presentation/
│           ├── notes_notifier.dart
│           ├── note_detail_notifier.dart
│           ├── screens/notes_list_screen.dart
│           ├── screens/note_detail_screen.dart
│           ├── screens/note_form_screen.dart
│           └── widgets/note_tile.dart
```

**Dependency Direction** (enforced by `dart_code_metrics`):
- `presentation` → `domain`, `core`
- `domain` → no feature imports (pure Dart)
- `data` → `domain`, `core/network`, `core/storage`
- `core` → no feature imports

---

## Auth & Security

### Backend

- **Password Hashing**: bcrypt via `passlib`, cost factor 12
- **JWT**: RS256 asymmetric keys (production) / HS256 (dev)
  - Access token: 15 min TTL, `sub=user_id`, `type=access`
  - Refresh token: 30 days TTL, `sub=user_id`, `type=refresh`, stored hashed in DB
- **Refresh Token Rotation**: On refresh, old refresh token revoked, new pair issued
- **Token Revocation**: `revoked_at` timestamp on `RefreshToken` model; checked on every refresh
- **CORS**: Configured via `config.CORS_ORIGINS` (explicit list, no wildcard in prod)
- **Rate Limiting**: `slowapi` on `/api/auth/*` — 5 req/min per IP
- **Security Headers**: `SecureHeadersMiddleware` (CSP, HSTS, X-Frame-Options, Referrer-Policy)
- **Dependency**: `get_current_user` extracts `sub` from validated access token, loads `User` from DB, raises 401 if missing/inactive

### Frontend

- **Token Storage**: `flutter_secure_storage` with platform-specific secure enclave/Keystore
  - Keys: `access_token`, `refresh_token`
- **Automatic Refresh**: Dio interceptor catches 401, calls refresh endpoint once, retries original request
- **Auth State**: `AuthNotifier` exposes `Stream<AuthState>` via Riverpod `StateNotifierProvider`
- **Route Guard**: GoRouter `redirect` checks `AuthState`; unauthenticated → `/login`, authenticated → `/notes`
- **Logout**: Clears secure storage, revokes refresh token via `POST /api/auth/logout` (best-effort), emits `AuthState.unauthenticated`

---

## Data Model

### Backend (SQLAlchemy Models)

```python
# backend/app/models/user.py
class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# backend/app/models/note.py
class Note(Base):
    __tablename__ = "notes"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# backend/app/models/refresh_token.py
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

### Frontend (Freezed Models)

```dart
// frontend/lib/features/auth/domain/models.dart
@freezed
class User with _$User {
  const factory User({
    required String id,
    required String email,
    required DateTime createdAt,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

@freezed
class AuthTokens with _$AuthTokens {
  const factory AuthTokens({
    required String accessToken,
    required String refreshToken,
  }) = _AuthTokens;

  factory AuthTokens.fromJson(Map<String, dynamic> json) => _$AuthTokensFromJson(json);
}

// frontend/lib/features/notes/domain/models.dart
@freezed
class Note with _$Note {
  const factory Note({
    required String id,
    required String userId,
    required String title,
    required String content,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _Note;

  factory Note.fromJson(Map<String, dynamic> json) => _$NoteFromJson(json);
}
```

### API Schemas (Pydantic)

```python
# backend/app/schemas/auth.py
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

# backend/app/schemas/note.py
class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(default="", max_length=50000)

class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, max_length=50000)

class NoteResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NoteListResponse(BaseModel):
    items: list[NoteResponse]
    total: int
    page: int
    size: int
```

---

## Error Handling

### Backend

- **Exception Hierarchy** (`backend/app/core/exceptions.py`):
  ```python
  class AppException(Exception):
      status_code: int = 500
      detail: str = "Internal server error"

  class NotFoundError(AppException):
      status_code = 404
      detail = "Resource not found"

  class ConflictError(AppException):
      status_code = 409
      detail = "Resource already exists"

  class UnauthorizedError(AppException):
      status_code = 401
      detail = "Invalid credentials"

  class ForbiddenError(AppException):
      status_code = 403
      detail = "Access denied"

  class ValidationError(AppException):
      status_code = 422
      detail = "Validation failed"
  ```
- **Global Handlers** in `main.py`: map `AppException` → JSON `{detail, code}`, `RequestValidationError` → 422 with field errors, `SQLAlchemyError` → 500 (logged, generic message)
- **Service Layer**: Raises typed exceptions; routers don't catch — global handlers do

### Frontend

- **Failure Types** (Freezed sealed classes):
  ```dart
  // auth_failure.dart
  @freezed
  class AuthFailure with _$AuthFailure {
    const factory AuthFailure.invalidCredentials() = _InvalidCredentials;
    const factory AuthFailure.emailAlreadyExists() = _EmailAlreadyExists;
    const factory AuthFailure.networkError(String message) = _NetworkError;
    const factory AuthFailure.tokenExpired() = _TokenExpired;
    const factory AuthFailure.unknown(String message) = _Unknown;
  }

  // note_failure.dart
  @freezed
  class NoteFailure