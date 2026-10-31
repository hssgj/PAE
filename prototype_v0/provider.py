from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from urllib import error, request
from pathlib import Path


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
        max_tokens: int | None = None,
        disable_thinking: bool | None = None,
    ) -> None:
        self.url = url
        self.model = model
        self.api_key = api_key
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.disable_thinking = disable_thinking

    def chat(self, messages: list[dict[str, str]]) -> str:
        payload_data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.8,
            "max_tokens": self.max_tokens if self.max_tokens is not None else int(os.getenv("PAE_MAX_TOKENS", "512")),
        }

        disable_thinking = self.disable_thinking
        if disable_thinking is None:
            disable_thinking = os.getenv("PAE_DISABLE_THINKING", "").strip().lower() in {
                "1", "true", "yes", "on"
            }
        if disable_thinking:
            payload_data["chat_template_kwargs"] = {
                "enable_thinking": False
            }

        payload = json.dumps(payload_data).encode("utf-8")

        headers = {"Content-Type": "application/json", "User-Agent": "PAE/0.1"}
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


def build_provider(*, profile_name: str | None = None, profiles_path: str | Path | None = None) -> Provider:
    if profile_name is not None and not profile_name.strip():
        from model_profiles import ProfileError
        raise ProfileError("An explicitly selected profile cannot be empty")
    selected = profile_name if profile_name is not None else os.getenv("PAE_PROFILE", "").strip()
    if selected:
        from model_profiles import get_profile
        profile = get_profile(selected, profiles_path)
        if profile.provider == "echo":
            provider = EchoProvider()
        else:
            provider = OpenAICompatibleProvider(
                url=profile.url, model=profile.resolve_model(), api_key=profile.resolve_key(),
                max_tokens=profile.max_output_tokens, disable_thinking=profile.disable_thinking,
            )
        provider.profile_id = profile.profile_id
        provider.context_tokens = profile.context_tokens
        return provider

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
