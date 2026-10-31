"""Small OpenAI-compatible Chat Completions adapter with no framework dependency."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request


class ChatClient:
    def __init__(self, settings: dict):
        allowed = {"base_url_env", "api_key_env", "model_env", "auth_header", "strict_tools", "timeout_seconds", "max_retries", "max_output_tokens", "token_parameter", "temperature", "max_total_tokens"}
        if set(settings) - allowed:
            raise ValueError(f"Unknown llm settings: {sorted(set(settings) - allowed)}. Credentials must come from environment variables.")
        self.base_url = os.environ.get(settings.get("base_url_env", "AGENT1_BASE_URL"), "").rstrip("/")
        self.api_key = os.environ.get(settings.get("api_key_env", "AGENT1_API_KEY"), "")
        self.model = os.environ.get(settings.get("model_env", "AGENT1_MODEL"), "")
        if not all((self.base_url, self.api_key, self.model)):
            raise ValueError("LLM mode requires AGENT1_BASE_URL, AGENT1_API_KEY and AGENT1_MODEL (or configured environment variable names)")
        parsed = urllib.parse.urlparse(self.base_url)
        if parsed.scheme != "https" and not (parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1"}):
            raise ValueError("Use an HTTPS model endpoint; HTTP is allowed only for localhost testing")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("base_url must not contain credentials, a query or a fragment")
        self.settings = settings
        self.total_tokens = 0

    def complete(self, messages: list[dict], tools: list[dict]) -> dict:
        budget = self.settings.get("max_total_tokens", 60000)
        if self.total_tokens >= budget:
            raise RuntimeError("Reported LLM token budget exhausted")
        body = {"model": self.model, "messages": messages, "tools": tools, "tool_choice": "auto"}
        token_parameter = self.settings.get("token_parameter", "max_tokens")
        if token_parameter not in {"max_tokens", "max_completion_tokens"}:
            raise ValueError("token_parameter must be max_tokens or max_completion_tokens")
        body[token_parameter] = min(self.settings.get("max_output_tokens", 3000), budget - self.total_tokens)
        if self.settings.get("temperature") is not None:
            body["temperature"] = self.settings["temperature"]
        header = self.settings.get("auth_header", "Authorization")
        if header not in {"Authorization", "api-key"}:
            raise ValueError("auth_header must be Authorization or api-key")
        headers = {"Content-Type": "application/json", header: "Bearer " + self.api_key if header == "Authorization" else self.api_key}
        request = urllib.request.Request(self.base_url + "/chat/completions", data=json.dumps(body, ensure_ascii=False).encode("utf-8"), headers=headers, method="POST")
        retries = min(max(int(self.settings.get("max_retries", 2)), 0), 3)
        for attempt in range(retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.settings.get("timeout_seconds", 60)) as response:
                    result = json.loads(response.read().decode("utf-8"))
                if not result.get("choices") or "message" not in result["choices"][0]:
                    raise RuntimeError("Endpoint returned no assistant message")
                usage = result.get("usage") or {}
                # Providers omitting usage cannot satisfy an exact token budget; turn/tool limits still apply.
                self.total_tokens += int(usage.get("total_tokens") or 0)
                return {"message": result["choices"][0]["message"], "usage": usage,
                        "usage_reported": "total_tokens" in usage}
            except urllib.error.HTTPError as error:
                if error.code in {429, 500, 502, 503, 504} and attempt < retries:
                    time.sleep(min(2 ** attempt, 4))
                    continue
                # Do not surface response bodies or headers that could echo credentials.
                raise RuntimeError(f"Model endpoint HTTP {error.code}; verify endpoint, model, tool support, authentication and quota") from None
            except urllib.error.URLError:
                if attempt < retries:
                    time.sleep(min(2 ** attempt, 4))
                    continue
                raise RuntimeError("Model endpoint connection failed; no silent offline substitution was made") from None
        raise RuntimeError("Model request failed")
