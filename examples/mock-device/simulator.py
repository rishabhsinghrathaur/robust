import json
import os
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
    registration = {
        "device_uid": "RB-DEMO-EDGE-01",
        "device_type": "esp32",
        "firmware_version": "1.0.0",
        "site": "Simulator Lab",
    }

    try:
        device = post_json("/devices/register", registration)
        print("Registered device:")
        print(json.dumps(device, indent=2))

        command = post_json(
            f"/devices/{device['id']}/commands",
            {"command": "sync-config", "issued_by": "mock-device-simulator"},
        )
        print("\nQueued command:")
        print(json.dumps(command, indent=2))
    except urllib.error.URLError as exc:
        print(f"Failed to reach backend at {API_BASE_URL}: {exc}")


if __name__ == "__main__":
    main()

