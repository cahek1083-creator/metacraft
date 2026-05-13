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
from tkinter import filedialog, messagebox, ttk

CONFIG_PATH = Path.home() / ".vr_launcher_profiles.json"

GAME_EXECUTABLE_RULES = {
    "Forza Horizon 3": ["forzahorizon3.exe"],
    "Forza Horizon 4": ["forzahorizon4.exe"],
    "Forza Horizon 5": ["forzahorizon5.exe"],
    "Counter-Strike 2": ["cs2.exe"],
}

DEFAULT_GAMES = {
    game: {"launch_path": "", "openxr_runtime": "System Default", "resolution_scale": "1.0", "fov": "90", "notes": ""}
    for game in GAME_EXECUTABLE_RULES
}
DEFAULT_GAMES["Counter-Strike 2"]["notes"] = "No injection. Configure only official launch options."


class VrLauncherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Universal VR Launcher (Profiles)")
        self.geometry("960x650")

        self.profiles = self._load_profiles()
        self.widgets: dict[str, dict[str, tk.Entry | tk.Text | ttk.Combobox | ttk.Label]] = {}

        self._build_ui()

    def _load_profiles(self) -> dict:
        if CONFIG_PATH.exists():
            try:
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                for game, defaults in DEFAULT_GAMES.items():
                    data.setdefault(game, defaults.copy())
                return data
            except json.JSONDecodeError:
                pass
        return {k: v.copy() for k, v in DEFAULT_GAMES.items()}

    def _save_profiles(self) -> None:
        CONFIG_PATH.write_text(json.dumps(self.profiles, indent=2, ensure_ascii=False), encoding="utf-8")

    def _build_ui(self) -> None:
        top = ttk.Frame(self, padding=10)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Профили запуска VR (без инжекта). Выбирай exe через Проводник.", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for game_name, profile in self.profiles.items():
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=game_name)
            self.widgets[game_name] = self._build_game_tab(frame, game_name, profile)

        actions = ttk.Frame(self, padding=10)
        actions.pack(fill=tk.X)

        ttk.Button(actions, text="💾 Сохранить профили", command=self.save_all).pack(side=tk.LEFT)
        ttk.Button(actions, text="▶ Запустить выбранную игру", command=lambda: self.launch_selected(notebook)).pack(side=tk.LEFT, padx=8)

    def _build_game_tab(self, parent: ttk.Frame, game_name: str, profile: dict):
        form = ttk.Frame(parent, padding=12)
        form.pack(fill=tk.BOTH, expand=True)

        allowed = ", ".join(GAME_EXECUTABLE_RULES[game_name])

        ttk.Label(form, text=f"Разрешенный файл запуска: {allowed}", foreground="#005a9e").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Путь к .exe:").grid(row=1, column=0, sticky="w")
        launch_path = ttk.Entry(form, width=90)
        launch_path.insert(0, profile.get("launch_path", profile.get("launch_cmd", "")))
        launch_path.grid(row=2, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(form, text="Выбрать...", command=lambda g=game_name: self.pick_exe(g)).grid(row=2, column=1, sticky="ew")

        status = ttk.Label(form, text="", foreground="#666")
        status.grid(row=3, column=0, columnspan=2, sticky="w", pady=(4, 12))

        ttk.Label(form, text="OpenXR Runtime:").grid(row=4, column=0, sticky="w")
        runtime = ttk.Combobox(form, values=["System Default", "SteamVR", "Oculus", "WMR", "Vive"], state="readonly")
        runtime.set(profile.get("openxr_runtime", "System Default"))
        runtime.grid(row=5, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Resolution Scale (например 1.0):").grid(row=6, column=0, sticky="w")
        resolution = ttk.Entry(form, width=20)
        resolution.insert(0, profile.get("resolution_scale", "1.0"))
        resolution.grid(row=7, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Target FOV:").grid(row=8, column=0, sticky="w")
        fov = ttk.Entry(form, width=20)
        fov.insert(0, profile.get("fov", "90"))
        fov.grid(row=9, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Заметки:").grid(row=10, column=0, sticky="w")
        notes = tk.Text(form, height=8)
        notes.insert("1.0", profile.get("notes", ""))
        notes.grid(row=11, column=0, columnspan=2, sticky="nsew")

        form.columnconfigure(0, weight=1)
        form.rowconfigure(11, weight=1)

        return {
            "launch_path": launch_path,
            "status": status,
            "openxr_runtime": runtime,
            "resolution_scale": resolution,
            "fov": fov,
            "notes": notes,
        }

    def _is_allowed_exe(self, game_name: str, path: str) -> bool:
        if not path:
            return False
        filename = Path(path).name.lower()
        return filename in GAME_EXECUTABLE_RULES[game_name]

    def pick_exe(self, game_name: str) -> None:
        path = filedialog.askopenfilename(
            title=f"Выбери .exe для {game_name}",
            filetypes=[("Executable", "*.exe")],
        )
        if not path:
            return

        widgets = self.widgets[game_name]
        if not self._is_allowed_exe(game_name, path):
            allowed = ", ".join(GAME_EXECUTABLE_RULES[game_name])
            widgets["status"].configure(text=f"❌ Неверный файл. Разрешено только: {allowed}", foreground="#a00000")
            messagebox.showerror("Неверный exe", f"Для {game_name} разрешено только: {allowed}")
            return

        widgets["launch_path"].delete(0, tk.END)
        widgets["launch_path"].insert(0, path)
        widgets["status"].configure(text="✅ Файл принят", foreground="#007a00")

    def save_all(self) -> None:
        for game_name, w in self.widgets.items():
            path = w["launch_path"].get().strip()
            if path and not self._is_allowed_exe(game_name, path):
                allowed = ", ".join(GAME_EXECUTABLE_RULES[game_name])
                messagebox.showerror("Ошибка", f"{game_name}: разрешено только {allowed}")
                return

            self.profiles[game_name] = {
                "launch_path": path,
                "openxr_runtime": w["openxr_runtime"].get(),
                "resolution_scale": w["resolution_scale"].get(),
                "fov": w["fov"].get(),
                "notes": w["notes"].get("1.0", tk.END).strip(),
            }

        self._save_profiles()
        messagebox.showinfo("Сохранено", f"Профили сохранены: {CONFIG_PATH}")

    def launch_selected(self, notebook: ttk.Notebook) -> None:
        tab_id = notebook.select()
        game_name = notebook.tab(tab_id, "text")
        path = self.widgets[game_name]["launch_path"].get().strip()
        if not path:
            messagebox.showwarning("Нет файла", "Сначала выбери exe через кнопку 'Выбрать...'.")
            return
        if not self._is_allowed_exe(game_name, path):
            allowed = ", ".join(GAME_EXECUTABLE_RULES[game_name])
            messagebox.showerror("Неверный exe", f"Для {game_name} разрешено только: {allowed}")
            return

        try:
            subprocess.Popen([path], shell=False)
            messagebox.showinfo("Запуск", f"Запущено: {game_name}")
        except OSError as exc:
            messagebox.showerror("Ошибка запуска", str(exc))


if __name__ == "__main__":
    app = VrLauncherApp()
    app.mainloop()
