import hashlib
import hmac
import os
import time
import secrets
import binascii
from typing import Optional, Dict, Tuple

# Simple in-memory user store for demonstration. 
# In a real app, use a proper database (PostgreSQL, SQLite, etc.) via SQLAlchemy/Tortoise ORM.
_user_db: Dict[str, Dict[str, str]] = {}

def _hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """Securely hashes a password using PBKDF2 HMAC SHA-256."""
    if salt is None:
        salt = os.urandom(16)
    iterations = 100_000
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return key, salt

def _verify_password(password: str, salt: bytes, expected_key: bytes) -> bool:
    """Verifies a password against a salt and expected key using constant-time comparison."""
    derived_key, _ = _hash_password(password, salt)
    return hmac.compare_digest(derived_key, expected_key)

def _generate_session_token() -> str:
    """Generates a cryptographically secure random session token."""
    return secrets.token_urlsafe(32)

class AuthManager:
    """Handles user authentication, registration, and session management."""
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, any]] = {}

    def register_user(self, email: str, password: str) -> bool:
        """Registers a new user"""
        email = email.lower().strip()
        if not email or not password:
            return False
        if len(password) < 8:
            return False
        if email in _user_db:
            return False
            
        key, salt = _hash_password(password)
        _user_db[email] = {
            "user_id": str(secrets.uuid4) if hasattr(secrets, 'uuid4') else binascii.hexlify(os.urandom(16)).decode(),
            "password_key": binascii.hexlify(key).decode('utf-8'),
            "salt": binascii.hexlify(salt).decode('utf-8'),
            "created_at": int(time.time())
        }
        return True

    def login_user(self, email: str, password: str) -> Optional[str]:
        """Logs in a user and returns a session token, or None if failed."""
        email = email.lower().strip()
        user = _user_db.get(email)
        
        if not user:
            return None
            
        salt = binascii.unhexlify(user["salt"].encode('utf-8'))
        expected_key = binascii.unhexlify(user["password_key"].encode('utf-8'))
        
        if not _verify_password(password, salt, expected_key):
            return None
            
        token = _generate_session_token()
        self._sessions[token] = {
            "user_id": user["user_id"],
            "email": email,
            "expires_at": time.time() + 86400 # 24 hours
        }
        return token

    def verify_session(self, token: str) -> Optional[Dict[str, any]]:
        """Verifies a session token and returns the session data if valid, else None."""
        if not token:
            return None
            
        session = self._sessions.get(token)
        if not session:
            return None
            
        if time.time() > session["expires_at"]:
            self.logout_user(token)
            return None
            
        return session

    def get_user_id(self, token: str) -> Optional[str]:
        """Retrieves the user_id associated with a valid session token."""
        session = self.verify_session(token)
        if session:
            return session["user_id"]
        return None

    def logout_user(self, token: str) -> bool:
        """Logs out a user by deleting their session token."""
        if token in self._sessions:
            del self._sessions[token]
            return True
        return False

    def change_password(self, email: str, old_password: str, new_password: str) -> bool:
        """Changes a user's password."""
        email = email.lower().strip()
        user = _user_db.get(email)
        if not user or len(new_password) < 8:
            return False
            
        salt = binascii.unhexlify(user["salt"].encode('utf-8'))
        expected_key = binascii.unhexlify(user["password_key"].encode('utf-8'))
        
        if not _verify_password(old_password, salt, expected_key):
            return False
            
        new_key, new_salt = _hash_password(new_password)
        user["password_key"] = binascii.hexlify(new_key).decode('utf-8')
        user["salt"] = binascii.hexlify(new_salt).decode('utf-8')
        return True

# Singleton instance for app-level usage
auth_manager = AuthManager()