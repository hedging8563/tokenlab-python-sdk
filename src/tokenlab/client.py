from __future__ import annotations

import os
from typing import Any, Mapping

import httpx

TOKENLAB_API_BASE = "https://api.tokenlab.sh"
TOKENLAB_OPENAI_BASE_URL = f"{TOKENLAB_API_BASE}/v1"


class TokenLabClient:
    """Small synchronous TokenLab client for discovery and native endpoints."""

    def __init__(
        self,
        api_key: str | None = None,
        api_base: str = TOKENLAB_API_BASE,
        timeout: float = 60.0,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("TOKENLAB_API_KEY", "")
        self.api_base = api_base.rstrip("/")
        self.openai_base_url = f"{self.api_base}/v1"
        self._headers = dict(headers or {})
        self._client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "TokenLabClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
    ) -> Any:
        request_headers = {
            "Content-Type": "application/json",
            **self._headers,
            **dict(headers or {}),
        }

        if self.api_key and "Authorization" not in request_headers and "x-goog-api-key" not in request_headers:
            request_headers["Authorization"] = f"Bearer {self.api_key}"

        response = self._client.request(
            method,
            f"{self.api_base}{path}",
            json=json,
            headers=request_headers,
            params=params,
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"TokenLab request failed: {response.text}") from exc
        return response.json() if response.content else None

    def list_models(self, **query: str) -> Any:
        return self.request("GET", "/v1/models", params={k: v for k, v in query.items() if v is not None})

    def get_model(self, model: str) -> Any:
        return self.request("GET", f"/v1/models/{model}")

    def get_model_pricing(self, model: str) -> Any:
        return self.request("GET", f"/v1/models/{model}/pricing")

    def list_pricing(self, **query: str) -> Any:
        return self.request("GET", "/v1/pricing", params={k: v for k, v in query.items() if v is not None})

    def get_models_json(self) -> Any:
        return self.request("GET", "/models.json")

    def get_pricing_json(self) -> Any:
        return self.request("GET", "/pricing.json")

    def get_integrations_json(self) -> Any:
        return self.request("GET", "/integrations.json")

    def create_chat_completion(self, body: Mapping[str, Any]) -> Any:
        return self.request("POST", "/v1/chat/completions", json=dict(body))

    def create_response(self, body: Mapping[str, Any]) -> Any:
        return self.request("POST", "/v1/responses", json=dict(body))

    def evaluate_decisions(self, body: Mapping[str, Any]) -> Any:
        return self.request("POST", "/v1/systemone", json=dict(body))

    def create_anthropic_message(self, body: Mapping[str, Any]) -> Any:
        return self.request("POST", "/v1/messages", json=dict(body))

    def create_gemini_content(self, model: str, body: Mapping[str, Any]) -> Any:
        return self.request(
            "POST",
            f"/v1beta/models/{model}:generateContent",
            json=dict(body),
            headers={"x-goog-api-key": self.api_key},
        )
