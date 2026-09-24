from app.config import DEVICE_ID
from app.mqtt.publisher import publish_command

devices = {
    DEVICE_ID: {
        "device_id": DEVICE_ID,
        "temperature": 36.5,
        "rpm": 1500,
        "status": "RUNNING",
        "last_seen": None,
    }
}

SUPPORTED_COMMANDS = {"STOP"}


def list_devices():
    return list(devices.values())


def get_device(device_id: str):
    return devices.get(device_id)


def command_is_supported(command: str) -> bool:
    return command in SUPPORTED_COMMANDS


def send_command(command: str) -> None:
    publish_command(command)
