from datetime import UTC, datetime
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from .auth import AuthContext, require_role
from .db import AUTO_CREATE_SCHEMA, AUTO_SEED_DEMO_DATA, Base, SessionLocal, engine
from .models import ApprovalRequest, AuditEvent, Command, Device, OtaRelease, TelemetryRecord


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


class ProposedCommandRequest(BaseModel):
    command: str = Field(..., min_length=2)
    issued_by: str = Field(..., min_length=2)
    reason: str = Field(..., min_length=4)


class ApprovalDecisionRequest(BaseModel):
    note: str = Field(default="")


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


def serialize_approval(approval: ApprovalRequest) -> dict:
    return {
        "id": approval.id,
        "command_id": approval.command_id,
        "requested_by": approval.requested_by,
        "reason": approval.reason,
        "status": approval.status,
        "approved_by": approval.approved_by,
        "decided_at": approval.decided_at,
        "created_at": approval.created_at,
    }


def serialize_audit_event(event: AuditEvent) -> dict:
    return {
        "id": event.id,
        "actor": event.actor,
        "actor_role": event.actor_role,
        "event_type": event.event_type,
        "target_type": event.target_type,
        "target_id": event.target_id,
        "summary": event.summary,
        "created_at": event.created_at,
    }


def record_audit(
    session,
    *,
    actor: str,
    actor_role: str,
    event_type: str,
    target_type: str,
    target_id: str,
    summary: str,
) -> None:
    session.add(
        AuditEvent(
            actor=actor,
            actor_role=actor_role,
            event_type=event_type,
            target_type=target_type,
            target_id=target_id,
            summary=summary,
            created_at=now_iso(),
        )
    )


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
        session.flush()
        queued_command = session.scalar(select(Command).where(Command.device_id == initial_devices[0].id).limit(1))
        if queued_command:
            session.add(
                ApprovalRequest(
                    command_id=queued_command.id,
                    requested_by="system",
                    reason="Bootstrap review of seeded sync workflow",
                    status="approved",
                    approved_by="system",
                    decided_at=now_iso(),
                    created_at=now_iso(),
                )
            )
            record_audit(
                session,
                actor="system",
                actor_role="admin",
                event_type="command.seeded",
                target_type="command",
                target_id=queued_command.id,
                summary="Seeded command and approval example created.",
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


@app.get("/approvals/pending")
def list_pending_approvals(_: AuthContext = Depends(require_role("viewer"))) -> dict[str, list[dict]]:
    with SessionLocal() as session:
        approvals = session.scalars(
            select(ApprovalRequest).where(ApprovalRequest.status == "pending").order_by(ApprovalRequest.created_at.desc())
        ).all()
        return {"approvals": [serialize_approval(approval) for approval in approvals]}


@app.get("/audit/events")
def list_audit_events(_: AuthContext = Depends(require_role("viewer"))) -> dict[str, list[dict]]:
    with SessionLocal() as session:
        events = session.scalars(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(50)).all()
        return {"events": [serialize_audit_event(event) for event in events]}


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
            record_audit(
                session,
                actor=payload.device_uid,
                actor_role="device",
                event_type="device.reregistered",
                target_type="device",
                target_id=existing.id,
                summary=f"Device {payload.device_uid} refreshed registration.",
            )
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
        record_audit(
            session,
            actor=payload.device_uid,
            actor_role="device",
            event_type="device.registered",
            target_type="device",
            target_id=device.id,
            summary=f"Device {payload.device_uid} registered at site {payload.site}.",
        )
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
        record_audit(
            session,
            actor=payload.issued_by,
            actor_role="operator",
            event_type="command.queued",
            target_type="command",
            target_id=command.id,
            summary=f"Command '{payload.command}' queued for device {device.device_uid}.",
        )
        session.commit()
        session.refresh(command)
        return serialize_command(command)


@app.post("/devices/{device_id}/commands/propose")
def propose_command(
    device_id: str,
    payload: ProposedCommandRequest,
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
            status="pending_approval",
            created_at=now_iso(),
        )
        session.add(command)
        session.flush()

        approval = ApprovalRequest(
            command_id=command.id,
            requested_by=payload.issued_by,
            reason=payload.reason,
            status="pending",
            created_at=now_iso(),
        )
        session.add(approval)
        session.flush()
        record_audit(
            session,
            actor=payload.issued_by,
            actor_role="operator",
            event_type="approval.requested",
            target_type="approval",
            target_id=str(approval.id),
            summary=f"Approval requested for command '{payload.command}' on device {device.device_uid}.",
        )
        session.commit()
        session.refresh(command)
        session.refresh(approval)
        return {"command": serialize_command(command), "approval": serialize_approval(approval)}


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


@app.post("/approvals/{approval_id}/approve")
def approve_command(
    approval_id: int,
    payload: ApprovalDecisionRequest,
    context: AuthContext = Depends(require_role("admin")),
) -> dict:
    with SessionLocal() as session:
        approval = session.get(ApprovalRequest, approval_id)
        if not approval:
            raise HTTPException(status_code=404, detail="Approval request not found")
        if approval.status != "pending":
            raise HTTPException(status_code=409, detail="Approval request already decided")

        command = session.get(Command, approval.command_id)
        if not command:
            raise HTTPException(status_code=404, detail="Command not found")

        approval.status = "approved"
        approval.approved_by = context.token_name
        approval.decided_at = now_iso()
        command.status = "queued"
        record_audit(
            session,
            actor=context.token_name,
            actor_role=context.role,
            event_type="approval.approved",
            target_type="approval",
            target_id=str(approval.id),
            summary=f"Approval granted for command '{command.command}'. {payload.note}".strip(),
        )
        session.commit()
        session.refresh(approval)
        session.refresh(command)
        return {"command": serialize_command(command), "approval": serialize_approval(approval)}


@app.post("/approvals/{approval_id}/reject")
def reject_command(
    approval_id: int,
    payload: ApprovalDecisionRequest,
    context: AuthContext = Depends(require_role("admin")),
) -> dict:
    with SessionLocal() as session:
        approval = session.get(ApprovalRequest, approval_id)
        if not approval:
            raise HTTPException(status_code=404, detail="Approval request not found")
        if approval.status != "pending":
            raise HTTPException(status_code=409, detail="Approval request already decided")

        command = session.get(Command, approval.command_id)
        if not command:
            raise HTTPException(status_code=404, detail="Command not found")

        approval.status = "rejected"
        approval.approved_by = context.token_name
        approval.decided_at = now_iso()
        command.status = "rejected"
        record_audit(
            session,
            actor=context.token_name,
            actor_role=context.role,
            event_type="approval.rejected",
            target_type="approval",
            target_id=str(approval.id),
            summary=f"Approval rejected for command '{command.command}'. {payload.note}".strip(),
        )
        session.commit()
        session.refresh(approval)
        session.refresh(command)
        return {"command": serialize_command(command), "approval": serialize_approval(approval)}


@app.post("/ota/releases")
def create_release(
    payload: OtaReleaseRequest,
    context: AuthContext = Depends(require_role("admin")),
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
        record_audit(
            session,
            actor=context.token_name,
            actor_role=context.role,
            event_type="ota.release_created",
            target_type="ota_release",
            target_id=release.id,
            summary=f"OTA release {payload.version} created for {payload.hardware_target}.",
        )
        session.commit()
        session.refresh(release)
        return serialize_release(release)


@app.get("/ota/releases")
def list_releases(_: AuthContext = Depends(require_role("viewer"))) -> dict[str, list[dict]]:
    with SessionLocal() as session:
        releases = session.scalars(select(OtaRelease).order_by(OtaRelease.created_at.desc())).all()
        return {"releases": [serialize_release(release) for release in releases]}
