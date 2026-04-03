from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="Robust Backend",
    description="Control plane API for device registration, fleet management, and OTA metadata.",
    version="0.1.0",
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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}


@app.get("/devices")
def list_devices() -> dict[str, list[dict]]:
    return {"devices": list(devices.values())}


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

