#!/usr/bin/env python3
"""Multi-game VR profile manager (safe launcher UI).

This app does NOT inject into game processes.
It manages per-game VR settings and can start games via shell commands
that user explicitly configures.
"""

from __future__ import annotations

import json
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

CONFIG_PATH = Path.home() / ".vr_launcher_profiles.json"

DEFAULT_GAMES = {
    "Forza Horizon 3": {"launch_cmd": "", "openxr_runtime": "System Default", "resolution_scale": "1.0", "fov": "90", "notes": ""},
    "Forza Horizon 4": {"launch_cmd": "", "openxr_runtime": "System Default", "resolution_scale": "1.0", "fov": "90", "notes": ""},
    "Forza Horizon 5": {"launch_cmd": "", "openxr_runtime": "System Default", "resolution_scale": "1.0", "fov": "90", "notes": ""},
    "Counter-Strike 2": {"launch_cmd": "", "openxr_runtime": "System Default", "resolution_scale": "1.0", "fov": "90", "notes": "No injection. Configure only official launch options."},
}


class VrLauncherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Universal VR Launcher (Profiles)")
        self.geometry("900x600")

        self.profiles = self._load_profiles()
        self.widgets: dict[str, dict[str, tk.Entry | tk.Text | ttk.Combobox]] = {}

        self._build_ui()

    def _load_profiles(self) -> dict:
        if CONFIG_PATH.exists():
            try:
                return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return DEFAULT_GAMES.copy()

    def _save_profiles(self) -> None:
        CONFIG_PATH.write_text(json.dumps(self.profiles, indent=2, ensure_ascii=False), encoding="utf-8")

    def _build_ui(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=8)

        ttk.Label(top, text="Safe VR profile launcher. No process injection included.").pack(side=tk.LEFT)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for game_name, profile in self.profiles.items():
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=game_name)
            self.widgets[game_name] = self._build_game_tab(frame, game_name, profile)

        actions = ttk.Frame(self)
        actions.pack(fill=tk.X, padx=10, pady=8)

        ttk.Button(actions, text="Save Profiles", command=self.save_all).pack(side=tk.LEFT)
        ttk.Button(actions, text="Launch Selected Game", command=lambda: self.launch_selected(notebook)).pack(side=tk.LEFT, padx=6)

    def _build_game_tab(self, parent: ttk.Frame, game_name: str, profile: dict) -> dict[str, tk.Entry | tk.Text | ttk.Combobox]:
        form = ttk.Frame(parent)
        form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(form, text="Launch Command (Steam URI or executable path):").grid(row=0, column=0, sticky="w")
        launch_cmd = ttk.Entry(form, width=100)
        launch_cmd.insert(0, profile.get("launch_cmd", ""))
        launch_cmd.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="OpenXR Runtime:").grid(row=2, column=0, sticky="w")
        runtime = ttk.Combobox(form, values=["System Default", "SteamVR", "Oculus", "WMR", "Vive"], state="readonly")
        runtime.set(profile.get("openxr_runtime", "System Default"))
        runtime.grid(row=3, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Resolution Scale (e.g. 1.0):").grid(row=4, column=0, sticky="w")
        resolution = ttk.Entry(form, width=20)
        resolution.insert(0, profile.get("resolution_scale", "1.0"))
        resolution.grid(row=5, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Target FOV:").grid(row=6, column=0, sticky="w")
        fov = ttk.Entry(form, width=20)
        fov.insert(0, profile.get("fov", "90"))
        fov.grid(row=7, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Notes:").grid(row=8, column=0, sticky="w")
        notes = tk.Text(form, height=8)
        notes.insert("1.0", profile.get("notes", ""))
        notes.grid(row=9, column=0, sticky="nsew")

        form.columnconfigure(0, weight=1)
        form.rowconfigure(9, weight=1)

        return {
            "launch_cmd": launch_cmd,
            "openxr_runtime": runtime,
            "resolution_scale": resolution,
            "fov": fov,
            "notes": notes,
        }

    def save_all(self) -> None:
        for game_name, w in self.widgets.items():
            self.profiles[game_name] = {
                "launch_cmd": w["launch_cmd"].get(),
                "openxr_runtime": w["openxr_runtime"].get(),
                "resolution_scale": w["resolution_scale"].get(),
                "fov": w["fov"].get(),
                "notes": w["notes"].get("1.0", tk.END).strip(),
            }

        self._save_profiles()
        messagebox.showinfo("Saved", f"Profiles saved to {CONFIG_PATH}")

    def launch_selected(self, notebook: ttk.Notebook) -> None:
        tab_id = notebook.select()
        game_name = notebook.tab(tab_id, "text")
        cmd = self.widgets[game_name]["launch_cmd"].get().strip()
        if not cmd:
            messagebox.showwarning("Missing command", "Set Launch Command first.")
            return

        try:
            subprocess.Popen(cmd, shell=True)
            messagebox.showinfo("Launched", f"Started: {game_name}")
        except OSError as exc:
            messagebox.showerror("Launch error", str(exc))


if __name__ == "__main__":
    app = VrLauncherApp()
    app.mainloop()
