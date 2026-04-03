from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .providers import get_provider


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
    provider: str
    model: str
    execution_mode: str


class ExecuteRequest(BaseModel):
    message: str = Field(..., min_length=4)
    requested_by: str = Field(default="operator")


class ProviderStatus(BaseModel):
    provider: str
    model: str
    mode: str


def _rule_based_action(message: str, base: dict[str, str]) -> SuggestedAction:
    normalized = message.lower()
    if "update" in normalized or "firmware" in normalized:
        return SuggestedAction(
            action_type="ota_rollout",
            target_scope="fleet:esp32",
            summary="Prepare staged OTA rollout for ESP32 devices on outdated firmware.",
            requires_approval=True,
            confidence=0.82,
            **base,
        )
    if "restart" in normalized or "reboot" in normalized:
        return SuggestedAction(
            action_type="command",
            target_scope="device:unknown",
            summary="Issue reboot command after explicit device selection.",
            requires_approval=True,
            confidence=0.74,
            **base,
        )
    if "status" in normalized or "health" in normalized or "summary" in normalized:
        return SuggestedAction(
            action_type="query",
            target_scope="fleet:all",
            summary="Retrieve fleet health, firmware distribution, and recent command outcomes.",
            requires_approval=False,
            confidence=0.85,
            **base,
        )
    return SuggestedAction(
        action_type="query",
        target_scope="fleet:all",
        summary="Retrieve current fleet state and telemetry summary before taking action.",
        requires_approval=False,
        confidence=0.68,
        **base,
    )


def infer_action(message: str) -> SuggestedAction:
    provider = get_provider()
    base = {
        "provider": provider.name,
        "model": provider.model,
        "execution_mode": provider.mode,
    }
    provider_result = provider.interpret(message)
    if provider_result:
        try:
            return SuggestedAction(
                action_type=provider_result["action_type"],
                target_scope=provider_result["target_scope"],
                summary=provider_result["summary"],
                requires_approval=bool(provider_result["requires_approval"]),
                confidence=float(provider_result["confidence"]),
                **base,
            )
        except (KeyError, TypeError, ValueError):
            pass
    return _rule_based_action(message, base)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai"}


@app.get("/providers/current", response_model=ProviderStatus)
def current_provider() -> ProviderStatus:
    provider = get_provider()
    return ProviderStatus(provider=provider.name, model=provider.model, mode=provider.mode)


@app.post("/chat", response_model=SuggestedAction)
def chat(payload: ChatRequest) -> SuggestedAction:
    return infer_action(payload.message)


@app.post("/execute")
def execute(payload: ExecuteRequest) -> dict:
    action = infer_action(payload.message)
    return {
        "requested_by": payload.requested_by,
        "approved": not action.requires_approval,
        "suggested_action": action.model_dump(),
        "note": "This endpoint only returns a structured action plan. Backend policy must approve execution.",
    }
