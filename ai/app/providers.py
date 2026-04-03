import os
from abc import ABC, abstractmethod
from json import JSONDecodeError, dumps, loads
from typing import Literal
from urllib.error import URLError
from urllib.request import Request, urlopen


ProviderName = Literal["rule-based", "openai-compatible", "ollama", "llama-cpp"]


def _post_json(url: str, payload: dict, timeout: int = 20) -> dict:
    request = Request(
        url,
        data=dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    return loads(body)


class ModelProvider(ABC):
    def __init__(self, name: ProviderName, model: str, mode: str) -> None:
        self.name = name
        self.model = model
        self.mode = mode

    def metadata(self) -> dict[str, str]:
        return {"provider": self.name, "model": self.model, "mode": self.mode}

    @abstractmethod
    def interpret(self, message: str) -> dict | None:
        raise NotImplementedError


class RuleBasedProvider(ModelProvider):
    def interpret(self, message: str) -> dict | None:
        return None


class OllamaProvider(ModelProvider):
    def __init__(self, model: str, base_url: str) -> None:
        super().__init__(name="ollama", model=model, mode="remote-adapter")
        self.base_url = base_url.rstrip("/")

    def interpret(self, message: str) -> dict | None:
        prompt = (
            "Convert the operator message into JSON with keys "
            "action_type, target_scope, summary, requires_approval, confidence. "
            "Allowed action_type values: command, query, ota_rollout. "
            "Return JSON only.\n"
            f"Message: {message}"
        )
        try:
            payload = _post_json(
                f"{self.base_url}/api/generate",
                {"model": self.model, "prompt": prompt, "stream": False},
            )
            raw = payload.get("response", "").strip()
            return loads(raw) if raw else None
        except (URLError, JSONDecodeError, TimeoutError, ValueError):
            return None


class OpenAICompatibleProvider(ModelProvider):
    def __init__(self, model: str, base_url: str) -> None:
        super().__init__(name="openai-compatible", model=model, mode="remote-adapter")
        self.base_url = base_url.rstrip("/")

    def interpret(self, message: str) -> dict | None:
        prompt = (
            "Return JSON only with keys action_type, target_scope, summary, "
            "requires_approval, confidence for this operator request: "
            f"{message}"
        )
        try:
            payload = _post_json(
                f"{self.base_url}/chat/completions",
                {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
            )
            content = payload["choices"][0]["message"]["content"].strip()
            return loads(content) if content else None
        except (KeyError, URLError, JSONDecodeError, TimeoutError, ValueError):
            return None


class LlamaCppProvider(ModelProvider):
    def __init__(self, model: str, base_url: str) -> None:
        super().__init__(name="llama-cpp", model=model, mode="remote-adapter")
        self.base_url = base_url.rstrip("/")

    def interpret(self, message: str) -> dict | None:
        prompt = (
            "Respond with JSON only using keys action_type, target_scope, summary, "
            "requires_approval, confidence.\n"
            f"Request: {message}"
        )
        try:
            payload = _post_json(
                f"{self.base_url}/completion",
                {"prompt": prompt, "temperature": 0.1},
            )
            content = payload.get("content", "").strip()
            return loads(content) if content else None
        except (URLError, JSONDecodeError, TimeoutError, ValueError):
            return None


def get_provider() -> ModelProvider:
    provider = os.getenv("ROBUST_AI_PROVIDER", "rule-based").strip().lower()
    model = os.getenv("ROBUST_AI_MODEL", "demo-router").strip()
    ollama_base_url = os.getenv("ROBUST_OLLAMA_BASE_URL", "http://localhost:11434")
    openai_base_url = os.getenv("ROBUST_OPENAI_COMPAT_BASE_URL", "http://localhost:8001/v1")
    llama_cpp_base_url = os.getenv("ROBUST_LLAMACPP_BASE_URL", "http://localhost:8080")

    if provider == "ollama":
        return OllamaProvider(model=model, base_url=ollama_base_url)
    if provider == "openai-compatible":
        return OpenAICompatibleProvider(model=model, base_url=openai_base_url)
    if provider == "llama-cpp":
        return LlamaCppProvider(model=model, base_url=llama_cpp_base_url)

    return RuleBasedProvider(name="rule-based", model=model, mode="local-fallback")
