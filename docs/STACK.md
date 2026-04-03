# Suggested Stack

## Embedded

- ESP32 with ESP-IDF for production-oriented networking and OTA support
- STM32 with FreeRTOS or bare-metal plus a clear transport abstraction layer

## Backend

- FastAPI for early API velocity
- PostgreSQL for registry and audit records
- Redis for short-lived state, queues, and caching
- MQTT broker for low-latency device messaging

## Dashboard

- React + Vite for fast frontend iteration
- charting and event timeline components as the product matures

## AI Layer

- separate service boundary
- typed action schema
- approval workflow for sensitive operations
- audit logging for prompt-to-action traceability

