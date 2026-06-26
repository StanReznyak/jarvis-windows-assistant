from .main_window_shared import *


class SettingsVisualMixin:
    def clamp_opacity(self, value, min_value=0.2, max_value=1.0):
        try:
            value = float(value)
        except Exception:
            value = max_value
        return max(min_value, min(max_value, value))

    def apply_root_opacity(self):
        normal_value = self.clamp_opacity(self.window_opacity_var.get())
        hud_value = self.clamp_opacity(self.hud_opacity_var.get())
        value = hud_value if bool(self.cfg.get("hud_mode", False)) else normal_value
        self.root.attributes("-alpha", value)
        self.window_opacity_var.set(normal_value)
        self.hud_opacity_var.set(hud_value)
        self.cfg["window_opacity"] = normal_value
        self.cfg["hud_opacity"] = hud_value

    def apply_overlay_opacity(self):
        value = self.clamp_opacity(self.overlay_opacity_var.get())
        self.overlay_opacity_var.set(value)
        self.cfg["overlay_opacity"] = value
        if self.overlay_window is not None:
            try:
                self.overlay_window.attributes("-alpha", value)
            except Exception:
                pass

    def apply_splash_opacity(self):
        value = self.clamp_opacity(self.splash_opacity_var.get())
        self.splash_opacity_var.set(value)
        self.cfg["splash_opacity"] = value

    def apply_hud_opacity(self):
        value = self.clamp_opacity(self.hud_opacity_var.get())
        self.hud_opacity_var.set(value)
        self.cfg["hud_opacity"] = value
        if bool(self.cfg.get("hud_mode", False)):
            try:
                self.root.attributes("-alpha", value)
            except Exception:
                pass

    def apply_all_opacity(self, initial=False):
        self.apply_root_opacity()
        self.apply_overlay_opacity()
        self.apply_splash_opacity()
        self.apply_hud_opacity()
        if not initial:
            save_config(self.cfg)

    def on_window_opacity_change(self, _value=None):
        self.apply_root_opacity()
        save_config(self.cfg)
        self.footer_var.set(f"Прозрачность окна: {int(self.window_opacity_var.get()*100)}%")

    def on_overlay_opacity_change(self, _value=None):
        self.apply_overlay_opacity()
        save_config(self.cfg)
        self.footer_var.set(f"Прозрачность оверлея: {int(self.overlay_opacity_var.get()*100)}%")

    def on_splash_opacity_change(self, _value=None):
        self.apply_splash_opacity()
        save_config(self.cfg)
        self.footer_var.set(f"Прозрачность splash: {int(self.splash_opacity_var.get()*100)}%")

    def on_hud_opacity_change(self, _value=None):
        self.apply_hud_opacity()
        save_config(self.cfg)
        self.footer_var.set(f"Прозрачность HUD: {int(self.hud_opacity_var.get()*100)}%")

    def step_window_opacity(self, delta):
        new_value = self.clamp_opacity(self.window_opacity_var.get() + delta)
        self.window_opacity_var.set(new_value)
        self.on_window_opacity_change()

    def step_hud_opacity(self, delta):
        new_value = self.clamp_opacity(self.hud_opacity_var.get() + delta)
        self.hud_opacity_var.set(new_value)
        self.on_hud_opacity_change()

    def build_scale_slider(self, parent, title, variable, command, min_pct=80, max_pct=150):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", pady=6)
        head = tk.Frame(row, bg=CARD)
        head.pack(fill="x")
        value_var = tk.StringVar(value=f"{int(variable.get()*100)}%")
        tk.Label(head, text=title, bg=CARD, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(head, textvariable=value_var, bg=CARD, fg=ACCENT_2, font=("Consolas", 11, "bold")).pack(side="right")
        scale = tk.Scale(row, from_=min_pct, to=max_pct, orient="horizontal", resolution=1, showvalue=False, highlightthickness=0, bd=0, troughcolor=PANEL_2, bg=CARD, fg=TEXT, activebackground=ACCENT, length=420)
        scale.pack(fill="x", pady=(4, 0))
        scale.set(int(variable.get()*100))
        def _on_scale(value):
            pct = max(min_pct, min(max_pct, int(float(value))))
            variable.set(pct / 100.0)
            value_var.set(f"{pct}%")
            command(pct / 100.0)
        scale.configure(command=_on_scale)

    def build_opacity_slider(self, parent, title, variable, command):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", pady=6)
        head = tk.Frame(row, bg=CARD)
        head.pack(fill="x")
        value_var = tk.StringVar(value=f"{int(variable.get()*100)}%")
        tk.Label(head, text=title, bg=CARD, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(head, textvariable=value_var, bg=CARD, fg=ACCENT_2, font=("Consolas", 11, "bold")).pack(side="right")
        scale = tk.Scale(row, from_=20, to=100, orient="horizontal", resolution=1, showvalue=False, highlightthickness=0, bd=0, troughcolor=PANEL_2, bg=CARD, fg=TEXT, activebackground=ACCENT, length=420)
        scale.pack(fill="x", pady=(4, 0))
        scale.set(int(variable.get()*100))
        def _on_scale(value):
            pct = max(20, min(100, int(float(value))))
            variable.set(pct / 100.0)
            value_var.set(f"{pct}%")
            command(pct / 100.0)
        scale.configure(command=_on_scale)

    def apply_topmost_flags(self):
        self.cfg["always_on_top"] = bool(self.always_on_top_var.get())
        self.cfg["overlay_topmost"] = bool(self.overlay_topmost_var.get())
        try:
            self.root.attributes("-topmost", bool(self.always_on_top_var.get()))
        except Exception:
            pass
        if self.overlay_window is not None:
            try:
                self.overlay_window.attributes("-topmost", bool(self.overlay_topmost_var.get()))
            except Exception:
                pass

    def on_main_topmost_toggle(self):
        self.apply_topmost_flags()
        save_config(self.cfg)
        self.footer_var.set("Главное окно закреплено сверху" if self.always_on_top_var.get() else "Главное окно больше не закреплено")

    def on_overlay_topmost_toggle(self):
        self.apply_topmost_flags()
        save_config(self.cfg)
        self.footer_var.set("Оверлей закреплён сверху" if self.overlay_topmost_var.get() else "Оверлей может уходить назад")

    def on_overlay_scale_change(self, _value=None):
        value = max(0.8, min(1.5, float(self.overlay_scale_var.get())))
        self.overlay_scale_var.set(value)
        self.cfg["overlay_scale"] = value
        save_config(self.cfg)
        if self.overlay_window is not None:
            self.toggle_overlay(force=False)
            if self.overlay_var.get():
                self.toggle_overlay(force=True)
        self.footer_var.set(f"Размер оверлея: {int(value*100)}%")

    def apply_glass_preset(self, preset):
        preset = (preset or "glass").strip().lower()
        presets = {
            "ghost": (0.66, 0.56, 0.72, 0.92),
            "glass": (0.82, 0.72, 0.86, 0.96),
            "solid": (0.94, 0.88, 0.94, 1.00),
        }
        if preset not in presets:
            preset = "glass"
        win, hud, over, splash = presets[preset]
        self.window_opacity_var.set(win)
        self.hud_opacity_var.set(hud)
        self.overlay_opacity_var.set(over)
        self.splash_opacity_var.set(splash)
        self.cfg["glass_preset"] = preset
        self.apply_all_opacity(initial=True)
        save_config(self.cfg)
        names = {"ghost": "Ghost", "glass": "Glass", "solid": "Solid"}
        self.footer_var.set(f"Активирован пресет {names[preset]}")
        self.post_log(f"[ui] Включен glass preset {names[preset]}")
        self.update_overlay_view()

    def apply_theme(self, theme_key, save=True):
        global ACCENT, ACCENT_2, DANGER, WARN
        theme = THEMES.get(theme_key, THEMES["cyan"])
        ACCENT = theme["accent"]
        ACCENT_2 = theme["accent_2"]
        DANGER = theme["danger"]
        WARN = theme["warn"]
        self.cfg["theme"] = theme_key
        if save:
            save_config(self.cfg)
            try:
                self.footer_var.set(f"Тема переключена: {theme['name']}")
                self.post_log(f"[ui] Активирована тема {theme['name']}")
                self.apply_all_opacity()
            except Exception:
                pass

    def toggle_hud_mode(self):
        enabled = not bool(self.cfg.get("hud_mode", False))
        self.cfg["hud_mode"] = enabled
        save_config(self.cfg)
        self.root.attributes("-fullscreen", enabled)
        if not enabled:
            self.root.geometry("1460x900")
        self.apply_root_opacity()
        self.footer_var.set("HUD-режим включен" if enabled else "HUD-режим выключен")
        self.post_log("[ui] HUD-режим включен" if enabled else "[ui] HUD-режим выключен")
