"""
Authentication service.

Handles user login, registration, and password management
with bcrypt hashing for secure credential storage.
"""

import bcrypt

from app.models.user import UserModel


class AuthService:
    """Business logic for authentication and user management."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain‑text password using bcrypt.

        Args:
            password: The plain‑text password.

        Returns:
            The bcrypt hash as a UTF‑8 string.
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Check a plain‑text password against a stored hash.

        Args:
            password:      Plain‑text password to verify.
            password_hash: The stored bcrypt hash.

        Returns:
            ``True`` if the password matches.
        """
        return bcrypt.checkpw(
            password.encode("utf-8"), password_hash.encode("utf-8")
        )

    @classmethod
    def login(cls, username: str, password: str) -> dict | None:
        """
        Authenticate a user by username and password.

        Args:
            username: Login username.
            password: Plain‑text password.

        Returns:
            User dict on success, ``None`` on failure.

        Raises:
            ValueError: If username or password is empty.
        """
        if not username or not password:
            raise ValueError("Username and password are required.")

        user = UserModel.get_by_username(username)
        if user is None:
            return None

        if cls.verify_password(password, user["password_hash"]):
            return user
        return None

    @classmethod
    def register_user(cls, username: str, password: str,
                      role: str = "librarian") -> int:
        """
        Register a new user with a hashed password.

        Args:
            username: Unique username.
            password: Plain‑text password (will be hashed).
            role:     ``'admin'`` or ``'librarian'``.

        Returns:
            The new user's id.

        Raises:
            ValueError: If fields are empty or username already exists.
        """
        if not username or not password:
            raise ValueError("Username and password are required.")

        if UserModel.get_by_username(username):
            raise ValueError(f"Username '{username}' already exists.")

        password_hash = cls.hash_password(password)
        return UserModel.create(username, password_hash, role)

    @classmethod
    def change_password(cls, user_id: int, old_password: str,
                        new_password: str) -> bool:
        """
        Change a user's password after verifying the old one.

        Args:
            user_id:      The user's primary key.
            old_password: Current plain‑text password.
            new_password: New plain‑text password.

        Returns:
            ``True`` if the password was changed successfully.

        Raises:
            ValueError: If the old password is incorrect or new password empty.
        """
        user = UserModel.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found.")

        if not cls.verify_password(old_password, user["password_hash"]):
            raise ValueError("Current password is incorrect.")

        if not new_password:
            raise ValueError("New password cannot be empty.")

        new_hash = cls.hash_password(new_password)
        UserModel.update(user_id, password_hash=new_hash)
        return True
