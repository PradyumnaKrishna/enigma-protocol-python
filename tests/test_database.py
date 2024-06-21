"""
Tests database module
"""

import os
import tempfile
import unittest

from app.database import DataBase


class TestDataBase(unittest.TestCase):
    """
    Test DataBase Class that runs SQLite query
    """

    def setUp(self):
        self.file = tempfile.NamedTemporaryFile(delete=False)
        self.database = DataBase(self.file.name, "test_table")

    def test_save_user(self):
        """
        Test insertion and selection query
        """
        public_key = "random-public-key"
        user_id = self.database.save_user(public_key)
        self.assertEqual(public_key, self.database.get_public_key(user_id))

    def test_is_exist(self):
        """
        Test user existence
        """
        self.assertFalse(self.database.is_exist("random-id"))

        public_key = "random-key"
        user_id = self.database.save_user(public_key)
        self.assertTrue(self.database.is_exist(user_id))

    def tearDown(self):
        self.file.close()
        os.unlink(self.file.name)
