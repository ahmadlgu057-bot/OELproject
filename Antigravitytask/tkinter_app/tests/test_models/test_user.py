"""Unit tests for UserModel (mocked DB)."""

import unittest
from unittest.mock import patch

from app.models.user import UserModel


class TestUserModel(unittest.TestCase):

    @patch("app.models.user.db")
    def test_create(self, mock_db):
        mock_db.execute_query.return_value = 1
        uid = UserModel.create("testuser", "hash123", "admin")
        self.assertEqual(uid, 1)
        mock_db.execute_query.assert_called_once()

    @patch("app.models.user.db")
    def test_get_by_id(self, mock_db):
        mock_db.execute_read_one.return_value = {"id": 1, "username": "u"}
        user = UserModel.get_by_id(1)
        self.assertEqual(user["username"], "u")

    @patch("app.models.user.db")
    def test_get_by_username(self, mock_db):
        mock_db.execute_read_one.return_value = {"id": 1, "username": "admin"}
        user = UserModel.get_by_username("admin")
        self.assertIsNotNone(user)

    @patch("app.models.user.db")
    def test_get_all(self, mock_db):
        mock_db.execute_read.return_value = [{"id": 1}, {"id": 2}]
        self.assertEqual(len(UserModel.get_all()), 2)

    @patch("app.models.user.db")
    def test_update(self, mock_db):
        UserModel.update(1, username="new")
        mock_db.execute_query.assert_called_once()

    @patch("app.models.user.db")
    def test_update_no_fields(self, mock_db):
        UserModel.update(1)
        mock_db.execute_query.assert_not_called()

    @patch("app.models.user.db")
    def test_delete(self, mock_db):
        UserModel.delete(1)
        mock_db.execute_query.assert_called_once()


if __name__ == "__main__":
    unittest.main()
