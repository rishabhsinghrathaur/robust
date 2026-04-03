from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(
    title="Robust Backend",
    description="Control plane API for device registration, fleet management, and OTA metadata.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DeviceRegistrationRequest(BaseModel):
    device_uid: str = Field(..., min_length=6, description="Unique hardware identifier")
    device_type: Literal["esp32", "stm32"]
    firmware_version: str
    site: str = Field(default="default")


class CommandRequest(BaseModel):
    command: str = Field(..., min_length=2)
    issued_by: str = Field(..., min_length=2)


class OtaRelease(BaseModel):
    version: str
    hardware_target: Literal["esp32", "stm32"]
    artifact_url: str
    mandatory: bool = False


devices: dict[str, dict] = {}
commands: list[dict] = []
releases: list[dict] = []


def seed_demo_data() -> None:
    if devices:
        return

    initial_devices = [
        {
            "id": str(uuid4()),
            "device_uid": "RB-ESP32-01",
            "device_type": "esp32",
            "firmware_version": "1.0.3",
            "site": "Lab A",
            "status": "online",
            "last_seen_at": datetime.now(UTC).isoformat(),
        },
        {
            "id": str(uuid4()),
            "device_uid": "RB-STM32-07",
            "device_type": "stm32",
            "firmware_version": "1.1.0",
            "site": "Field 2",
            "status": "updating",
            "last_seen_at": datetime.now(UTC).isoformat(),
        },
        {
            "id": str(uuid4()),
            "device_uid": "RB-ESP32-19",
            "device_type": "esp32",
            "firmware_version": "0.9.8",
            "site": "Greenhouse",
            "status": "offline",
            "last_seen_at": datetime.now(UTC).isoformat(),
        },
    ]

    for device in initial_devices:
        devices[device["id"]] = device

    releases.append(
        {
            "id": str(uuid4()),
            "version": "1.1.0",
            "hardware_target": "esp32",
            "artifact_url": "https://example.com/firmware/esp32/1.1.0.bin",
            "mandatory": False,
            "created_at": datetime.now(UTC).isoformat(),
        }
    )

    commands.append(
        {
            "id": str(uuid4()),
            "device_id": initial_devices[0]["id"],
            "command": "sync-config",
            "issued_by": "system",
            "status": "queued",
            "created_at": datetime.now(UTC).isoformat(),
        }
    )


seed_demo_data()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}


@app.get("/devices")
def list_devices() -> dict[str, list[dict]]:
    return {"devices": list(devices.values())}


@app.get("/dashboard/summary")
def dashboard_summary() -> dict:
    total_devices = len(devices)
    online_devices = sum(1 for device in devices.values() if device["status"] == "online")
    stale_devices = sum(1 for device in devices.values() if device["status"] != "online")
    sites = len({device["site"] for device in devices.values()})
    return {
        "managed_devices": total_devices,
        "healthy_percent": round((online_devices / total_devices) * 100) if total_devices else 0,
        "devices_needing_attention": stale_devices,
        "active_sites": sites,
        "queued_commands": len(commands),
        "available_releases": len(releases),
    }


@app.post("/devices/register")
def register_device(payload: DeviceRegistrationRequest) -> dict:
    existing = next((item for item in devices.values() if item["device_uid"] == payload.device_uid), None)
    if existing:
        existing["last_seen_at"] = datetime.now(UTC).isoformat()
        existing["firmware_version"] = payload.firmware_version
        return existing

    device_id = str(uuid4())
    record = {
        "id": device_id,
        "device_uid": payload.device_uid,
        "device_type": payload.device_type,
        "firmware_version": payload.firmware_version,
        "site": payload.site,
        "status": "online",
        "last_seen_at": datetime.now(UTC).isoformat(),
    }
    devices[device_id] = record
    return record


@app.post("/devices/{device_id}/commands")
def issue_command(device_id: str, payload: CommandRequest) -> dict:
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")

    command = {
        "id": str(uuid4()),
        "device_id": device_id,
        "command": payload.command,
        "issued_by": payload.issued_by,
        "status": "queued",
        "created_at": datetime.now(UTC).isoformat(),
    }
    commands.append(command)
    return command


@app.get("/commands")
def list_commands() -> dict[str, list[dict]]:
    return {"commands": commands}


@app.post("/ota/releases")
def create_release(payload: OtaRelease) -> dict:
    release = payload.model_dump()
    release["id"] = str(uuid4())
    release["created_at"] = datetime.now(UTC).isoformat()
    releases.append(release)
    return release


@app.get("/ota/releases")
def list_releases() -> dict[str, list[dict]]:
    return {"releases": releases}
