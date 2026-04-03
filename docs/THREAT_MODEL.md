# Threat Model

## High-Risk Areas

- device identity spoofing
- malicious firmware distribution
- AI-generated unsafe commands
- leaked operator credentials
- insecure OTA rollback paths
- exposed MQTT brokers or backend APIs

## Baseline Mitigations

- unique per-device identity
- signed firmware artifacts
- transport encryption
- explicit authorization on commands
- approval flow for destructive actions
- audit logs for prompt-to-command traceability

## AI-Specific Rule

The model must never be the final authority for physical actions. The backend must validate:

- who requested the action
- what device or fleet is targeted
- whether the action is allowed
- whether human approval is required

## Open Source Consideration

An open-source repo increases transparency, but it does not reduce the need for secure deployment defaults. Documentation should make production hardening non-optional.

