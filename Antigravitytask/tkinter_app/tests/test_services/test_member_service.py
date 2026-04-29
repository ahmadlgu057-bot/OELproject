"""
Unit tests for MemberService.

Tests registration, update, deactivation, and search with mocked models.
"""

import unittest
from unittest.mock import patch

from app.services.member_service import MemberService


class TestMemberService(unittest.TestCase):
    """Test suite for MemberService."""

    # ── Register ────────────────────────────────────────────────────────

    @patch("app.services.member_service.MemberModel")
    def test_register_member_success(self, mock_model):
        """register_member should create a member and return id."""
        mock_model.create.return_value = 7
        member_id = MemberService.register_member(
            "Ali Khan", "ali@example.com", "+923001234567", "Lahore")
        self.assertEqual(member_id, 7)
        mock_model.create.assert_called_once()

    def test_register_missing_name(self):
        """register_member should raise ValueError for empty name."""
        with self.assertRaises(ValueError) as ctx:
            MemberService.register_member("", "email@test.com")
        self.assertIn("Name", str(ctx.exception))

    def test_register_missing_email(self):
        """register_member should raise ValueError for empty email."""
        with self.assertRaises(ValueError) as ctx:
            MemberService.register_member("Name", "")
        self.assertIn("Email", str(ctx.exception))

    def test_register_invalid_email(self):
        """register_member should reject badly formatted emails."""
        with self.assertRaises(ValueError) as ctx:
            MemberService.register_member("Name", "not-an-email")
        self.assertIn("email", str(ctx.exception).lower())

    def test_register_invalid_phone(self):
        """register_member should reject invalid phone numbers."""
        with self.assertRaises(ValueError) as ctx:
            MemberService.register_member("Name", "a@b.com", "123")
        self.assertIn("phone", str(ctx.exception).lower())

    # ── Update ──────────────────────────────────────────────────────────

    @patch("app.services.member_service.MemberModel")
    def test_update_member_success(self, mock_model):
        """update_member should call model update for existing member."""
        mock_model.get_by_id.return_value = {"id": 1, "name": "Old"}
        MemberService.update_member(1, name="New Name")
        mock_model.update.assert_called_once_with(1, name="New Name")

    @patch("app.services.member_service.MemberModel")
    def test_update_member_not_found(self, mock_model):
        """update_member should raise ValueError for nonexistent member."""
        mock_model.get_by_id.return_value = None
        with self.assertRaises(ValueError):
            MemberService.update_member(999, name="X")

    @patch("app.services.member_service.MemberModel")
    def test_update_member_invalid_email(self, mock_model):
        """update_member should reject invalid email on update."""
        mock_model.get_by_id.return_value = {"id": 1}
        with self.assertRaises(ValueError):
            MemberService.update_member(1, email="bad")

    # ── Deactivate ──────────────────────────────────────────────────────

    @patch("app.services.member_service.MemberModel")
    def test_deactivate_success(self, mock_model):
        """deactivate_member should call model deactivate."""
        mock_model.get_by_id.return_value = {"id": 1, "is_active": True}
        MemberService.deactivate_member(1)
        mock_model.deactivate.assert_called_once_with(1)

    @patch("app.services.member_service.MemberModel")
    def test_deactivate_not_found(self, mock_model):
        """deactivate_member should raise ValueError for unknown member."""
        mock_model.get_by_id.return_value = None
        with self.assertRaises(ValueError):
            MemberService.deactivate_member(999)

    # ── Search ──────────────────────────────────────────────────────────

    @patch("app.services.member_service.MemberModel")
    def test_search_with_keyword(self, mock_model):
        """search_members should filter by keyword."""
        mock_model.search.return_value = [{"id": 1, "name": "Ali"}]
        results = MemberService.search_members("Ali")
        self.assertEqual(len(results), 1)

    @patch("app.services.member_service.MemberModel")
    def test_search_empty_returns_all(self, mock_model):
        """search_members with empty query returns all."""
        mock_model.get_all.return_value = [{"id": 1}, {"id": 2}]
        results = MemberService.search_members("")
        self.assertEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main()
