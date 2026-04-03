# AI Service

The AI service converts natural-language operator requests into structured actions that the backend can validate and execute safely.

## Safety Position

The service should never act as an unrestricted direct control channel. It should:

- parse intent
- produce typed actions
- include rationale and confidence
- flag risky operations for human approval

## Suggested Next Steps

- connect to an LLM provider through an adapter layer
- add action schema validation
- add policy enforcement hooks
- add conversation memory scoped per operator or incident

## Provider Modes

The service is designed to remain usable without paid inference.

- `rule-based`: free local fallback for development and demos
- `ollama`: self-hosted local inference
- `llama-cpp`: embedded or server-hosted local inference
- `openai-compatible`: generic adapter mode for any OpenAI-style API

Use env vars:

```bash
ROBUST_AI_PROVIDER=ollama
ROBUST_AI_MODEL=qwen2.5:7b
```

## Local Development

```bash
uvicorn app.main:app --reload --port 8100
```
