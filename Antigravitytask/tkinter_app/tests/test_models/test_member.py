"""Unit tests for MemberModel (mocked DB)."""

import unittest
from unittest.mock import patch

from app.models.member import MemberModel


class TestMemberModel(unittest.TestCase):

    @patch("app.models.member.db")
    def test_create(self, mock_db):
        mock_db.execute_query.return_value = 1
        mid = MemberModel.create("Ali", "a@b.com", "123", "Addr")
        self.assertEqual(mid, 1)

    @patch("app.models.member.db")
    def test_get_by_id(self, mock_db):
        mock_db.execute_read_one.return_value = {"id": 1, "name": "Ali"}
        self.assertIsNotNone(MemberModel.get_by_id(1))

    @patch("app.models.member.db")
    def test_get_all(self, mock_db):
        mock_db.execute_read.return_value = [{"id": 1}]
        self.assertEqual(len(MemberModel.get_all()), 1)

    @patch("app.models.member.db")
    def test_search(self, mock_db):
        mock_db.execute_read.return_value = [{"id": 1}]
        self.assertEqual(len(MemberModel.search("Ali")), 1)

    @patch("app.models.member.db")
    def test_update(self, mock_db):
        MemberModel.update(1, name="New")
        mock_db.execute_query.assert_called_once()

    @patch("app.models.member.db")
    def test_deactivate(self, mock_db):
        MemberModel.deactivate(1)
        mock_db.execute_query.assert_called_once()

    @patch("app.models.member.db")
    def test_delete(self, mock_db):
        MemberModel.delete(1)
        mock_db.execute_query.assert_called_once()


if __name__ == "__main__":
    unittest.main()
