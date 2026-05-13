#!/usr/bin/env python3
from __future__ import annotations

import ctypes
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


class VrLauncherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Universal VR Launcher")
        self.geometry("980x700")

        self.profiles = self._load_profiles()
        self.widgets: dict[str, dict[str, tk.Entry | tk.Text | ttk.Combobox | ttk.Label]] = {}

        self.overlay_visible = False
        self.mouse_hold_rmb = tk.BooleanVar(value=False)
        self.dpi_scale = tk.DoubleVar(value=35.0)
        self.prev_yaw = 0.0
        self.prev_pitch = 0.0

        self._build_ui()
        self.bind_all('<Delete>', self.toggle_overlay)

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
        header = ttk.Frame(self, padding=10)
        header.pack(fill=tk.X)
        ttk.Label(header, text="Профили VR и мыши (Delete = показать/скрыть оверлей)", font=("Segoe UI", 12, "bold")).pack(anchor='w')

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for game_name, profile in self.profiles.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=game_name)
            self.widgets[game_name] = self._build_game_tab(frame, game_name, profile)

        mouse_tab = ttk.Frame(self.notebook)
        self.notebook.add(mouse_tab, text="VR -> Mouse")
        self._build_mouse_tab(mouse_tab)

        actions = ttk.Frame(self, padding=10)
        actions.pack(fill=tk.X)
        ttk.Button(actions, text="💾 Сохранить", command=self.save_all).pack(side=tk.LEFT)
        ttk.Button(actions, text="▶ Запустить выбранную игру", command=self.launch_selected).pack(side=tk.LEFT, padx=8)

    def _build_game_tab(self, parent: ttk.Frame, game_name: str, profile: dict):
        form = ttk.Frame(parent, padding=12)
        form.pack(fill=tk.BOTH, expand=True)
        allowed = ", ".join(GAME_EXECUTABLE_RULES[game_name])
        ttk.Label(form, text=f"Разрешенный файл запуска: {allowed}", foreground="#005a9e").grid(row=0, column=0, columnspan=2, sticky='w')
        ttk.Label(form, text="Путь к .exe:").grid(row=1, column=0, sticky='w', pady=(8,0))
        launch_path = ttk.Entry(form, width=90)
        launch_path.insert(0, profile.get("launch_path", ""))
        launch_path.grid(row=2, column=0, sticky='ew', padx=(0,8))
        ttk.Button(form, text="Выбрать...", command=lambda g=game_name: self.pick_exe(g)).grid(row=2, column=1)
        status = ttk.Label(form, text="", foreground="#666")
        status.grid(row=3, column=0, columnspan=2, sticky='w', pady=(4,10))

        ttk.Label(form, text="OpenXR Runtime").grid(row=4, column=0, sticky='w')
        runtime = ttk.Combobox(form, values=["System Default", "SteamVR", "Oculus", "WMR", "Vive"], state='readonly')
        runtime.set(profile.get("openxr_runtime", "System Default"))
        runtime.grid(row=5, column=0, sticky='w')

        ttk.Label(form, text="Заметки").grid(row=6, column=0, sticky='w', pady=(10,0))
        notes = tk.Text(form, height=7)
        notes.insert('1.0', profile.get("notes", ""))
        notes.grid(row=7, column=0, columnspan=2, sticky='nsew')
        form.columnconfigure(0, weight=1)
        form.rowconfigure(7, weight=1)
        return {"launch_path": launch_path, "status": status, "openxr_runtime": runtime, "notes": notes}

    def _build_mouse_tab(self, parent: ttk.Frame) -> None:
        f = ttk.Frame(parent, padding=14)
        f.pack(fill=tk.BOTH, expand=True)

        card = ttk.LabelFrame(f, text="vR-like mouse look (без инжекта)")
        card.pack(fill=tk.X, pady=4)
        ttk.Checkbutton(card, text="Всегда зажимать правую кнопку мыши", variable=self.mouse_hold_rmb, command=self._apply_rmb_state).pack(anchor='w', padx=10, pady=8)

        ttk.Label(card, text="DPI / чувствительность").pack(anchor='w', padx=10)
        ttk.Scale(card, from_=5.0, to=120.0, variable=self.dpi_scale, orient='horizontal').pack(fill=tk.X, padx=10, pady=(0,8))
        ttk.Label(card, text="Проверка: подвигай ползунки yaw/pitch — скрипт двигает мышь как free-look.").pack(anchor='w', padx=10, pady=(4,10))

        sim = ttk.LabelFrame(f, text="Симуляция входа шлема")
        sim.pack(fill=tk.X, pady=6)
        self.yaw_var = tk.DoubleVar(value=0.0)
        self.pitch_var = tk.DoubleVar(value=0.0)
        ttk.Label(sim, text="Yaw").grid(row=0, column=0, sticky='w', padx=10)
        ttk.Scale(sim, from_=-90, to=90, variable=self.yaw_var, orient='horizontal', command=self._on_head_moved).grid(row=0, column=1, sticky='ew', padx=10)
        ttk.Label(sim, text="Pitch").grid(row=1, column=0, sticky='w', padx=10)
        ttk.Scale(sim, from_=-60, to=60, variable=self.pitch_var, orient='horizontal', command=self._on_head_moved).grid(row=1, column=1, sticky='ew', padx=10, pady=(6,8))
        sim.columnconfigure(1, weight=1)

    def toggle_overlay(self, _event=None):
        self.overlay_visible = not self.overlay_visible
        if self.overlay_visible:
            self.deiconify()
            self.lift()
        else:
            self.withdraw()

    def _mouse_event(self, flags: int, dx: int = 0, dy: int = 0):
        ctypes.windll.user32.mouse_event(flags, dx, dy, 0, 0)

    def _apply_rmb_state(self):
        # 0x0008 right down, 0x0010 right up
        if self.mouse_hold_rmb.get():
            self._mouse_event(0x0008)
        else:
            self._mouse_event(0x0010)

    def _on_head_moved(self, _evt=None):
        yaw = self.yaw_var.get()
        pitch = self.pitch_var.get()
        dpi = self.dpi_scale.get()
        dx = int((yaw - self.prev_yaw) * dpi)
        dy = int((pitch - self.prev_pitch) * dpi)
        self.prev_yaw = yaw
        self.prev_pitch = pitch
        if dx or dy:
            # 0x0001 move
            self._mouse_event(0x0001, dx, dy)

    def _is_allowed_exe(self, game_name: str, path: str) -> bool:
        return Path(path).name.lower() in GAME_EXECUTABLE_RULES[game_name]

    def pick_exe(self, game_name: str) -> None:
        path = filedialog.askopenfilename(title=f"Выбери .exe для {game_name}", filetypes=[("Executable", "*.exe")])
        if not path:
            return
        w = self.widgets[game_name]
        if not self._is_allowed_exe(game_name, path):
            allowed = ', '.join(GAME_EXECUTABLE_RULES[game_name])
            w['status'].configure(text=f"❌ Разрешено только: {allowed}", foreground='#a00000')
            messagebox.showerror("Неверный exe", f"Для {game_name} разрешено только: {allowed}")
            return
        w['launch_path'].delete(0, tk.END)
        w['launch_path'].insert(0, path)
        w['status'].configure(text='✅ Файл принят', foreground='#007a00')

    def save_all(self):
        for game, w in self.widgets.items():
            path = w['launch_path'].get().strip()
            if path and not self._is_allowed_exe(game, path):
                messagebox.showerror('Ошибка', f"{game}: неверный exe")
                return
            self.profiles[game] = {
                'launch_path': path,
                'openxr_runtime': w['openxr_runtime'].get(),
                'notes': w['notes'].get('1.0', tk.END).strip(),
            }
        self._save_profiles()
        messagebox.showinfo('Сохранено', f'Профили сохранены: {CONFIG_PATH}')

    def launch_selected(self):
        game = self.notebook.tab(self.notebook.select(), 'text')
        if game not in self.widgets:
            return
        path = self.widgets[game]['launch_path'].get().strip()
        if not path:
            messagebox.showwarning('Нет файла', 'Сначала выбери exe.')
            return
        if not self._is_allowed_exe(game, path):
            messagebox.showerror('Неверный exe', f'Для {game} неверный exe.')
            return
        try:
            subprocess.Popen([path], shell=False, cwd=str(Path(path).parent))
            messagebox.showinfo('Запуск', f'Запущено: {game}')
        except OSError as exc:
            messagebox.showerror('Ошибка запуска', str(exc))


if __name__ == '__main__':
    app = VrLauncherApp()
    app.mainloop()
