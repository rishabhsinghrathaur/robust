from datetime import UTC, datetime
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from .auth import AuthContext, require_role
from .db import AUTO_CREATE_SCHEMA, AUTO_SEED_DEMO_DATA, Base, SessionLocal, engine
from .models import Command, Device, OtaRelease, TelemetryRecord


app = FastAPI(
    title="Robust Backend",
    description="Control plane API for device registration, fleet management, and OTA metadata.",
    version="0.3.0",
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
    device_type: str
    firmware_version: str
    site: str = Field(default="default")


class CommandRequest(BaseModel):
    command: str = Field(..., min_length=2)
    issued_by: str = Field(..., min_length=2)


class OtaReleaseRequest(BaseModel):
    version: str
    hardware_target: str
    artifact_url: str
    mandatory: bool = False


class TelemetryEvent(BaseModel):
    temperature_c: float | None = None
    battery_percent: int | None = None
    connectivity: str = "good"
    message: str | None = None


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def serialize_device(device: Device) -> dict:
    return {
        "id": device.id,
        "device_uid": device.device_uid,
        "device_type": device.device_type,
        "firmware_version": device.firmware_version,
        "site": device.site,
        "status": device.status,
        "last_seen_at": device.last_seen_at,
    }


def serialize_command(command: Command) -> dict:
    return {
        "id": command.id,
        "device_id": command.device_id,
        "command": command.command,
        "issued_by": command.issued_by,
        "status": command.status,
        "created_at": command.created_at,
    }


def serialize_release(release: OtaRelease) -> dict:
    return {
        "id": release.id,
        "version": release.version,
        "hardware_target": release.hardware_target,
        "artifact_url": release.artifact_url,
        "mandatory": release.mandatory,
        "created_at": release.created_at,
    }


def serialize_telemetry(record: TelemetryRecord) -> dict:
    return {
        "recorded_at": record.recorded_at,
        "temperature_c": record.temperature_c,
        "battery_percent": record.battery_percent,
        "connectivity": record.connectivity,
        "message": record.message,
    }


def seed_demo_data() -> None:
    with SessionLocal() as session:
        existing = session.scalar(select(func.count()).select_from(Device))
        if existing:
            return

        initial_devices = [
            Device(
                id=str(uuid4()),
                device_uid="RB-ESP32-01",
                device_type="esp32",
                firmware_version="1.0.3",
                site="Lab A",
                status="online",
                last_seen_at=now_iso(),
            ),
            Device(
                id=str(uuid4()),
                device_uid="RB-STM32-07",
                device_type="stm32",
                firmware_version="1.1.0",
                site="Field 2",
                status="updating",
                last_seen_at=now_iso(),
            ),
            Device(
                id=str(uuid4()),
                device_uid="RB-ESP32-19",
                device_type="esp32",
                firmware_version="0.9.8",
                site="Greenhouse",
                status="offline",
                last_seen_at=now_iso(),
            ),
        ]
        session.add_all(initial_devices)
        session.flush()

        session.add(
            OtaRelease(
                id=str(uuid4()),
                version="1.1.0",
                hardware_target="esp32",
                artifact_url="https://example.com/firmware/esp32/1.1.0.bin",
                mandatory=False,
                created_at=now_iso(),
            )
        )
        session.add(
            Command(
                id=str(uuid4()),
                device_id=initial_devices[0].id,
                command="sync-config",
                issued_by="system",
                status="queued",
                created_at=now_iso(),
            )
        )
        for device in initial_devices:
            session.add(
                TelemetryRecord(
                    device_id=device.id,
                    recorded_at=now_iso(),
                    temperature_c=24.5,
                    battery_percent=91,
                    connectivity="good",
                    message="Boot heartbeat",
                )
            )
        session.commit()


if AUTO_CREATE_SCHEMA:
    Base.metadata.create_all(bind=engine)
if AUTO_SEED_DEMO_DATA:
    seed_demo_data()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}


@app.get("/auth/whoami")
def whoami(context: AuthContext = Depends(require_role("viewer"))) -> dict[str, str]:
    return context.model_dump()


@app.get("/devices")
def list_devices() -> dict[str, list[dict]]:
    with SessionLocal() as session:
        devices = session.scalars(select(Device).order_by(Device.last_seen_at.desc())).all()
        return {"devices": [serialize_device(device) for device in devices]}


@app.get("/devices/{device_id}")
def get_device(device_id: str) -> dict:
    with SessionLocal() as session:
        device = session.get(Device, device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        recent_commands = session.scalars(
            select(Command).where(Command.device_id == device_id).order_by(Command.created_at.desc()).limit(5)
        ).all()
        telemetry = session.scalars(
            select(TelemetryRecord)
            .where(TelemetryRecord.device_id == device_id)
            .order_by(TelemetryRecord.recorded_at.desc())
            .limit(10)
        ).all()
        return {
            "device": serialize_device(device),
            "recent_commands": [serialize_command(item) for item in recent_commands],
            "telemetry": [serialize_telemetry(item) for item in telemetry],
        }


@app.get("/dashboard/summary")
def dashboard_summary() -> dict:
    with SessionLocal() as session:
        devices = session.scalars(select(Device)).all()
        total_devices = len(devices)
        online_devices = sum(1 for device in devices if device.status == "online")
        stale_devices = sum(1 for device in devices if device.status != "online")
        sites = len({device.site for device in devices})
        queued_commands = session.scalar(select(func.count()).select_from(Command)) or 0
        available_releases = session.scalar(select(func.count()).select_from(OtaRelease)) or 0
        return {
            "managed_devices": total_devices,
            "healthy_percent": round((online_devices / total_devices) * 100) if total_devices else 0,
            "devices_needing_attention": stale_devices,
            "active_sites": sites,
            "queued_commands": queued_commands,
            "available_releases": available_releases,
        }


@app.get("/dashboard/activity")
def dashboard_activity() -> dict[str, list[dict]]:
    with SessionLocal() as session:
        activity = []
        commands = session.scalars(select(Command).order_by(Command.created_at.desc()).limit(5)).all()
        releases = session.scalars(select(OtaRelease).order_by(OtaRelease.created_at.desc()).limit(3)).all()
        for command in commands:
            activity.append(
                {
                    "kind": "command",
                    "summary": f"{command.issued_by} queued {command.command}",
                    "timestamp": command.created_at,
                }
            )
        for release in releases:
            activity.append(
                {
                    "kind": "release",
                    "summary": f"Release {release.version} available for {release.hardware_target}",
                    "timestamp": release.created_at,
                }
            )
        activity.sort(key=lambda item: item["timestamp"], reverse=True)
        return {"activity": activity[:8]}


@app.post("/devices/register")
def register_device(payload: DeviceRegistrationRequest) -> dict:
    with SessionLocal() as session:
        existing = session.scalar(select(Device).where(Device.device_uid == payload.device_uid))
        if existing:
            existing.last_seen_at = now_iso()
            existing.firmware_version = payload.firmware_version
            existing.site = payload.site
            existing.device_type = payload.device_type
            existing.status = "online"
            session.commit()
            session.refresh(existing)
            return serialize_device(existing)

        device = Device(
            id=str(uuid4()),
            device_uid=payload.device_uid,
            device_type=payload.device_type,
            firmware_version=payload.firmware_version,
            site=payload.site,
            status="online",
            last_seen_at=now_iso(),
        )
        session.add(device)
        session.commit()
        session.refresh(device)
        return serialize_device(device)


@app.post("/devices/{device_id}/commands")
def issue_command(
    device_id: str,
    payload: CommandRequest,
    _: AuthContext = Depends(require_role("operator")),
) -> dict:
    with SessionLocal() as session:
        device = session.get(Device, device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        command = Command(
            id=str(uuid4()),
            device_id=device_id,
            command=payload.command,
            issued_by=payload.issued_by,
            status="queued",
            created_at=now_iso(),
        )
        session.add(command)
        session.commit()
        session.refresh(command)
        return serialize_command(command)


@app.post("/devices/{device_id}/telemetry")
def record_telemetry(device_id: str, payload: TelemetryEvent) -> dict:
    with SessionLocal() as session:
        device = session.get(Device, device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        record = TelemetryRecord(
            device_id=device_id,
            recorded_at=now_iso(),
            temperature_c=payload.temperature_c,
            battery_percent=payload.battery_percent,
            connectivity=payload.connectivity,
            message=payload.message,
        )
        session.add(record)
        device.last_seen_at = record.recorded_at
        if payload.connectivity == "offline":
            device.status = "offline"
        elif device.status == "offline":
            device.status = "online"
        session.commit()
        session.refresh(record)
        return serialize_telemetry(record)


@app.get("/commands")
def list_commands(_: AuthContext = Depends(require_role("viewer"))) -> dict[str, list[dict]]:
    with SessionLocal() as session:
        commands = session.scalars(select(Command).order_by(Command.created_at.desc())).all()
        return {"commands": [serialize_command(command) for command in commands]}


@app.post("/ota/releases")
def create_release(
    payload: OtaReleaseRequest,
    _: AuthContext = Depends(require_role("admin")),
) -> dict:
    with SessionLocal() as session:
        release = OtaRelease(
            id=str(uuid4()),
            version=payload.version,
            hardware_target=payload.hardware_target,
            artifact_url=payload.artifact_url,
            mandatory=payload.mandatory,
            created_at=now_iso(),
        )
        session.add(release)
        session.commit()
        session.refresh(release)
        return serialize_release(release)


@app.get("/ota/releases")
def list_releases(_: AuthContext = Depends(require_role("viewer"))) -> dict[str, list[dict]]:
    with SessionLocal() as session:
        releases = session.scalars(select(OtaRelease).order_by(OtaRelease.created_at.desc())).all()
        return {"releases": [serialize_release(release) for release in releases]}
