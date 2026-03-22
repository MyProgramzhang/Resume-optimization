from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.core.config import settings


class LlmClient:
    def __init__(self) -> None:
        self.base_url = settings.model_base_url.rstrip("/")
        self.api_key = settings.model_api_key
        self.model_name = settings.model_name
        self.use_mock = settings.use_mock_llm

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if self.use_mock or not self.api_key:
            return self._mock_response(user_prompt)

        payload = {
            "model": self.model_name,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        if settings.model_thinking_type:
            payload["thinking"] = {"type": settings.model_thinking_type}
        if settings.model_enable_thinking is not None:
            payload["enable_thinking"] = settings.model_enable_thinking
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=settings.job_timeout_seconds) as client:
            response = client.post(self._chat_completions_url(), headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = self._extract_content(data)
        return self._parse_json_content(content)

    @staticmethod
    def _mock_response(user_prompt: str) -> dict[str, Any]:
        return {"mock": True, "source": user_prompt}

    def _chat_completions_url(self) -> str:
        if self.base_url.endswith("/chat/completions"):
            return self.base_url
        return f"{self.base_url}/chat/completions"

    @staticmethod
    def _extract_content(response_data: dict[str, Any]) -> str:
        content = response_data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(item.get("text", ""))
            return "\n".join(parts)
        return str(content)

    @staticmethod
    def _parse_json_content(content: str) -> dict[str, Any]:
        content = content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, re.DOTALL)
            if fenced:
                return json.loads(fenced.group(1))
            inline = re.search(r"(\{.*\})", content, re.DOTALL)
            if inline:
                return json.loads(inline.group(1))
            raise ValueError("Model response was not valid JSON.")
