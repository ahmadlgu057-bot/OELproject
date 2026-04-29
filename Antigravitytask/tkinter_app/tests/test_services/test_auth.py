"""
Unit tests for the AuthService.

Tests login, registration, password hashing, and password change
logic using mocked database calls.
"""

import unittest
from unittest.mock import patch, MagicMock

from app.services.auth import AuthService


class TestAuthService(unittest.TestCase):
    """Test suite for AuthService."""

    # ── Password hashing ────────────────────────────────────────────────

    def test_hash_password_returns_string(self):
        """hash_password should return a non‑empty string."""
        hashed = AuthService.hash_password("test123")
        self.assertIsInstance(hashed, str)
        self.assertTrue(len(hashed) > 0)

    def test_hash_password_differs_from_plain(self):
        """The hash must not equal the plain‑text input."""
        plain = "mypassword"
        hashed = AuthService.hash_password(plain)
        self.assertNotEqual(plain, hashed)

    def test_verify_password_correct(self):
        """verify_password should return True for matching password."""
        plain = "secret123"
        hashed = AuthService.hash_password(plain)
        self.assertTrue(AuthService.verify_password(plain, hashed))

    def test_verify_password_incorrect(self):
        """verify_password should return False for wrong password."""
        hashed = AuthService.hash_password("correct_password")
        self.assertFalse(AuthService.verify_password("wrong_password", hashed))

    # ── Login ───────────────────────────────────────────────────────────

    @patch("app.services.auth.UserModel")
    def test_login_success(self, mock_user_model):
        """login should return user dict when credentials match."""
        password = "admin123"
        hashed = AuthService.hash_password(password)
        mock_user_model.get_by_username.return_value = {
            "id": 1,
            "username": "ghazanfar",
            "password_hash": hashed,
            "role": "admin",
        }

        result = AuthService.login("ghazanfar", password)
        self.assertIsNotNone(result)
        self.assertEqual(result["username"], "ghazanfar")

    @patch("app.services.auth.UserModel")
    def test_login_wrong_password(self, mock_user_model):
        """login should return None for incorrect password."""
        hashed = AuthService.hash_password("correct")
        mock_user_model.get_by_username.return_value = {
            "id": 1,
            "username": "user1",
            "password_hash": hashed,
            "role": "librarian",
        }

        result = AuthService.login("user1", "wrong")
        self.assertIsNone(result)

    @patch("app.services.auth.UserModel")
    def test_login_user_not_found(self, mock_user_model):
        """login should return None when username doesn't exist."""
        mock_user_model.get_by_username.return_value = None
        result = AuthService.login("nonexistent", "pass")
        self.assertIsNone(result)

    def test_login_empty_fields(self):
        """login should raise ValueError for empty credentials."""
        with self.assertRaises(ValueError):
            AuthService.login("", "password")
        with self.assertRaises(ValueError):
            AuthService.login("user", "")

    # ── Registration ────────────────────────────────────────────────────

    @patch("app.services.auth.UserModel")
    def test_register_user_success(self, mock_user_model):
        """register_user should create a new user and return the id."""
        mock_user_model.get_by_username.return_value = None
        mock_user_model.create.return_value = 5

        user_id = AuthService.register_user("newuser", "pass123", "librarian")
        self.assertEqual(user_id, 5)
        mock_user_model.create.assert_called_once()

    @patch("app.services.auth.UserModel")
    def test_register_duplicate_username(self, mock_user_model):
        """register_user should raise ValueError for duplicate username."""
        mock_user_model.get_by_username.return_value = {"id": 1}

        with self.assertRaises(ValueError):
            AuthService.register_user("existing", "pass123")

    def test_register_empty_fields(self):
        """register_user should raise ValueError for empty inputs."""
        with self.assertRaises(ValueError):
            AuthService.register_user("", "pass")
        with self.assertRaises(ValueError):
            AuthService.register_user("user", "")

    # ── Change password ─────────────────────────────────────────────────

    @patch("app.services.auth.UserModel")
    def test_change_password_success(self, mock_user_model):
        """change_password should update hash when old password is correct."""
        old_pass = "oldpass"
        hashed = AuthService.hash_password(old_pass)
        mock_user_model.get_by_id.return_value = {
            "id": 1,
            "password_hash": hashed,
        }

        result = AuthService.change_password(1, old_pass, "newpass")
        self.assertTrue(result)
        mock_user_model.update.assert_called_once()

    @patch("app.services.auth.UserModel")
    def test_change_password_wrong_old(self, mock_user_model):
        """change_password should raise ValueError for wrong old password."""
        hashed = AuthService.hash_password("correct")
        mock_user_model.get_by_id.return_value = {
            "id": 1,
            "password_hash": hashed,
        }

        with self.assertRaises(ValueError):
            AuthService.change_password(1, "wrong", "newpass")


if __name__ == "__main__":
    unittest.main()
