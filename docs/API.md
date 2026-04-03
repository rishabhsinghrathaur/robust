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

Example payload:

```json
{
  "command": "reboot",
  "issued_by": "operator@example"
}
```

### `GET /dashboard/summary`

Returns fleet counters used by the dashboard.

### `POST /ota/releases`

Creates OTA metadata for a release artifact.

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

## Design Rule

AI outputs are advisory. Device execution must still pass backend authorization and policy checks.

