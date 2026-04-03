# ESP32 Firmware

Recommended modules:

- `provisioning/`
- `network/`
- `registry/`
- `telemetry/`
- `commands/`
- `ota/`

## Boot Sequence

1. Start in provisioning mode if no Wi-Fi credentials exist.
2. Join configured network.
3. Register with backend using unique device identifier.
4. Start heartbeat and telemetry loop.
5. Poll or subscribe for commands and OTA instructions.

