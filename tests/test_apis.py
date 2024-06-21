"""
Tests for Flask APIs
"""

import unittest

from fastapi.testclient import TestClient

from app import app


class TestAPI(unittest.TestCase):
    """
    Test Flask APIs
    """

    def setUp(self):
        self.client = TestClient(app)

    def test_home(self):
        """
        Test homepage
        """
        response = self.client.get("/")
        self.assertEqual(200, response.status_code)

    def test_new(self):
        """
        Test new user creation
        """
        public_key = "random-public-key"
        response = self.client.get(f"/login/{public_key}")
        self.assertEqual(200, response.status_code)

        user_id = response.json()["user"]
        response = self.client.get(f"/connect/{user_id}")
        self.assertEqual(200, response.status_code)
        self.assertEqual(public_key, response.json()["publicKey"])

    def test_not_found(self):
        """
        Test user not found
        """
        user_id = "wrong-id"
        response = self.client.get(f"/connet/{user_id}")
        self.assertEqual(404, response.status_code)


if __name__ == "__main__":
    unittest.main()
