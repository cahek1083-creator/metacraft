"""Minimalist Minecraft launcher desktop app (Tkinter)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class LauncherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Metacraft Launcher")
        self.geometry("980x620")
        self.minsize(900, 560)
        self.configure(bg="#0b1322")

        self._style = ttk.Style(self)
        self._style.theme_use("clam")
        self._configure_styles()
        self._build_ui()

    def _configure_styles(self) -> None:
        self._style.configure(
            "Header.TLabel",
            background="#0f1a30",
            foreground="#f4f7ff",
            font=("Segoe UI", 28, "bold"),
        )
        self._style.configure(
            "Eyebrow.TLabel",
            background="#0f1a30",
            foreground="#b6c2df",
            font=("Segoe UI", 10),
        )
        self._style.configure(
            "Meta.TLabel",
            background="#1a2740",
            foreground="#d7deef",
            font=("Segoe UI", 11),
        )
        self._style.configure(
            "Primary.TButton",
            font=("Segoe UI", 12, "bold"),
            foreground="#142611",
            background="#b9f3c1",
            borderwidth=0,
            padding=(10, 10),
        )
        self._style.map(
            "Primary.TButton",
            background=[("active", "#cef9d4")],
        )
        self._style.configure(
            "Ghost.TButton",
            font=("Segoe UI", 11),
            foreground="#f4f7ff",
            background="#ffffff22",
            borderwidth=0,
            padding=(10, 10),
        )
        self._style.map(
            "Ghost.TButton",
            background=[("active", "#ffffff33")],
        )

    def _build_ui(self) -> None:
        canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg="#0b1322")
        canvas.pack(fill="both", expand=True)

        self.bind(
            "<Configure>",
            lambda _event: self._redraw(canvas),
        )
        self._redraw(canvas)

    def _redraw(self, canvas: tk.Canvas) -> None:
        canvas.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()

        # Night background gradient imitation
        for i in range(height):
            shade = 14 + int((i / max(1, height)) * 26)
            color = f"#{shade:02x}{(shade + 8):02x}{(shade + 22):02x}"
            canvas.create_line(0, i, width, i, fill=color)

        # Calm moon on background
        moon_x = int(width * 0.16)
        moon_y = int(height * 0.2)
        moon_r = 62
        canvas.create_oval(
            moon_x - moon_r,
            moon_y - moon_r,
            moon_x + moon_r,
            moon_y + moon_r,
            fill="#f4f0de",
            outline="",
        )
        canvas.create_oval(
            moon_x + 14,
            moon_y - 9,
            moon_x + 31,
            moon_y + 8,
            fill="#ded7c0",
            outline="",
        )

        # Main launcher panel
        panel_x1 = int(width * 0.14)
        panel_y1 = int(height * 0.18)
        panel_x2 = int(width * 0.86)
        panel_y2 = int(height * 0.84)
        canvas.create_rectangle(
            panel_x1,
            panel_y1,
            panel_x2,
            panel_y2,
            fill="#0f1a30",
            outline="#5f6e8d",
            width=1,
        )

        # Left info card
        info_x1 = panel_x1 + 26
        info_y1 = panel_y1 + 130
        info_x2 = panel_x2 - 300
        info_y2 = panel_y2 - 28
        canvas.create_rectangle(
            info_x1,
            info_y1,
            info_x2,
            info_y2,
            fill="#1a2740",
            outline="#6d7da0",
            width=1,
        )

        # Rounded frosted-like action frame (simulated)
        action_x1 = panel_x2 - 262
        action_y1 = panel_y1 + 130
        action_x2 = panel_x2 - 24
        action_y2 = panel_y2 - 28
        canvas.create_rectangle(
            action_x1,
            action_y1,
            action_x2,
            action_y2,
            fill="#d9e3ff22",
            outline="#c9d8ff66",
            width=2,
        )

        self._draw_text_and_widgets(canvas, panel_x1, panel_y1, info_x1, info_y1, action_x1, action_y1)

    def _draw_text_and_widgets(
        self,
        canvas: tk.Canvas,
        panel_x1: int,
        panel_y1: int,
        info_x1: int,
        info_y1: int,
        action_x1: int,
        action_y1: int,
    ) -> None:
        canvas.create_text(
            panel_x1 + 30,
            panel_y1 + 34,
            text="metacraft",
            fill="#b7c2dc",
            font=("Segoe UI", 10),
            anchor="w",
        )
        canvas.create_text(
            panel_x1 + 30,
            panel_y1 + 74,
            text="Minecraft Launcher",
            fill="#f4f7ff",
            font=("Segoe UI", 28, "bold"),
            anchor="w",
        )
        canvas.create_text(
            panel_x1 + 30,
            panel_y1 + 104,
            text="Минималистичный вход в мир блоков",
            fill="#c9d4ee",
            font=("Segoe UI", 12),
            anchor="w",
        )

        canvas.create_text(
            info_x1 + 20,
            info_y1 + 28,
            text="Профиль\n\nSurvival Build\nВерсия 1.20.6 · Fabric",
            fill="#ecf1ff",
            font=("Segoe UI", 14),
            anchor="nw",
        )

        # Buttons on frosted frame
        labels = ["Играть", "Установки", "Аккаунт", "Выход"]
        styles = ["Primary.TButton", "Ghost.TButton", "Ghost.TButton", "Ghost.TButton"]

        base_y = action_y1 + 24
        for idx, (text, style_name) in enumerate(zip(labels, styles)):
            btn = ttk.Button(canvas, text=text, style=style_name, command=lambda t=text: self._on_click(t))
            canvas.create_window(action_x1 + 18, base_y + idx * 64, window=btn, width=200, anchor="nw")

    @staticmethod
    def _on_click(name: str) -> None:
        print(f"Нажата кнопка: {name}")


if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()
