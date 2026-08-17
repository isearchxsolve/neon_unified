"""
Tests for authentication service.
"""

import pytest
from src.auth import AuthService, AuthError


class TestAuthService:
    """Test the AuthService class."""

    def setup_method(self):
        """Reset auth state before each test."""
        from src.storage import users_store, sessions_store
        users_store.clear()
        sessions_store.clear()
        self.auth = AuthService()

    def test_register_user_creates_user_with_username(self):
        """User registration creates a user with the given username."""
        user = self.auth.register("alice", "alice@example.com", "secret123")
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.is_active is True

    def test_register_user_generates_unique_id(self):
        """Each registered user gets a unique ID."""
        u1 = self.auth.register("alice", "alice@example.com", "secret123")
        u2 = self.auth.register("bob", "bob@example.com", "secret456")
        assert u1.id != u2.id

    def test_register_duplicate_username_raises_error(self):
        """Registering a duplicate username raises AuthError."""
        self.auth.register("alice", "alice@example.com", "secret123")
        with pytest.raises(AuthError):
            self.auth.register("alice", "alice2@example.com", "secret123")

    def test_login_valid_credentials_returns_token(self):
        """Login with valid credentials returns a session token."""
        self.auth.register("alice", "alice@example.com", "secret123")
        token = self.auth.login("alice", "secret123")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_login_wrong_password_raises_error(self):
        """Login with wrong password raises AuthError."""
        self.auth.register("alice", "alice@example.com", "secret123")
        with pytest.raises(AuthError):
            self.auth.login("alice", "wrongpassword")

    def test_login_unknown_user_raises_error(self):
        """Login with unknown user raises AuthError."""
        with pytest.raises(AuthError):
            self.auth.login("nobody", "secret123")

    def test_verify_token_returns_user(self):
        """verify_token returns the user for a valid token."""
        self.auth.register("alice", "alice@example.com", "secret123")
        token = self.auth.login("alice", "secret123")
        user = self.auth.verify_token(token)
        assert user is not None
        assert user.username == "alice"

    def test_verify_token_invalid_returns_none(self):
        """verify_token returns None for an invalid token."""
        result = self.auth.verify_token("invalid-token")
        assert result is None

    def test_logout_invalidates_token(self):
        """Logout invalidates the session token."""
        self.auth.register("alice", "alice@example.com", "secret123")
        token = self.auth.login("alice", "secret123")
        self.auth.logout(token)
        assert self.auth.verify_token(token) is None

    def test_password_is_hashed_not_stored_plaintext(self):
        """Password should not be stored in plaintext."""
        user = self.auth.register("alice", "alice@example.com", "secret123")
        # User object should not contain plaintext password
        user_dict = user.to_dict()
        assert "password" not in user_dict
        assert "secret123" not in str(user_dict)
