# Architecture

## Objectives

Robust is designed as a control plane for connected embedded devices with AI-assisted operations. The architecture should support:

- secure device onboarding
- remote command execution
- OTA firmware delivery
- fleet monitoring
- safe automation through AI-assisted workflows

## High-Level Components

### 1. Device Layer

Embedded hardware such as ESP32 or STM-based boards is responsible for:

- first-boot provisioning access point
- Wi-Fi credential capture
- device identity presentation
- telemetry publishing
- command execution
- OTA download and firmware swap

Recommended device-side modules:

- connectivity manager
- provisioning service
- secure credential store
- telemetry publisher
- command dispatcher
- OTA client with rollback support

### 2. Control Plane / Backend

The backend is the source of truth for devices, operators, policies, and firmware releases.

Recommended services:

- device registry service
- authentication and authorization service
- command broker / dispatcher
- OTA orchestration service
- telemetry ingestion pipeline
- audit and event logging service

Recommended storage:

- relational database for accounts, devices, firmware metadata, and audit events
- object storage for firmware artifacts
- message broker for events, commands, and update rollout tasks
- time-series or analytics store for telemetry at scale

### 3. Web Dashboard

The dashboard should provide:

- fleet overview
- device health monitoring
- firmware version visibility
- per-device control actions
- command history
- rollout management
- operator and team permissions

### 4. AI Command Layer

The AI layer should not directly bypass backend policy checks. A safer model is:

1. User issues natural-language instruction.
2. AI parses intent and proposes structured action.
3. Backend validates permissions and policy.
4. Action is logged and dispatched to the target device.
5. Result is returned to the user with traceability.

This keeps AI useful without letting it become an ungoverned control path.

## Recommended Communication Model

Use a split strategy:

- HTTPS for onboarding, registration, and admin actions
- MQTT or WebSocket for low-latency device messaging
- signed firmware download URLs for OTA delivery

This avoids overloading one protocol with every responsibility.

## Scalability Recommendations

- Keep API services stateless behind a load balancer.
- Partition telemetry ingestion from command/control paths.
- Use background workers for OTA campaign scheduling.
- Group devices into fleets, sites, or tenants.
- Design for eventual consistency in non-critical dashboards.

## Security Model

### Device Identity

- provision unique per-device credentials
- avoid global shared secrets
- bind device registration to manufacturing or enrollment workflow

### Transport Security

- use TLS everywhere
- prefer mutual authentication for high-trust environments
- rotate credentials and revoke compromised devices

### Firmware Security

- sign firmware images
- verify signatures on-device before activation
- preserve previous working image for rollback

### AI Command Safety

- convert natural language into constrained, typed actions
- apply authorization before execution
- require confirmation for high-risk operations
- log prompt, action, target, and result for audits

## Reliability Concerns

Key failure modes to handle explicitly:

- network interruptions during OTA
- duplicate command delivery
- partial provisioning
- token expiration
- server restarts during long-running update campaigns
- devices stuck on incompatible firmware

Mitigations:

- resumable downloads
- command IDs with deduplication
- heartbeat monitoring
- phased rollout with canary groups
- automatic rollback thresholds

## Suggested Phase Split

### Phase 1

- device onboarding
- registry
- dashboard basics
- manual command dispatch

### Phase 2

- OTA management
- fleet segmentation
- audit logs
- alerting

### Phase 3

- AI command assistant
- policy engine
- automation workflows
- analytics and prediction

