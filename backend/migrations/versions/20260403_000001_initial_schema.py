"""initial schema"""

from alembic import op
import sqlalchemy as sa


revision = "20260403_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("device_uid", sa.String(length=64), nullable=False),
        sa.Column("device_type", sa.String(length=16), nullable=False),
        sa.Column("firmware_version", sa.String(length=64), nullable=False),
        sa.Column("site", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("last_seen_at", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_devices_device_uid"), "devices", ["device_uid"], unique=True)
    op.create_table(
        "ota_releases",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("hardware_target", sa.String(length=16), nullable=False),
        sa.Column("artifact_url", sa.Text(), nullable=False),
        sa.Column("mandatory", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ota_releases_created_at"), "ota_releases", ["created_at"], unique=False)
    op.create_table(
        "commands",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("device_id", sa.String(length=36), nullable=False),
        sa.Column("command", sa.String(length=128), nullable=False),
        sa.Column("issued_by", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_commands_created_at"), "commands", ["created_at"], unique=False)
    op.create_index(op.f("ix_commands_device_id"), "commands", ["device_id"], unique=False)
    op.create_table(
        "telemetry_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.String(length=36), nullable=False),
        sa.Column("recorded_at", sa.String(length=64), nullable=False),
        sa.Column("temperature_c", sa.Float(), nullable=True),
        sa.Column("battery_percent", sa.Integer(), nullable=True),
        sa.Column("connectivity", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_telemetry_records_device_id"), "telemetry_records", ["device_id"], unique=False)
    op.create_index(op.f("ix_telemetry_records_recorded_at"), "telemetry_records", ["recorded_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_telemetry_records_recorded_at"), table_name="telemetry_records")
    op.drop_index(op.f("ix_telemetry_records_device_id"), table_name="telemetry_records")
    op.drop_table("telemetry_records")
    op.drop_index(op.f("ix_commands_device_id"), table_name="commands")
    op.drop_index(op.f("ix_commands_created_at"), table_name="commands")
    op.drop_table("commands")
    op.drop_index(op.f("ix_ota_releases_created_at"), table_name="ota_releases")
    op.drop_table("ota_releases")
    op.drop_index(op.f("ix_devices_device_uid"), table_name="devices")
    op.drop_table("devices")

