"""LLM access for the three research agents.

Supports any OpenAI-compatible chat endpoint (DeepSeek, vLLM, OpenAI, ...) and
Anthropic's Messages API.  When no key is configured the agents fall back to a
rule-based researcher so the whole pipeline stays runnable offline.
"""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Optional

import requests

from ..config import LLMSettings


class LLMError(RuntimeError):
    pass


def parse_json(text: str) -> Any:
    """Best-effort JSON extraction from a model reply."""
    if text is None:
        raise LLMError("empty reply")
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.S)
    if fence:
        text = fence.group(1).strip()
    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        if start < 0:
            continue
        try:
            obj, _ = json.JSONDecoder().raw_decode(text[start:])
            return obj
        except json.JSONDecodeError:
            end = text.rfind(closer)
            if end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    pass
    raise LLMError(f"could not parse JSON from reply: {text[:300]!r}")


class LLMClient:
    name = "base"

    def __init__(self, settings: LLMSettings):
        self.settings = settings

    @property
    def available(self) -> bool:
        return False

    def complete(self, system: str, user: str, json_mode: bool = False) -> str:
        raise LLMError("no LLM configured")

    def complete_json(
        self, system: str, user: str, retries: int = 2
    ) -> Any:
        last: Optional[Exception] = None
        for attempt in range(retries + 1):
            try:
                text = self.complete(system, user, json_mode=True)
                return parse_json(text)
            except (LLMError, json.JSONDecodeError, requests.RequestException) as exc:
                last = exc
                if attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
        raise LLMError(f"LLM did not return usable JSON: {last}")


class OfflineClient(LLMClient):
    name = "offline"

    @property
    def available(self) -> bool:
        return False

    def complete(self, system: str, user: str, json_mode: bool = False) -> str:
        raise LLMError("offline mode: no LLM key configured")


class OpenAICompatibleClient(LLMClient):
    name = "openai-compatible"

    def __init__(self, settings: LLMSettings):
        super().__init__(settings)
        self._key = os.getenv(settings.api_key_env, "") if settings.api_key_env else ""
        self.base = settings.base_url.rstrip("/")
        if not self.base.endswith("/v1"):
            self.base = self.base + "/v1"
        self.url = f"{self.base}/chat/completions"

    @property
    def available(self) -> bool:
        return bool(self._key)

    def complete(self, system: str, user: str, json_mode: bool = False) -> str:
        if not self.available:
            raise LLMError(f"missing API key ({self.settings.api_key_env})")
        payload = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
        }
        resp = requests.post(
            self.url, json=payload, headers=headers, timeout=self.settings.timeout
        )
        if resp.status_code == 400 and json_mode:
            payload.pop("response_format", None)
            resp = requests.post(
                self.url, json=payload, headers=headers, timeout=self.settings.timeout
            )
        if resp.status_code >= 400:
            raise LLMError(f"LLM HTTP {resp.status_code}: {resp.text[:400]}")
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise LLMError(f"unexpected LLM payload: {str(data)[:400]}") from exc


class AnthropicClient(LLMClient):
    name = "anthropic"

    def __init__(self, settings: LLMSettings):
        super().__init__(settings)
        self._key = os.getenv(settings.api_key_env, "") if settings.api_key_env else ""
        self.base = (settings.base_url or "https://api.anthropic.com").rstrip("/")
        self.url = f"{self.base}/v1/messages"

    @property
    def available(self) -> bool:
        return bool(self._key)

    def complete(self, system: str, user: str, json_mode: bool = False) -> str:
        if not self.available:
            raise LLMError(f"missing API key ({self.settings.api_key_env})")
        payload = {
            "model": self.settings.model,
            "max_tokens": self.settings.max_tokens,
            "temperature": self.settings.temperature,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        headers = {
            "x-api-key": self._key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        resp = requests.post(
            self.url, json=payload, headers=headers, timeout=self.settings.timeout
        )
        if resp.status_code >= 400:
            raise LLMError(f"LLM HTTP {resp.status_code}: {resp.text[:400]}")
        data = resp.json()
        try:
            blocks = data["content"]
            return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        except (KeyError, TypeError) as exc:
            raise LLMError(f"unexpected Anthropic payload: {str(data)[:400]}") from exc


def build_client(settings: Optional[LLMSettings] = None) -> LLMClient:
    settings = settings or LLMSettings.from_env()
    if settings.provider == "openai":
        return OpenAICompatibleClient(settings)
    if settings.provider == "anthropic":
        return AnthropicClient(settings)
    return OfflineClient(settings)
