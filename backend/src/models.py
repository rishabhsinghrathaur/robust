from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    device_uid: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    device_type: Mapped[str] = mapped_column(String(16))
    firmware_version: Mapped[str] = mapped_column(String(64))
    site: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32))
    last_seen_at: Mapped[str] = mapped_column(String(64))

    commands: Mapped[list["Command"]] = relationship(back_populates="device", cascade="all, delete-orphan")
    telemetry_events: Mapped[list["TelemetryRecord"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
    )


class Command(Base):
    __tablename__ = "commands"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), index=True)
    command: Mapped[str] = mapped_column(String(128))
    issued_by: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[str] = mapped_column(String(64), index=True)

    device: Mapped[Device] = relationship(back_populates="commands")


class OtaRelease(Base):
    __tablename__ = "ota_releases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    version: Mapped[str] = mapped_column(String(64))
    hardware_target: Mapped[str] = mapped_column(String(16))
    artifact_url: Mapped[str] = mapped_column(Text)
    mandatory: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[str] = mapped_column(String(64), index=True)


class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), index=True)
    recorded_at: Mapped[str] = mapped_column(String(64), index=True)
    temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    battery_percent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    connectivity: Mapped[str] = mapped_column(String(32), default="good")
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    device: Mapped[Device] = relationship(back_populates="telemetry_events")
