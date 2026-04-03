# Firmware

This directory holds reference firmware implementations for supported hardware families.

## Design Goals

- simple first-boot provisioning
- reliable device registration
- secure OTA handling
- resilient command execution
- offline-tolerant behavior

## Layout

- `esp32/`: ESP-IDF or Arduino-compatible implementation path
- `stm32/`: STM32Cube or RTOS-based implementation path

## Firmware Concerns

- credentials should be stored in secure or protected storage where available
- firmware images should be signed and verified before activation
- commands should be typed, versioned, and idempotent
- watchdog and rollback strategies should be defined per board family

