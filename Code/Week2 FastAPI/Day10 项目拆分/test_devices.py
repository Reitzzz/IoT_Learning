import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class DeviceRoutesTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_device_routes(self):
        self.assertEqual(self.client.get("/devices").status_code, 200)
        self.assertEqual(self.client.get("/devices/001").json()["device_id"], "001")
        self.assertEqual(
            self.client.post("/devices/999/command", json={"command": "STOP"}).status_code,
            404,
        )
        self.assertEqual(
            self.client.post("/devices/001/command", json={"command": "RESET"}).status_code,
            400,
        )

        with patch("app.services.device_service.publish_command"):
            response = self.client.post(
                "/devices/001/command",
                json={"command": "STOP"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "命令已发送")


if __name__ == "__main__":
    unittest.main()
