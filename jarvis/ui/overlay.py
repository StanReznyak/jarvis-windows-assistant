from ..app.main_window_shared import *


def update_overlay_view(app):
    if app.overlay_window is None:
        app.overlay_state_var.set("Оверлей выключен")
        return
    app.overlay_state_var.set("Оверлей активен")
    try:
        app.overlay_status_label.config(text=app.status_var.get(), fg=ACCENT_2 if app.listening else TEXT)
        app.overlay_heard_label.config(text=app.overlay_heard_var.get()[:60] or "...")
        app.overlay_answer_label.config(text=app.response_var.get()[:70])
        draw_overlay_orb(app)
    except Exception:
        pass


def toggle_overlay(app, force=None):
    desired = app.overlay_window is None if force is None else bool(force)
    if not desired:
        if app.overlay_window is not None:
            try:
                app.overlay_window.destroy()
            except Exception:
                pass
            app.overlay_window = None
            app.overlay_state_var.set("Оверлей выключен")
            app.footer_var.set("Мини-оверлей выключен")
        return
    if app.overlay_window is not None:
        try:
            app.overlay_window.lift()
        except Exception:
            pass
        return
    ow = tk.Toplevel(app.root)
    app.overlay_window = ow
    try:
        ow.overrideredirect(True)
    except Exception:
        pass
    ow.title("JARVIS — оверлей")
    scale = max(0.8, min(1.5, float(app.overlay_scale_var.get())))
    ow.geometry(f"{int(440*scale)}x{int(250*scale)}+960+80")
    ow.configure(bg=BG)
    ow.attributes("-topmost", bool(app.overlay_topmost_var.get()))
    try:
        ow.attributes("-alpha", app.clamp_opacity(app.overlay_opacity_var.get()))
    except Exception:
        pass
    ow.resizable(False, False)
    ow.protocol("WM_DELETE_WINDOW", lambda: toggle_overlay(app, force=False))

    frame = tk.Frame(ow, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
    frame.pack(fill="both", expand=True, padx=8, pady=8)
    top = tk.Frame(frame, bg=PANEL)
    top.pack(fill="x", padx=10, pady=(10, 4))

    def _start_drag(event):
        ow._drag_x = event.x_root - ow.winfo_x()
        ow._drag_y = event.y_root - ow.winfo_y()

    def _on_drag(event):
        dx = getattr(ow, "_drag_x", 0)
        dy = getattr(ow, "_drag_y", 0)
        ow.geometry(f"+{event.x_root - dx}+{event.y_root - dy}")

    top.bind("<ButtonPress-1>", _start_drag)
    top.bind("<B1-Motion>", _on_drag)
    tk.Label(top, text="JARVIS", bg=PANEL, fg=ACCENT, font=("Segoe UI", max(14, int(16*scale)), "bold")).pack(side="left")
    tk.Button(top, text="✕", command=lambda: toggle_overlay(app, force=False), bg=PANEL_2, fg=TEXT, relief="flat", bd=0, cursor="hand2").pack(side="right")

    orb_size = int(110 * scale)
    app.overlay_orb_canvas = tk.Canvas(frame, width=orb_size, height=orb_size, bg=PANEL, highlightthickness=0)
    app.overlay_orb_canvas.pack(pady=(0, 2))
    app.overlay_status_label = tk.Label(frame, text=app.status_var.get(), bg=PANEL, fg=TEXT, font=("Segoe UI", 11, "bold"))
    app.overlay_status_label.pack(anchor="center", pady=(2, 4))
    wrap = int(400 * scale)
    app.overlay_heard_label = tk.Label(frame, text=app.overlay_heard_var.get(), bg=PANEL, fg=ACCENT_2, font=("Segoe UI", max(10, int(10*scale))), wraplength=wrap, justify="left")
    app.overlay_heard_label.pack(anchor="w", padx=12)
    app.overlay_answer_label = tk.Label(frame, text=app.response_var.get(), bg=PANEL, fg=TEXT, font=("Segoe UI", max(10, int(10*scale))), wraplength=wrap, justify="left")
    app.overlay_answer_label.pack(anchor="w", padx=12, pady=(6, 8))

    controls = tk.Frame(frame, bg=PANEL)
    controls.pack(fill="x", padx=12, pady=(2, 10))
    for text, cmd in [("Микрофон", app.toggle_voice_hotkey), ("Стоп", app.stop_speaking), ("Главное окно", app.root.deiconify), ("Стекло", lambda: app.apply_glass_preset("ghost"))]:
        tk.Button(controls, text=text, command=cmd, bg=PANEL_2, fg=TEXT, relief="flat", bd=0, cursor="hand2").pack(side="left", padx=(0, 6))

    app.overlay_state_var.set("Оверлей активен")
    app.footer_var.set(f"Мини-оверлей включён • {int(app.overlay_opacity_var.get()*100)}%")
    update_overlay_view(app)


def draw_overlay_orb(app):
    if not hasattr(app, "overlay_orb_canvas") or app.overlay_orb_canvas is None:
        return
    c = app.overlay_orb_canvas
    c.delete("all")
    w = int(c.winfo_width() or 110)
    h = int(c.winfo_height() or 110)
    cx, cy = w // 2, h // 2
    pulse = 8 * math.sin(app.speech_visual_phase * 1.4)
    radius = 26 + max(0, pulse) + (10 if app.listening else 0) + int(app.speech_visual_boost * 10)
    c.create_oval(cx-44, cy-44, cx+44, cy+44, outline=BORDER, width=2)
    c.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, fill=ACCENT if app.listening else PANEL_2, outline="")
    c.create_text(cx, cy, text="J", fill=BG, font=("Segoe UI", 22, "bold"))
