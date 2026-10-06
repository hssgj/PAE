from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from urllib import error, request


def _coerce_text_content(content) -> str | None:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if not isinstance(item, dict):
                continue

            item_type = item.get("type")
            text = item.get("text")
            if item_type in {"text", "output_text"} and isinstance(text, str):
                parts.append(text)

        if parts:
            return "".join(parts)

    return None


class Provider(ABC):
    name = "provider"

    @abstractmethod
    def chat(self, messages: list[dict[str, str]]) -> str:
        raise NotImplementedError


class EchoProvider(Provider):
    """Zero-dependency smoke-test provider."""

    name = "echo"

    def chat(self, messages: list[dict[str, str]]) -> str:
        last_user = next(
            (item["content"] for item in reversed(messages) if item["role"] == "user"),
            "",
        )
        return f"[echo] {last_user}"


class OpenAICompatibleProvider(Provider):
    """Works with servers exposing POST /v1/chat/completions."""

    name = "openai-compatible"

    def __init__(
        self,
        *,
        url: str,
        model: str,
        api_key: str = "",
        timeout: int = 120,
    ) -> None:
        self.url = url
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def chat(self, messages: list[dict[str, str]]) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
            }
        ).encode("utf-8")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = request.Request(
            self.url,
            data=payload,
            headers=headers,
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"provider HTTP {exc.code}: {detail}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(f"provider connection failed: {exc}") from exc

        data = json.loads(body)

        try:
            choice = data["choices"][0]
            message = choice["message"]
            content = message.get("content")
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"unexpected provider response shape: {type(data).__name__}"
            ) from exc

        text = _coerce_text_content(content)

        if text is None:
            refusal = message.get("refusal")
            if isinstance(refusal, str) and refusal.strip():
                text = refusal

        if text is None:
            model_id = data.get("model", "UNKNOWN")
            finish_reason = choice.get("finish_reason", "UNKNOWN")
            keys = sorted(message.keys()) if isinstance(message, dict) else []
            raise RuntimeError(
                "provider returned non-text content "
                f"(model={model_id!r}, finish_reason={finish_reason!r}, "
                f"message_keys={keys})"
            )

        return text.strip()


def build_provider() -> Provider:
    provider_name = os.getenv("PAE_PROVIDER", "echo").strip().lower()

    if provider_name == "echo":
        return EchoProvider()

    if provider_name in {"openai", "openai_compatible", "openai-compatible"}:
        url = os.getenv(
            "PAE_API_URL",
            "http://127.0.0.1:1234/v1/chat/completions",
        )
        model = os.getenv("PAE_MODEL", "").strip()
        api_key = os.getenv("PAE_API_KEY", "").strip()

        if not model:
            raise RuntimeError(
                "PAE_MODEL is required when PAE_PROVIDER=openai-compatible"
            )

        return OpenAICompatibleProvider(
            url=url,
            model=model,
            api_key=api_key,
        )

    raise RuntimeError(
        f"unknown PAE_PROVIDER={provider_name!r}; "
        "use 'echo' or 'openai-compatible'"
    )
