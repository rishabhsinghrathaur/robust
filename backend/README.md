# Backend

The backend is the control plane for device registration, fleet state, command dispatch, and OTA metadata.

## Responsibilities

- register and identify devices
- expose operator-facing APIs
- store firmware release metadata
- dispatch validated commands
- keep an audit trail of critical operations

## Suggested Next Steps

- replace in-memory repositories with PostgreSQL
- add JWT-based auth
- add MQTT/WebSocket integration for live device messaging
- add firmware artifact storage and signed OTA manifests

## Local Development

```bash
uvicorn src.main:app --reload --port 8000
```

