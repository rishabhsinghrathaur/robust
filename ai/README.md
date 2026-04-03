# AI Service

The AI service converts natural-language operator requests into structured actions that the backend can validate and execute safely.

## Safety Position

The service should never act as an unrestricted direct control channel. It should:

- parse intent
- produce typed actions
- include rationale and confidence
- flag risky operations for human approval

## Suggested Next Steps

- connect to an LLM provider
- add action schema validation
- add policy enforcement hooks
- add conversation memory scoped per operator or incident

## Local Development

```bash
uvicorn app.main:app --reload --port 8100
```

