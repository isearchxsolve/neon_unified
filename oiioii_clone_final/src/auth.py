"""
Authentication service for the AI Animation Agent Platform.

Provides user registration, login, token-based session management,
and password hashing.
"""

import hashlib
import secrets
from typing import Optional, Dict

from src.models import User
from src.storage import users_store, sessions_store


class AuthError(Exception):
    """Authentication error."""
    pass


class AuthService:
    """Authentication service."""

    def __init__(self):
        self._users = users_store
        self._sessions = sessions_store

    def register(self, username: str, email: str, password: str) -> User:
        """Register a new user with a hashed password."""
        if not username or not email or not password:
            raise AuthError("username, email, and password are required")
        existing = self._users.filter(
            lambda u: u.username == username
        )
        if existing:
            raise AuthError(f"username '{username}' is already taken")
        user = User(username=username, email=email)
        self._users.add(user.id, user)
        self._store_password(user.id, password)
        return user

    def login(self, username: str, password: str) -> str:
        """Authenticate and return a session token."""
        matches = self._users.filter(lambda u: u.username == username)
        if not matches:
            raise AuthError("invalid credentials")
        user = matches[0]
        if not user.is_active:
            raise AuthError("user is inactive")
        if not self._verify_password(user.id, password):
            raise AuthError("invalid credentials")
        token = self._generate_token()
        self._sessions.add(token, user.id)
        return token

    def verify_token(self, token: str) -> Optional[User]:
        """Return the user associated with the token, or None if invalid."""
        user_id = self._sessions.get(token)
        if not user_id:
            return None
        return self._users.get(user_id)

    def logout(self, token: str) -> None:
        """Invalidate the given token."""
        self._sessions.delete(token)

    def _generate_token(self) -> str:
        """Generate a random session token."""
        return secrets.token_urlsafe(32)

    def _store_password(self, user_id: str, password: str) -> None:
        """Store a salted hash of the password."""
        salt = secrets.token_hex(16)
        pw_hash = self._hash_password(password, salt)
        self._sessions.add(f"pwd:{user_id}", f"{salt}${pw_hash}")

    def _verify_password(self, user_id: str, password: str) -> bool:
        """Verify a password against the stored hash."""
        stored = self._sessions.get(f"pwd:{user_id}")
        if not stored:
            return False
        salt, pw_hash = stored.split("$", 1)
        return self._hash_password(password, salt) == pw_hash

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Hash a password with the given salt using SHA-256."""
        return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
