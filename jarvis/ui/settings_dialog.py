from ..app.main_window_shared import *


def open_runtime_settings_dialog(app):
    existing = getattr(app, "runtime_settings_dialog", None)
    if existing is not None:
        try:
            existing.lift()
            existing.focus_force()
            return existing
        except Exception:
            pass

    win = tk.Toplevel(app.root)
    app.runtime_settings_dialog = win
    win.title("JARVIS • Быстрые настройки")
    win.configure(bg=BG)
    win.geometry("560x420+220+140")
    win.minsize(520, 380)
    try:
        win.transient(app.root)
    except Exception:
        pass

    def _close():
        try:
            win.destroy()
        finally:
            app.runtime_settings_dialog = None

    win.protocol("WM_DELETE_WINDOW", _close)

    shell = tk.Frame(win, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
    shell.pack(fill="both", expand=True, padx=12, pady=12)

    head = tk.Frame(shell, bg=PANEL)
    head.pack(fill="x", padx=16, pady=(14, 8))
    tk.Label(head, text="Быстрые настройки", bg=PANEL, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(side="left")
    tk.Button(head, text="✕", command=_close, bg=PANEL_2, fg=TEXT, relief="flat", bd=0, cursor="hand2").pack(side="right")

    tk.Label(shell, text="Здесь можно быстро проверить голос, оверлей и основные параметры интерфейса.", bg=PANEL, fg=MUTED, wraplength=500, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 12))

    form = tk.Frame(shell, bg=PANEL)
    form.pack(fill="x", padx=16)

    rows = [
        ("Распознавание речи", app.voice_input_engine_var),
        ("Озвучка", app.tts_engine_var),
        ("Ключевая фраза", app.wake_word_var),
    ]
    for idx, (label, var) in enumerate(rows):
        box = tk.Frame(form, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        box.pack(fill="x", pady=(0, 8))
        tk.Label(box, text=label, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(10, 0))
        entry = tk.Entry(box, textvariable=var)
        app.style_entry_widget(entry, font=("Segoe UI", 11))
        entry.configure(bg=BG)
        entry.pack(fill="x", padx=12, pady=(6, 12), ipady=7)

    checks = tk.Frame(shell, bg=PANEL)
    checks.pack(fill="x", padx=16, pady=(4, 8))
    tk.Checkbutton(checks, text="Мини-оверлей", variable=app.overlay_var, bg=PANEL, fg=TEXT, selectcolor=PANEL, activebackground=PANEL, activeforeground=TEXT).pack(anchor="w")
    tk.Checkbutton(checks, text="Ключевая фраза включена", variable=app.wake_word_enabled_var, bg=PANEL, fg=TEXT, selectcolor=PANEL, activebackground=PANEL, activeforeground=TEXT).pack(anchor="w")
    tk.Checkbutton(checks, text="Уведомления", variable=app.toast_var, bg=PANEL, fg=TEXT, selectcolor=PANEL, activebackground=PANEL, activeforeground=TEXT).pack(anchor="w")

    buttons = tk.Frame(shell, bg=PANEL)
    buttons.pack(fill="x", padx=16, pady=(8, 14))
    app.make_button(buttons, "Сохранить", app.save_paths, variant="primary", padx=12, pady=8).pack(side="left", padx=(0, 8))
    app.make_button(buttons, "Оверлей", app.toggle_overlay, variant="secondary", padx=12, pady=8).pack(side="left", padx=(0, 8))
    app.make_button(buttons, "В трей", app.hide_to_tray, variant="ghost", padx=12, pady=8).pack(side="left", padx=(0, 8))
    app.make_button(buttons, "Закрыть", _close, variant="secondary", padx=12, pady=8).pack(side="right")

    status = tk.Frame(shell, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
    status.pack(fill="both", expand=True, padx=16, pady=(0, 16))
    tk.Label(status, text="Состояние интерфейса", bg=PANEL_2, fg=ACCENT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
    summary = (
        f"Интерфейс: Tkinter\n"
        f"Оверлей: jarvis/ui/overlay.py\n"
        f"Трей: jarvis/ui/tray.py\n"
        f"Настройки: jarvis/ui/settings_dialog.py\n"
        f"Текущая страница: {getattr(app, 'current_page', '—')}\n"
        f"Голосовой режим: {app.voice_mode_var.get()}"
    )
    tk.Label(status, text=summary, bg=PANEL_2, fg=TEXT, justify="left", font=("Consolas", 10)).pack(anchor="w", padx=12, pady=(8, 12))

    return win
