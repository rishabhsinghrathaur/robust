# Backend

The backend is the control plane for device registration, fleet state, command dispatch, and OTA metadata.

## Responsibilities

- register and identify devices
- expose operator-facing APIs
- store firmware release metadata
- dispatch validated commands
- keep an audit trail of critical operations

## Suggested Next Steps

- add JWT-based auth if you later need user identity beyond static service roles
- add MQTT/WebSocket integration for live device messaging
- add firmware artifact storage and signed OTA manifests

## Persistence

The backend now uses SQLAlchemy with a database URL from `DATABASE_URL`.

- local default: `sqlite:///./robust.db`
- Docker/PostgreSQL: set `DATABASE_URL` to a Postgres connection string

The current schema can still be auto-created at startup for developer convenience, but Alembic migrations are now included and should be the preferred path.

## Auth and Roles

Protected endpoints use bearer tokens mapped to roles:

- `viewer`: can read protected operational data
- `operator`: can issue device commands
- `admin`: can create OTA releases

Default development tokens:

- `viewer-dev-token`
- `operator-dev-token`
- `admin-dev-token`

Override them with env vars:

- `ROBUST_VIEWER_TOKEN`
- `ROBUST_OPERATOR_TOKEN`
- `ROBUST_ADMIN_TOKEN`

## Migrations

From the `backend/` directory:

```bash
alembic upgrade head
```

## Approval Workflow

High-risk commands can go through an explicit approval path:

1. Operator proposes a command.
2. Backend stores a pending approval request.
3. Admin approves or rejects it.
4. Command state is updated and an audit event is recorded.

Audit history can be queried through the backend for traceability.

Key routes:

- `POST /devices/{device_id}/commands/propose`
- `POST /approvals/{approval_id}/approve`
- `POST /approvals/{approval_id}/reject`
- `GET /audit/events`

## Local Development

```bash
uvicorn src.main:app --reload --port 8000
```
