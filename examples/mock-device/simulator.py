import json
import os
from random import randint, random
import urllib.error
import urllib.request


API_BASE_URL = os.getenv("ROBUST_API_BASE_URL", "http://localhost:8000")


def post_json(path: str, payload: dict) -> dict:
    request = urllib.request.Request(
        f"{API_BASE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    try:
        simulated_devices = [
            {
                "device_uid": "RB-DEMO-EDGE-01",
                "device_type": "esp32",
                "firmware_version": "1.0.0",
                "site": "Simulator Lab",
            },
            {
                "device_uid": "RB-DEMO-EDGE-02",
                "device_type": "stm32",
                "firmware_version": "1.0.1",
                "site": "Simulator Lab",
            },
            {
                "device_uid": "RB-DEMO-GREEN-01",
                "device_type": "esp32",
                "firmware_version": "0.9.7",
                "site": "Greenhouse",
            },
        ]
        registered = []
        for registration in simulated_devices:
            device = post_json("/devices/register", registration)
            registered.append(device)
            telemetry = post_json(
                f"/devices/{device['id']}/telemetry",
                {
                    "temperature_c": round(20 + (random() * 10), 1),
                    "battery_percent": randint(48, 100),
                    "connectivity": "good",
                    "message": "Mock heartbeat",
                },
            )
            print("Registered device:")
            print(json.dumps(device, indent=2))
            print("Telemetry:")
            print(json.dumps(telemetry, indent=2))
            print()

        command = post_json(
            f"/devices/{registered[0]['id']}/commands",
            {"command": "sync-config", "issued_by": "mock-device-simulator"},
        )
        print("Queued command:")
        print(json.dumps(command, indent=2))
    except urllib.error.URLError as exc:
        print(f"Failed to reach backend at {API_BASE_URL}: {exc}")


if __name__ == "__main__":
    main()
