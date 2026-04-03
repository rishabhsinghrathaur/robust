import os
from typing import Literal


ProviderName = Literal["rule-based", "openai-compatible", "ollama", "llama-cpp"]


class ModelProvider:
    def __init__(self, name: ProviderName, model: str, mode: str) -> None:
        self.name = name
        self.model = model
        self.mode = mode

    def metadata(self) -> dict[str, str]:
        return {"provider": self.name, "model": self.model, "mode": self.mode}


def get_provider() -> ModelProvider:
    provider = os.getenv("ROBUST_AI_PROVIDER", "rule-based").strip().lower()
    model = os.getenv("ROBUST_AI_MODEL", "demo-router").strip()

    if provider in {"ollama", "llama-cpp", "openai-compatible"}:
        return ModelProvider(name=provider, model=model, mode="adapter-ready")

    return ModelProvider(name="rule-based", model=model, mode="local-fallback")

