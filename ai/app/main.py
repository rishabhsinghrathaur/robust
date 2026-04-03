from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(
    title="Robust AI Service",
    description="AI-assisted command interpretation layer for device fleets.",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=4)


class SuggestedAction(BaseModel):
    action_type: Literal["command", "query", "ota_rollout"]
    target_scope: str
    summary: str
    requires_approval: bool
    confidence: float


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai"}


@app.post("/chat", response_model=SuggestedAction)
def chat(payload: ChatRequest) -> SuggestedAction:
    message = payload.message.lower()
    if "update" in message or "firmware" in message:
        return SuggestedAction(
            action_type="ota_rollout",
            target_scope="fleet:esp32",
            summary="Prepare staged OTA rollout for ESP32 devices on outdated firmware.",
            requires_approval=True,
            confidence=0.82,
        )
    if "restart" in message or "reboot" in message:
        return SuggestedAction(
            action_type="command",
            target_scope="device:unknown",
            summary="Issue reboot command after explicit device selection.",
            requires_approval=True,
            confidence=0.74,
        )
    return SuggestedAction(
        action_type="query",
        target_scope="fleet:all",
        summary="Retrieve current fleet state and telemetry summary before taking action.",
        requires_approval=False,
        confidence=0.68,
    )

