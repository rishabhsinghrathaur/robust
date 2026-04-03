# STM32 Firmware

Recommended modules:

- `boot/`
- `network/`
- `identity/`
- `commands/`
- `telemetry/`
- `ota/`

## Notes

STM32 deployments often vary more by board and RTOS choice than ESP32. Keep transport, identity, and update layers abstracted so the same backend contract works across both families.

