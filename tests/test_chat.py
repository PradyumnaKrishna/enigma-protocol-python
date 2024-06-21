import time
import unittest

from fastapi.testclient import TestClient

from app import app


class TestChat(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        # login for user 1
        response = self.client.get("/login/123")
        self.assertEqual(response.status_code, 200)
        self.user1 = response.json()["user"]

        # login for user 2
        response = self.client.get("/login/456")
        self.assertEqual(response.status_code, 200)
        self.user2 = response.json()["user"]

    def test_connect_invalid_user(self):
        with self.client.websocket_connect("/connect/invalid") as websocket:
            data = websocket.receive_json()
            self.assertEqual(data, {"error": "User not found"})

    def test_send_to_invalid_user(self):
        with self.client.websocket_connect(f"/connect/{self.user1}") as ws1:
            ws1.send_json(
                {"from": self.user1, "to": "invalid", "payload": "Hello User"}
            )
            data = ws1.receive_json()
            self.assertEqual(data, {"error": "User not found"})

    def test_sync_communication(self):
        # connect user1
        with self.client.websocket_connect(f"/connect/{self.user1}") as ws1:
            data = {"from": self.user1, "to": self.user2, "payload": "Hello User"}
            ws1.send_json(data)

        with self.client.websocket_connect(f"/connect/{self.user2}") as ws2:
            data = ws2.receive_json()
            self.assertEqual(data, data)

            data = {
                "from": self.user2,
                "to": self.user1,
                "payload": "Hello Another User",
            }
            ws2.send_json(data)

        with self.client.websocket_connect(f"/connect/{self.user1}") as ws1:
            data = ws1.receive_json()
            self.assertEqual(data, data)

    def test_async_communication(self):
        with self.client.websocket_connect(f"/connect/{self.user1}") as ws1:
            with self.client.websocket_connect(f"/connect/{self.user2}") as ws2:
                data = {"from": self.user1, "to": self.user2, "payload": "Hello User"}
                ws1.send_json(data)

                data = ws2.receive_json()
                self.assertEqual(data, data)

                data = {
                    "from": self.user2,
                    "to": self.user1,
                    "payload": "Hello Another User",
                }
                ws2.send_json(data)

                data = ws1.receive_json()
                self.assertEqual(data, data)

    def test_pending_messages(self):
        with self.client.websocket_connect(f"/connect/{self.user1}") as ws1:
            data = {"from": self.user1, "to": self.user2, "payload": "Hello User"}
            ws1.send_json(data)

            # Race Condition
            time.sleep(0.1)

            with self.client.websocket_connect(f"/connect/{self.user2}") as ws2:
                data = ws2.receive_json()
                self.assertEqual(data, data)

                data = {
                    "from": self.user2,
                    "to": self.user1,
                    "payload": "Hello Another User",
                }
                ws2.send_json(data)

            data = ws1.receive_json()
            self.assertEqual(data, data)

            data = {
                "from": self.user1,
                "to": self.user2,
                "payload": f"Hello User {self.user2}",
            }
            ws1.send_json(data)

        with self.client.websocket_connect(f"/connect/{self.user2}") as ws2:
            data = ws2.receive_json()
            self.assertEqual(data, data)

    def test_send_invaid_data(self):
        with self.client.websocket_connect(f"/connect/{self.user1}") as ws1:
            ws1.send_text("invalid")
            data = ws1.receive_json()
            self.assertEqual(data, {"error": "Invalid data"})


if __name__ == "__main__":
    unittest.main()
