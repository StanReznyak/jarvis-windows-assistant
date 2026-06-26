from ..app.main_window_shared import *


def create_tray_image():
    if Image is None or ImageDraw is None:
        return None
    img = Image.new("RGBA", (64, 64), (7, 17, 31, 255))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((4, 4, 60, 60), radius=14, outline=(89, 216, 255, 255), width=3, fill=(13, 27, 42, 255))
    draw.text((22, 16), "J", fill=(124, 252, 144, 255))
    return img


def ensure_tray_state(app):
    if pystray is None or Image is None:
        if hasattr(app, "tray_status_var"):
            app.tray_status_var.set("Трей: нужны pystray и Pillow")
        return False
    if app.tray_icon is not None:
        return True
    try:
        image = create_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem("Показать JARVIS", lambda icon, item: app.root.after(0, app.restore_from_tray)),
            pystray.MenuItem("Быстрая панель", lambda icon, item: app.root.after(0, app.toggle_quickbar)),
            pystray.MenuItem("Оверлей", lambda icon, item: app.root.after(0, app.toggle_overlay)),
            pystray.MenuItem("Выход", lambda icon, item: app.root.after(0, app.full_exit)),
        )
        app.tray_icon = pystray.Icon("jarvis_tray", image, "JARVIS", menu)
        app.tray_thread = threading.Thread(target=app.tray_icon.run, daemon=True)
        app.tray_thread.start()
        app.append_system_event("tray", "Иконка в трее активирована", toast=False)
        if hasattr(app, "tray_status_var"):
            app.tray_status_var.set("Трей: активен")
        return True
    except Exception as exc:
        app.tray_icon = None
        app.post_log(f"[tray] ошибка запуска: {exc}")
        app.append_system_event("tray", f"Ошибка запуска трея: {exc}")
        if hasattr(app, "tray_status_var"):
            app.tray_status_var.set("Трей: не запустился")
        return False


def hide_to_tray(app):
    if not ensure_tray_state(app):
        app.append_system_event("tray", "Трей недоступен, окно свёрнуто обычным способом")
        app.minimize_window()
        return
    try:
        app.root.withdraw()
        app.is_hidden_to_tray = True
        app.footer_var.set("JARVIS скрыт в трее")
        app.append_system_event("tray", "JARVIS скрыт в трее")
        if hasattr(app, "tray_status_var"):
            app.tray_status_var.set("Трей: окно скрыто")
    except Exception:
        app.minimize_window()


def restore_from_tray(app):
    try:
        app.root.deiconify()
        app.root.lift()
        app.root.focus_force()
        app.is_hidden_to_tray = False
        app.footer_var.set("JARVIS возвращён из трея")
        app.append_system_event("tray", "JARVIS возвращён из трея")
        if hasattr(app, "tray_status_var"):
            app.tray_status_var.set("Трей: окно активно")
    except Exception:
        pass


def stop_tray_icon(app):
    if app.tray_icon is not None:
        try:
            app.tray_icon.stop()
        except Exception:
            pass
        app.tray_icon = None
