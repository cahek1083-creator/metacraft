from __future__ import annotations

import json
import os
import platform
import shlex
import subprocess
import sys
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ActionError(ValueError):
    """Raised when an action is invalid or blocked."""


DANGEROUS_COMMAND_PATTERNS = (
    "rm -rf",
    "rmdir /s",
    "del /f",
    "format ",
    "mkfs",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    ":(){",
    "chmod -r 777 /",
    "chown -r",
    "dd if=",
    "> /dev/",
    "curl | sh",
    "wget | sh",
)

TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".csv",
    ".log",
    ".py",
    ".js",
    ".ts",
    ".html",
    ".css",
}


@dataclass(frozen=True)
class ActionResult:
    ok: bool
    message: str
    data: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "message": self.message, "data": self.data}


def normalize_action(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ActionError("Action must be a JSON object")
    action_type = str(raw.get("type", "")).strip().lower()
    if not action_type:
        raise ActionError("Action type is required")
    return {**raw, "type": action_type}


def workspace_root() -> Path:
    return Path(os.environ.get("PCAI_WORKSPACE", os.getcwd())).expanduser().resolve()


def resolve_inside_workspace(path_value: str | os.PathLike[str]) -> Path:
    root = workspace_root()
    candidate = (root / Path(path_value).expanduser()).resolve() if not Path(path_value).is_absolute() else Path(path_value).expanduser().resolve()
    if root != candidate and root not in candidate.parents:
        raise ActionError(f"Path is outside workspace: {candidate}")
    return candidate


def is_dangerous_command(command: str) -> bool:
    normalized = " ".join(command.lower().split())
    return any(pattern in normalized for pattern in DANGEROUS_COMMAND_PATTERNS)


def open_target(target: str) -> ActionResult:
    if not target:
        raise ActionError("Target is required")
    if target.startswith(("http://", "https://")):
        webbrowser.open(target)
        return ActionResult(True, f"Opened URL: {target}")

    path = Path(target).expanduser()
    if path.exists():
        if sys.platform.startswith("darwin"):
            subprocess.Popen(["open", str(path)])
        elif os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return ActionResult(True, f"Opened path: {path}")

    executable = target if os.name == "nt" else shlex.split(target)
    subprocess.Popen(executable)  # noqa: S603 - explicit user-approved action
    return ActionResult(True, f"Started application: {target}")


def list_files(path_value: str = ".") -> ActionResult:
    path = resolve_inside_workspace(path_value)
    if not path.exists():
        raise ActionError(f"Directory does not exist: {path}")
    if not path.is_dir():
        raise ActionError(f"Not a directory: {path}")
    entries = sorted(
        {"name": entry.name, "type": "dir" if entry.is_dir() else "file"}
        for entry in path.iterdir()
    )
    return ActionResult(True, f"Listed {len(entries)} entries in {path}", entries)


def read_text_file(path_value: str, max_bytes: int = 32_000) -> ActionResult:
    path = resolve_inside_workspace(path_value)
    if not path.exists() or not path.is_file():
        raise ActionError(f"File does not exist: {path}")
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        raise ActionError(f"Refusing to read non-text extension: {path.suffix}")
    data = path.read_bytes()[:max_bytes]
    text = data.decode("utf-8", errors="replace")
    return ActionResult(True, f"Read {len(data)} bytes from {path}", text)


def write_text_file(path_value: str, content: str) -> ActionResult:
    path = resolve_inside_workspace(path_value)
    if path.suffix.lower() and path.suffix.lower() not in TEXT_EXTENSIONS:
        raise ActionError(f"Refusing to write non-text extension: {path.suffix}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return ActionResult(True, f"Wrote {len(content)} characters to {path}")


def run_command(command: str, timeout: int = 30) -> ActionResult:
    if not command:
        raise ActionError("Command is required")
    if is_dangerous_command(command):
        raise ActionError("Command was blocked because it looks dangerous")
    completed = subprocess.run(
        command,
        shell=True,
        cwd=workspace_root(),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return ActionResult(
        completed.returncode == 0,
        f"Command exited with code {completed.returncode}",
        {"stdout": completed.stdout[-8000:], "stderr": completed.stderr[-8000:]},
    )


def execute_action(raw: dict[str, Any]) -> ActionResult:
    action = normalize_action(raw)
    action_type = action["type"]

    if action_type in {"open_url", "open_app", "open_path", "open"}:
        return open_target(str(action.get("target") or action.get("url") or action.get("path") or ""))
    if action_type == "list_files":
        return list_files(str(action.get("path") or "."))
    if action_type == "read_file":
        return read_text_file(str(action.get("path") or ""))
    if action_type in {"write_file", "create_file"}:
        return write_text_file(str(action.get("path") or ""), str(action.get("content") or ""))
    if action_type == "run_command":
        return run_command(str(action.get("command") or ""), int(action.get("timeout") or 30))
    raise ActionError(f"Unsupported action type: {action_type}")


def action_preview(raw: dict[str, Any]) -> str:
    action = normalize_action(raw)
    compact = json.dumps(action, ensure_ascii=False, sort_keys=True)
    os_name = platform.system() or os.name
    return f"{os_name}: {compact}"
