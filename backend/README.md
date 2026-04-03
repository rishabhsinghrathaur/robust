# Backend

The backend is the control plane for device registration, fleet state, command dispatch, and OTA metadata.

## Responsibilities

- register and identify devices
- expose operator-facing APIs
- store firmware release metadata
- dispatch validated commands
- keep an audit trail of critical operations

## Suggested Next Steps

- add JWT-based auth
- add MQTT/WebSocket integration for live device messaging
- add firmware artifact storage and signed OTA manifests

## Persistence

The backend now uses SQLAlchemy with a database URL from `DATABASE_URL`.

- local default: `sqlite:///./robust.db`
- Docker/PostgreSQL: set `DATABASE_URL` to a Postgres connection string

The current schema is created automatically at startup for developer convenience.

## Local Development

```bash
uvicorn src.main:app --reload --port 8000
```
