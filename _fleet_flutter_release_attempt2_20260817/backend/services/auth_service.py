from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
from jose import JWTError, jwt

# Exceptions


class AuthError(Exception):
    """Raised on any authentication/authorization failure."""

    def __init__(self, message: str = "authentication failed", status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


# User model -- intentionally minimal so the service stays storage-agnostic.
# Swap _store for a real repository when wiring a DB.


class User:
    __slots__ = ("id", "email", "password_hash", "created_at", "is_active")

    def __init__(
        self,
        email: str,
        password_hash: bytes,
        user_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        is_active: bool = True,
    ):
        self.id = user_id or str(uuid.uuid4())
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now(timezone.utc)
        self.is_active = is_active

    def to_public_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
        }


class AuthService:
    """Registration + login with bcrypt-hashed passwords and JWT issuance."""

    _ALGORITHM = "HS256"

    def __init__(
        self,
        secret_key: Optional[str] = None,
        token_expire_minutes: int = 60,
        issuer: str = "auth-service",
    ):
        self._secret_key = secret_key or os.environ.get("AUTH_SECRET_KEY")
        if not self._secret_key:
            # Refuse to operate without a signing key rather than silently
            # producing tokens signed with an empty/default secret.
            raise RuntimeError(
                "AUTH_SECRET_KEY must be provided via constructor or env var"
            )
        if token_expire_minutes <= 0:
            raise ValueError("token_expire_minutes must be positive")

        self._token_expire_minutes = token_expire_minutes
        self._issuer = issuer
        # { email -> User }; replace with a repository in production.
        self._store: Dict[str, User] = {}

    # ---- public API ---------------------------------------------------

    def register(self, email: str, password: str) -> Dict[str, Any]:
        email = self._normalize_email(email)
        self._validate_email(email)
        self._validate_password(password)

        if email in self._store:
            raise AuthError("email already registered", status_code=409)

        password_hash = self._hash_password(password)
        user = User(email=email, password_hash=password_hash)
        self._store[email] = user

        token = self._create_access_token(user)
        return {"user": user.to_public_dict(), "token": token}

    def login(self, email: str, password: str) -> Dict[str, Any]:
        email = self._normalize_email(email)
        user = self._store.get(email)
        if user is None or not user.is_active:
            raise AuthError("invalid credentials", status_code=401)

        if not self._verify_password(password, user.password_hash):
            raise AuthError("invalid credentials", status_code=401)

        token = self._create_access_token(user)
        return {"user": user.to_public_dict(), "token": token}

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT and return its claims. Raises AuthError on failure."""
        if not token:
            raise AuthError("missing token", status_code=401)
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._ALGORITHM],
                issuer=self._issuer,
                options={"require": ["exp", "iat", "sub", "iss"]},
            )
        except JWTError as exc:
            raise AuthError(f"invalid token: {exc}", status_code=401) from exc
        return payload

    # ---- helpers ------------------------------------------------------

    @staticmethod
    def _normalize_email(email: str) -> str:
        if not isinstance(email, str):
            raise AuthError("email must be a string", status_code=400)
        return email.strip().lower()

    @staticmethod
    def _validate_email(email: str) -> None:
        if not email or "@" not in email or len(email) > 254:
            raise AuthError("invalid email", status_code=400)
        local, _, domain = email.partition("@")
        if not local or not domain or "." not in domain:
            raise AuthError("invalid email", status_code=400)

    @staticmethod
    def _validate_password(password: str) -> None:
        if not isinstance(password, str) or not password:
            raise AuthError("password is required", status_code=400)
        if len(password) < 8:
            raise AuthError("password must be at least 8 characters", status_code=400)
        if len(password) > 1024:
            raise AuthError("password too long", status_code=400)

    @staticmethod
    def _hash_password(password: str) -> bytes:
        # 12 rounds is a reasonable default for interactive auth on modern
        # hardware; bump higher if your hardware budget allows.
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))

    @staticmethod
    def _verify_password(password: str, password_hash: bytes) -> bool:
        if not password_hash:
            return False
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash)
        except (ValueError, TypeError):
            return False

    def _create_access_token(self, user: User) -> str:
        now = datetime.now(timezone.utc)
        payload: Dict[str, Any] = {
            "iss": self._issuer,
            "sub": user.id,
            "email": user.email,
            "iat": int(now.timestamp()),
            "exp": int(
                (now + timedelta(minutes=self._token_expire_minutes)).timestamp()
            ),
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._ALGORITHM)