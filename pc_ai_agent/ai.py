from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

DEFAULT_API_BASE = "https://gen.pollinations.ai/v1/chat/completions"
DEFAULT_MODEL = "openai"

SYSTEM_PROMPT = """You are a safe PC assistant. Return only JSON with this schema:
{
  "reply": "short helpful reply in the user's language",
  "actions": [
    {"type": "open_url", "target": "https://example.com"},
    {"type": "open_app", "target": "calculator"},
    {"type": "list_files", "path": "."},
    {"type": "read_file", "path": "notes.txt"},
    {"type": "write_file", "path": "notes.txt", "content": "text"},
    {"type": "run_command", "command": "python --version"}
  ]
}
Rules:
- Never claim an action has already been executed.
- Propose only actions directly requested by the user.
- Prefer safe built-in action types over shell commands.
- Do not propose destructive commands, credential theft, surveillance, malware, persistence, or bypassing security.
- Keep actions empty for general questions.
"""


@dataclass(frozen=True)
class AIPlan:
    reply: str
    actions: list[dict[str, Any]]
    provider: str

    def to_dict(self) -> dict[str, Any]:
        return {"reply": self.reply, "actions": self.actions, "provider": self.provider}


def _extract_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _normalize_plan(data: dict[str, Any], provider: str) -> AIPlan:
    reply = str(data.get("reply") or data.get("message") or "Готово. Проверьте предложенные действия.")
    actions = data.get("actions") or []
    if not isinstance(actions, list):
        actions = []
    safe_actions = [action for action in actions if isinstance(action, dict)]
    return AIPlan(reply=reply, actions=safe_actions, provider=provider)


def ask_public_api(message: str) -> AIPlan:
    api_base = os.environ.get("PCAI_API_BASE", DEFAULT_API_BASE)
    model = os.environ.get("PCAI_MODEL", DEFAULT_MODEL)
    api_key = os.environ.get("POLLINATIONS_API_KEY", "")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(
        api_base,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as response:  # noqa: S310 - configured AI endpoint
        raw = response.read().decode("utf-8", errors="replace")
    parsed = json.loads(raw)
    content = parsed["choices"][0]["message"]["content"]
    return _normalize_plan(_extract_json(content), provider="pollinations")


def fallback_plan(message: str) -> AIPlan:
    text = message.strip()
    lowered = text.lower()
    actions: list[dict[str, Any]] = []

    url_match = re.search(r"https?://[^\s)]+", text)
    if url_match:
        actions.append({"type": "open_url", "target": url_match.group(0)})
    elif any(word in lowered for word in ("список файлов", "покажи файлы", "list files", "ls")):
        actions.append({"type": "list_files", "path": "."})
    elif "python --version" in lowered:
        actions.append({"type": "run_command", "command": "python --version"})
    elif "калькулятор" in lowered or "calculator" in lowered:
        actions.append({"type": "open_app", "target": "calc" if os.name == "nt" else "gnome-calculator"})

    reply = "AI API недоступен, поэтому я подготовил план локальным fallback-парсером."
    if not actions:
        reply += " Не удалось уверенно определить действие — уточните запрос."
    return AIPlan(reply=reply, actions=actions, provider="fallback")


def build_plan(message: str) -> AIPlan:
    try:
        return ask_public_api(message)
    except (OSError, urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError, TimeoutError):
        return fallback_plan(message)
