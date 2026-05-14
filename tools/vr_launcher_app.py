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
DEFAULT_GAMES = {g: {"launch_path": "", "openxr_runtime": "System Default", "notes": ""} for g in GAME_EXECUTABLE_RULES}


class VrLauncherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Universal VR Launcher")
        self.geometry("980x700")
        self.configure(bg="#0f1115")

        self.style = ttk.Style(self)
        if "vista" in self.style.theme_names():
            self.style.theme_use("vista")
        self.style.configure("Card.TLabelframe", background="#151922")
        self.style.configure("Card.TLabelframe.Label", foreground="#70b7ff")

        self.profiles = self._load_profiles()
        self.widgets: dict[str, dict[str, tk.Entry | tk.Text | ttk.Combobox | ttk.Label]] = {}

        self.mouse_hold_rmb = tk.BooleanVar(value=False)
        self.dpi_scale = tk.DoubleVar(value=35.0)
        self.prev_yaw = 0.0
        self.prev_pitch = 0.0
        self._delete_prev_down = False

        self.dim_window: tk.Toplevel | None = None
        self.overlay_window: tk.Toplevel | None = None

        self._build_ui()
        self.after(30, self._poll_delete_hotkey)

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
        header = tk.Frame(self, bg="#0f1115")
        header.pack(fill=tk.X, padx=12, pady=(12, 8))
        tk.Label(header, text="Universal VR Launcher", fg="#ffffff", bg="#0f1115", font=("Segoe UI", 18, "bold")).pack(anchor='w')
        tk.Label(header, text="Delete — оверлей | красивый UI + проверка exe + VR->Mouse", fg="#8fa3bf", bg="#0f1115", font=("Segoe UI", 10)).pack(anchor='w')

        shell = tk.Frame(self, bg="#0f1115")
        shell.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        self.notebook = ttk.Notebook(shell)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        for game_name, profile in self.profiles.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=game_name)
            self.widgets[game_name] = self._build_game_tab(frame, game_name, profile)

        mouse_tab = ttk.Frame(self.notebook)
        self.notebook.add(mouse_tab, text="VR -> Mouse")
        self._build_mouse_tab(mouse_tab)

        footer = tk.Frame(self, bg="#0f1115")
        footer.pack(fill=tk.X, padx=12, pady=(0, 12))
        ttk.Button(footer, text="💾 Сохранить", command=self.save_all).pack(side=tk.LEFT)
        ttk.Button(footer, text="▶ Запустить выбранную игру", command=self.launch_selected).pack(side=tk.LEFT, padx=8)

    def _build_game_tab(self, parent: ttk.Frame, game_name: str, profile: dict):
        form = ttk.LabelFrame(parent, text=f"Профиль: {game_name}", style="Card.TLabelframe", padding=12)
        form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        allowed = ", ".join(GAME_EXECUTABLE_RULES[game_name])
        ttk.Label(form, text=f"Разрешенный файл запуска: {allowed}").grid(row=0, column=0, columnspan=2, sticky='w')
        ttk.Label(form, text="Путь к .exe").grid(row=1, column=0, sticky='w', pady=(10, 0))
        launch_path = ttk.Entry(form, width=90)
        launch_path.insert(0, profile.get("launch_path", ""))
        launch_path.grid(row=2, column=0, sticky='ew', padx=(0, 8))
        ttk.Button(form, text="Выбрать...", command=lambda g=game_name: self.pick_exe(g)).grid(row=2, column=1)
        status = ttk.Label(form, text="")
        status.grid(row=3, column=0, columnspan=2, sticky='w', pady=(4, 10))
        ttk.Label(form, text="OpenXR Runtime").grid(row=4, column=0, sticky='w')
        runtime = ttk.Combobox(form, values=["System Default", "SteamVR", "Oculus", "WMR", "Vive"], state='readonly')
        runtime.set(profile.get("openxr_runtime", "System Default"))
        runtime.grid(row=5, column=0, sticky='w')
        ttk.Label(form, text="Заметки").grid(row=6, column=0, sticky='w', pady=(10,0))
        notes = tk.Text(form, height=8, bg="#0e1320", fg="#d5e8ff", insertbackground="#ffffff", relief=tk.FLAT)
        notes.insert('1.0', profile.get("notes", ""))
        notes.grid(row=7, column=0, columnspan=2, sticky='nsew')
        form.columnconfigure(0, weight=1)
        form.rowconfigure(7, weight=1)
        return {"launch_path": launch_path, "status": status, "openxr_runtime": runtime, "notes": notes}

    def _build_mouse_tab(self, parent: ttk.Frame) -> None:
        root = ttk.LabelFrame(parent, text="VR to Mouse Overlay", style="Card.TLabelframe", padding=12)
        root.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Checkbutton(root, text="Всегда зажимать правую кнопку мыши", variable=self.mouse_hold_rmb, command=self._apply_rmb_state).pack(anchor='w', pady=(0,8))
        ttk.Label(root, text="DPI / чувствительность").pack(anchor='w')
        ttk.Scale(root, from_=5.0, to=120.0, variable=self.dpi_scale, orient='horizontal').pack(fill=tk.X, pady=(0,12))

        ttk.Label(root, text="Симуляция входа шлема (для проверки mouse-look)").pack(anchor='w')
        self.yaw_var = tk.DoubleVar(value=0.0)
        self.pitch_var = tk.DoubleVar(value=0.0)
        ttk.Scale(root, from_=-90, to=90, variable=self.yaw_var, orient='horizontal', command=self._on_head_moved).pack(fill=tk.X, pady=(4,8))
        ttk.Scale(root, from_=-60, to=60, variable=self.pitch_var, orient='horizontal', command=self._on_head_moved).pack(fill=tk.X)

    def _poll_delete_hotkey(self):
        down = (ctypes.windll.user32.GetAsyncKeyState(0x2E) & 0x8000) != 0  # VK_DELETE
        if down and not self._delete_prev_down:
            self.toggle_overlay()
        self._delete_prev_down = down
        self.after(30, self._poll_delete_hotkey)

    def _open_overlay(self):
        if self.overlay_window and self.overlay_window.winfo_exists():
            return
        self.dim_window = tk.Toplevel(self)
        self.dim_window.overrideredirect(True)
        self.dim_window.attributes('-topmost', True)
        self.dim_window.attributes('-alpha', 0.35)
        self.dim_window.configure(bg='black')
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        self.dim_window.geometry(f"{w}x{h}+0+0")
        self.dim_window.attributes('-disabled', True)

        self.overlay_window = tk.Toplevel(self)
        self.overlay_window.title("VR Overlay")
        self.overlay_window.attributes('-topmost', True)
        self.overlay_window.configure(bg="#111827")
        self.overlay_window.geometry("540x320+120+120")
        self.overlay_window.transient(self)
        self.overlay_window.lift()
        self.dim_window.lower(self.overlay_window)
        self.overlay_window.focus_force()

        frame = tk.Frame(self.overlay_window, bg="#111827")
        frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        tk.Label(frame, text="VR Overlay", font=("Segoe UI", 18, "bold"), fg="#e5f3ff", bg="#111827").pack(anchor='w')
        tk.Label(frame, text="Delete — закрыть overlay", fg="#9fb7d6", bg="#111827").pack(anchor='w', pady=(0,8))
        ttk.Checkbutton(frame, text="Всегда зажимать ПКМ", variable=self.mouse_hold_rmb, command=self._apply_rmb_state).pack(anchor='w', pady=6)
        ttk.Label(frame, text="DPI чувствительность").pack(anchor='w')
        ttk.Scale(frame, from_=5.0, to=120.0, variable=self.dpi_scale, orient='horizontal').pack(fill=tk.X, pady=(4,10))
        ttk.Button(frame, text="Закрыть", command=self._close_overlay).pack(anchor='e')

    def _close_overlay(self):
        if self.overlay_window and self.overlay_window.winfo_exists():
            self.overlay_window.destroy()
        if self.dim_window and self.dim_window.winfo_exists():
            self.dim_window.destroy()

    def toggle_overlay(self, _event=None):
        if self.overlay_window and self.overlay_window.winfo_exists():
            self._close_overlay()
        else:
            self._open_overlay()

    def _mouse_event(self, flags: int, dx: int = 0, dy: int = 0):
        ctypes.windll.user32.mouse_event(flags, dx, dy, 0, 0)

    def _apply_rmb_state(self):
        self._mouse_event(0x0008 if self.mouse_hold_rmb.get() else 0x0010)

    def _on_head_moved(self, _evt=None):
        yaw = self.yaw_var.get()
        pitch = self.pitch_var.get()
        dpi = self.dpi_scale.get()
        dx = int((yaw - self.prev_yaw) * dpi)
        dy = int((pitch - self.prev_pitch) * dpi)
        self.prev_yaw = yaw
        self.prev_pitch = pitch
        if dx or dy:
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
            w['status'].configure(text=f"❌ Разрешено только: {allowed}")
            messagebox.showerror("Неверный exe", f"Для {game_name} разрешено только: {allowed}")
            return
        w['launch_path'].delete(0, tk.END)
        w['launch_path'].insert(0, path)
        w['status'].configure(text='✅ Файл принят')

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
