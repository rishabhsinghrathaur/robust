# Open Source Strategy

## What Should Be Open

- firmware structure and device protocol
- backend API and policy engine
- dashboard frontend
- AI routing and structured action schema
- mock device simulator and local development stack
- documentation, examples, and deployment references

## What Should Not Be Committed

- production secrets
- real device credentials
- firmware signing keys
- tenant-specific infrastructure config
- paid model provider keys

## Model Strategy

Robust should stay provider-agnostic.

Recommended approach:

- keep a local rule-based fallback for development
- support free or self-hosted models through adapters
- treat hosted inference as optional, not required
- always translate model output into typed backend actions

## Good Open Model Fit

- small local models for intent parsing
- medium instruct models for operator chat and summaries
- larger self-hosted models only when needed for richer reasoning

## Project Positioning

Robust should be presented as:

- an open control plane for connected devices
- an AI-assisted automation layer with safety boundaries
- a hardware-friendly system that can be tested without real devices

## Contributor Expectations

- changes should preserve auditability
- AI features must remain reviewable and policy-bound
- hardware protocols should be versioned and backward-aware

