# Robust

Robust is an AI-connected IoT device management platform built around ESP32/STM-class hardware, a web control plane, secure device registration, OTA firmware delivery, and an AI chatbot interface for real-time command execution.

The goal is simple: make physical devices as easy to manage, update, and automate as modern cloud applications.

## Overview

This project connects embedded hardware and software intelligence through a single operational workflow:

- Devices self-onboard through a local Wi-Fi provisioning flow.
- Each device registers using a unique hardware-backed identity.
- A central backend manages device state, configuration, and OTA rollout.
- A web dashboard gives operators visibility and control.
- An AI chatbot can translate high-level instructions into device-safe commands.

## Core Features

- Self-hosted onboarding flow for first-time Wi-Fi provisioning
- Unique device ID-based registration with central server validation
- Remote fleet management through a web dashboard
- Over-the-air firmware updates with rollout control
- AI chatbot interface for dynamic command and automation workflows
- Real-time telemetry, command dispatch, and status synchronization

## Why This Matters

Most IoT systems solve either device connectivity, firmware updates, or automation. Robust is designed to combine all three, with AI as an operational interface rather than a disconnected add-on.

That creates a platform where intelligence can directly interact with hardware in production:

- issue commands
- automate repetitive operations
- monitor field devices
- push firmware safely
- reduce manual support effort

## System Architecture

```text
+-------------------+        +--------------------+        +------------------+
| ESP32 / STM Node  | <----> | Backend API Layer  | <----> | Web Dashboard    |
|-------------------|        |--------------------|        |------------------|
| Wi-Fi Provisioning|        | Auth / Registry    |        | Device Ops       |
| Device Identity   |        | Device Management  |        | Fleet Monitoring |
| Command Handler   |        | OTA Orchestration  |        | Update Control   |
| OTA Agent         |        | Telemetry Ingest   |        | Audit Visibility |
+-------------------+        +--------------------+        +------------------+
          ^                            ^
          |                            |
          +----------------------------+
                       |
                +-------------+
                | AI Chatbot  |
                |-------------|
                | Intent ->   |
                | Safe Action |
                | Suggestions |
                +-------------+
```

More detail is available in [docs/ARCHITECTURE.md](/home/rishabh/Desktop/current projects /robust/docs/ARCHITECTURE.md).

## Key Design Priorities

### 1. Scalability

The platform should scale from a few prototype boards to large device fleets. Key design choices should include:

- stateless backend services
- event-driven device communication
- queue-based OTA rollout orchestration
- separate control-plane and telemetry ingestion paths
- tenant-aware device grouping and access control

### 2. Security

IoT platforms fail when identity and updates are weak. Recommended baseline:

- per-device credentials instead of shared secrets
- signed firmware images
- TLS-secured transport
- short-lived tokens for web and service access
- command authorization rules for AI-triggered actions
- audit trails for provisioning, updates, and remote commands

### 3. Reliability

Field hardware needs safe failure behavior:

- rollback-capable OTA updates
- idempotent command execution
- device heartbeat and last-seen tracking
- retries with backoff for unstable networks
- offline-safe device behavior when cloud connectivity is lost

## Repository Layout

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── ai/
│   ├── app/
│   └── README.md
├── backend/
│   ├── src/
│   └── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   └── USE_CASES.md
├── dashboard/
│   ├── src/
│   └── README.md
├── firmware/
│   ├── esp32/
│   ├── stm32/
│   └── README.md
├── scripts/
│   └── bootstrap.sh
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
├── docker-compose.yml
└── .gitignore
```

## Getting Started

This repository is currently scaffolded as a multi-service project with separate boundaries for firmware, backend APIs, dashboard UX, and AI-assisted command handling.

### Services

- `backend`: FastAPI control plane for devices, OTA metadata, and command dispatch
- `dashboard`: React + Vite operator dashboard
- `ai`: FastAPI service that converts natural language into structured, reviewable device actions
- `firmware`: reference layout for ESP32 and STM32 device firmware

### Quick Start

1. Copy [.env.example](/home/rishabh/Desktop/current%20projects%20/robust/.env.example) to `.env`.
2. Review each service README for local setup.
3. Use [docker-compose.yml](/home/rishabh/Desktop/current%20projects%20/robust/docker-compose.yml) as the initial orchestration reference.
4. Expand the starter implementations into production-ready services incrementally.

## Feedback and Improvement Areas

This project is actively shaped around five major questions:

### Architecture and Scalability

- Should command delivery be MQTT-first, WebSocket-first, or hybrid?
- How should OTA rollout be staged across device groups?
- What is the right split between edge logic and centralized orchestration?

### Security Best Practices

- How should device identity be provisioned at manufacturing time?
- What is the cleanest trust model for AI-issued commands?
- How should secrets, certificates, and firmware signing keys be rotated?

### UI and UX

- Fleet-level views for health, firmware version, and connectivity
- Device detail pages with logs, telemetry, and command history
- Guided onboarding and provisioning visibility
- Safe operator flows for updates, rollback, and AI suggestions

### Real-World Use Cases

- remote industrial monitoring
- smart agriculture and irrigation control
- building automation
- energy monitoring and control
- classroom, lab, or research hardware fleets
- field diagnostics for installed embedded products

### Robustness Improvements

- device digital twin model
- policy engine for safe automation
- role-based access control
- observability dashboards and alerting
- staged deployments with auto-rollback
- simulation environment for hardware-free testing

## Suggested Technical Roadmap

See [docs/ROADMAP.md](/home/rishabh/Desktop/current projects /robust/docs/ROADMAP.md) for the phased execution plan.

## Real-World Use Cases

See [docs/USE_CASES.md](/home/rishabh/Desktop/current projects /robust/docs/USE_CASES.md) for deployment ideas and product directions.

## Contributing

Contributions are welcome across embedded firmware, backend infrastructure, web UI, AI tooling, testing, and documentation.

Start here:

- [CONTRIBUTING.md](/home/rishabh/Desktop/current projects /robust/CONTRIBUTING.md)
- [SECURITY.md](/home/rishabh/Desktop/current projects /robust/SECURITY.md)

## License

This project is released under the MIT License. See [LICENSE](/home/rishabh/Desktop/current projects /robust/LICENSE).

