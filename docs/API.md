# API Overview

## Backend

### `GET /health`

Returns backend health status.

### `GET /devices`

Returns the currently known device list.

### `POST /devices/register`

Registers or refreshes a device record.

Example payload:

```json
{
  "device_uid": "RB-ESP32-01",
  "device_type": "esp32",
  "firmware_version": "1.0.3",
  "site": "Lab A"
}
```

### `POST /devices/{device_id}/commands`

Queues a command for a registered device.
Requires bearer token with at least `operator` role.

Example payload:

```json
{
  "command": "reboot",
  "issued_by": "operator@example"
}
```

### `POST /devices/{device_id}/commands/propose`

Creates a command in `pending_approval` state and opens an approval request.
Requires bearer token with at least `operator` role.

Example payload:

```json
{
  "command": "reboot",
  "issued_by": "operator@example",
  "reason": "Device is unresponsive after config push"
}
```

### `GET /devices/{device_id}`

Returns a selected device plus recent commands and telemetry samples.

### `POST /devices/{device_id}/telemetry`

Stores a telemetry event for a registered device and refreshes its last-seen state.

Example payload:

```json
{
  "temperature_c": 24.5,
  "battery_percent": 91,
  "connectivity": "good",
  "message": "Boot heartbeat"
}
```

### `GET /dashboard/summary`

Returns fleet counters used by the dashboard.

### `GET /dashboard/activity`

Returns recent command and release events for the dashboard activity feed.

### `POST /ota/releases`

Creates OTA metadata for a release artifact.
Requires bearer token with `admin` role.

### `GET /commands`

Returns queued commands across the fleet.
Requires bearer token with at least `viewer` role.

### `GET /ota/releases`

Returns known OTA releases.
Requires bearer token with at least `viewer` role.

### `GET /auth/whoami`

Returns the resolved role for the current bearer token.

### `GET /approvals/pending`

Returns pending approval requests.
Requires bearer token with at least `viewer` role.

### `POST /approvals/{approval_id}/approve`

Approves a pending command request and moves the command to `queued`.
Requires bearer token with `admin` role.

### `POST /approvals/{approval_id}/reject`

Rejects a pending command request and marks the command as `rejected`.
Requires bearer token with `admin` role.

### `GET /audit/events`

Returns recent audit events for traceability.
Requires bearer token with at least `viewer` role.

## AI Service

### `GET /health`

Returns AI service health status.

### `GET /providers/current`

Returns the active AI provider mode and configured model.

### `POST /chat`

Converts natural language into a structured suggested action.

Example payload:

```json
{
  "message": "Roll out the latest ESP32 firmware to outdated devices"
}
```

### `POST /execute`

Returns a structured action plan with approval status. It does not directly control hardware.

## Provider Adapters

The AI service can run in:

- `rule-based` mode for free local fallback
- `ollama` mode against `ROBUST_OLLAMA_BASE_URL`
- `openai-compatible` mode against `ROBUST_OPENAI_COMPAT_BASE_URL`
- `llama-cpp` mode against `ROBUST_LLAMACPP_BASE_URL`

## Design Rule

AI outputs are advisory. Device execution must still pass backend authorization and policy checks.

## Auth

Protected backend routes use `Authorization: Bearer <token>`.

Default development roles:

- `viewer-dev-token`
- `operator-dev-token`
- `admin-dev-token`
