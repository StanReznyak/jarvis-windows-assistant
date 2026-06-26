from .main_window_shared import *
from .main_window_shared import (
    _normalize_reminder_command_text,
    _looks_like_reminder_request,
    _looks_like_asr_garbage,
    _coerce_to_reminder_phrase,
)
from .voice_panel import VoicePanelMixin
from .reminders_panel import RemindersPanelMixin
from .settings_panel import SettingsPanelMixin
from .diagnostics_panel import DiagnosticsPanelMixin
from .actions_panel import ActionsPanelMixin
from .about_panel import AboutPanelMixin
from ..ui import overlay as ui_overlay
from ..ui import tray as ui_tray
from ..ui.settings_dialog import open_runtime_settings_dialog as ui_open_runtime_settings_dialog
from jarvis.weather import get_weather_answer, looks_like_weather_request


class JarvisApp(VoicePanelMixin, RemindersPanelMixin, SettingsPanelMixin, DiagnosticsPanelMixin, ActionsPanelMixin, AboutPanelMixin):
    def __init__(self, root):
        self.root = root
        self.cfg = load_config()
        self.voice_worker = None
        self.current_page = None
        self.page_buttons = {}
        self.pages = {}
        self.listening = False
        self.overlay_window = None
        self.overlay_heard_var = tk.StringVar(value="...")
        self.speech_visual_phase = 0.0
        self.speech_visual_boost = 0.0
        self.reminders = load_reminders()
        self.memory = load_memory_profile()
        self.reminder_count_var = tk.StringVar(value="0")
        self.reminder_status_var = tk.StringVar(value="Напоминаний: 0")
        self.reminder_feed_var = tk.StringVar(value="Активных напоминаний пока нет.")
        self.reminder_feed_short_var = tk.StringVar(value="Активных напоминаний пока нет.")
        self.memory_count_var = tk.StringVar(value="0")
        self.tts_busy = False
        # Guard against JARVIS hearing its own spoken answers through speakers/headphones.
        # Without this, long help text can accidentally create reminders from its own examples.
        self.voice_ignore_until = 0.0
        self.interrupt_phrases = ["замолчи", "стоп речь", "перестань говорить", "стоп", "тихо"]

        self.apply_theme(self.cfg.get("theme", "cyan"), save=False)

        self.root.title(f"{APP_TITLE} — {self.cfg['user_name']}")
        self.root.geometry("1460x900")
        self.root.minsize(1220, 780)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.on_root_close)
        self.root.report_callback_exception = self.handle_tk_exception

        self.tts_var = tk.BooleanVar(value=bool(self.cfg.get("auto_tts", True)))
        self.auto_start_voice_var = tk.BooleanVar(value=bool(self.cfg.get("auto_start_voice", True)))
        self.overlay_var = tk.BooleanVar(value=bool(self.cfg.get("overlay_enabled", False)))
        self.visualizer_var = tk.BooleanVar(value=bool(self.cfg.get("visualizer_enabled", True)))
        self.status_var = tk.StringVar(value="● ожидание")
        self.heard_var = tk.StringVar(value="Ничего не услышано")
        self.response_var = tk.StringVar(value="Готов к командам")
        self.clock_var = tk.StringVar(value="--:--:--")
        self.voice_mode_var = tk.StringVar(value="OFFLINE VOSK")
        self.model_var = tk.StringVar(value="Проверка модели...")
        self.last_action_var = tk.StringVar(value="Ничего не запускалось")
        self.footer_var = tk.StringVar(value="JARVIS готов")
        self.notes_count_var = tk.StringVar(value="0")
        self.profile_name_var = tk.StringVar(value="—")
        self.history_count_var = tk.StringVar(value="0")
        self.overlay_state_var = tk.StringVar(value="Оверлей выключен")
        self.hotkeys_var = tk.StringVar(value="Ctrl+K — палитра • F6 — быстрая панель • F8 — голос • Esc — стоп речи • F9 — оверлей • F11 — HUD • Ctrl+/− окно • Ctrl+Shift+/− HUD • Ctrl+Alt+1/2/3 пресеты")
        self.tts_engine_var = tk.StringVar(value=str(self.cfg.get("tts_preferred_engine", "auto")))
        self.tts_state_var = tk.StringVar(value="Голос включён" if self.tts_var.get() else "Без голоса")
        self.voice_pipeline_var = tk.StringVar(value="Голосовой модуль: готов")
        self.intent_editor_var = tk.StringVar(value=SUPPORTED_INTENTS[0][0] if SUPPORTED_INTENTS else "")
        self.intent_phrase_var = tk.StringVar(value="")
        self.wake_word_enabled_var = tk.BooleanVar(value=bool(self.cfg.get("wake_word_enabled", False)))
        self.wake_word_var = tk.StringVar(value=str(self.cfg.get("wake_word", "джарвис")))
        self.reminder_alert_repeats_var = tk.IntVar(value=max(1, int(self.cfg.get("reminder_alert_repeats", 3))))
        self.reminder_alert_interval_var = tk.DoubleVar(value=max(1.0, float(self.cfg.get("reminder_alert_interval_sec", 4.5))))
        self.reminder_melody_mode_var = tk.StringVar(value=str(self.cfg.get("reminder_melody_mode", "loud")))
        self.voice_input_engine_var = tk.StringVar(value=str(self.cfg.get("voice_input_engine", "auto")))
        self.speechkit_api_key_var = tk.StringVar(value=str(self.cfg.get("speechkit_api_key", "")))
        self.speechkit_folder_id_var = tk.StringVar(value=str(self.cfg.get("speechkit_folder_id", "")))
        self.speechkit_lang_var = tk.StringVar(value=str(self.cfg.get("speechkit_lang", "ru-RU")))
        self.speechkit_topic_var = tk.StringVar(value=str(self.cfg.get("speechkit_topic", "general")))
        self.whisper_model_var = tk.StringVar(value=str(self.cfg.get("whisper_model_size", "small")))
        self.whisper_compute_var = tk.StringVar(value=str(self.cfg.get("whisper_compute_type", "int8")))
        self.whisper_device_var = tk.StringVar(value=str(self.cfg.get("whisper_device", "auto")))
        self.whisper_cpp_cli_var = tk.StringVar(value=str(self.cfg.get("whisper_cpp_cli_path", "")))
        self.whisper_cpp_model_var = tk.StringVar(value=str(self.cfg.get("whisper_cpp_model_path", "")))
        self.whisper_cpp_lang_var = tk.StringVar(value=str(self.cfg.get("whisper_cpp_language", "ru")))
        self.whisper_cpp_threads_var = tk.IntVar(value=int(self.cfg.get("whisper_cpp_threads", 4) or 4))
        provider_value = str(self.cfg.get("model_provider", "auto")).lower()
        if provider_value not in {"auto", "local", "cloud"}:
            provider_value = "auto"
        self.model_answers_enabled_var = tk.BooleanVar(value=bool(self.cfg.get("model_answers_enabled", True)))
        self.model_fallback_unknown_var = tk.BooleanVar(value=bool(self.cfg.get("model_fallback_unknown", True)))
        self.model_provider_var = tk.StringVar(value=provider_value)
        self.ollama_base_url_var = tk.StringVar(value=str(self.cfg.get("ollama_base_url", "http://127.0.0.1:11434")))
        self.ollama_model_var = tk.StringVar(value=str(self.cfg.get("ollama_model", "llama3.2:1b")))
        self.ollama_max_tokens_var = tk.IntVar(value=int(self.cfg.get("ollama_max_output_tokens", 500) or 500))
        self.cloud_api_key_var = tk.StringVar(value=str(self.cfg.get("cloud_api_key", "")))
        self.cloud_model_var = tk.StringVar(value=str(self.cfg.get("cloud_model", "gpt-5-mini")))
        self.cloud_max_tokens_var = tk.IntVar(value=int(self.cfg.get("cloud_max_output_tokens", 500) or 500))
        self.model_chat_history = []
        self.model_busy = False

        self.tts = TTSWorker(lambda: bool(self.tts_var.get()), log_callback=self.log_tts_threadsafe, mode_getter=lambda: self.tts_engine_var.get())
        self.tts.start()

        self.window_opacity_var = tk.DoubleVar(value=float(self.cfg.get("window_opacity", 0.94)))
        self.overlay_opacity_var = tk.DoubleVar(value=float(self.cfg.get("overlay_opacity", 0.88)))
        self.splash_opacity_var = tk.DoubleVar(value=float(self.cfg.get("splash_opacity", 0.96)))
        self.hud_opacity_var = tk.DoubleVar(value=float(self.cfg.get("hud_opacity", 0.82)))
        self.always_on_top_var = tk.BooleanVar(value=bool(self.cfg.get("always_on_top", False)))
        self.overlay_topmost_var = tk.BooleanVar(value=bool(self.cfg.get("overlay_topmost", True)))
        self.overlay_scale_var = tk.DoubleVar(value=float(self.cfg.get("overlay_scale", 1.0)))
        self.quick_bar_topmost_var = tk.BooleanVar(value=bool(self.cfg.get("quick_bar_topmost", True)))
        self.minimize_to_tray_var = tk.BooleanVar(value=bool(self.cfg.get("minimize_to_tray", True)))
        self.close_to_tray_var = tk.BooleanVar(value=bool(self.cfg.get("close_to_tray", True)))
        self.start_minimized_var = tk.BooleanVar(value=bool(self.cfg.get("start_minimized", False)))
        self.autostart_enabled_var = tk.BooleanVar(value=bool(self.cfg.get("autostart_enabled", False)))
        self.restore_last_session_var = tk.BooleanVar(value=bool(self.cfg.get("restore_last_session", False)))
        self.startup_recovery_prompt_var = tk.BooleanVar(value=bool(self.cfg.get("startup_recovery_prompt", False)))
        self.launcher_app_name_var = tk.StringVar(value="")
        self.launcher_app_path_var = tk.StringVar(value="")
        self.launcher_site_name_var = tk.StringVar(value="")
        self.launcher_site_url_var = tk.StringVar(value="")
        self.launcher_icon_var = tk.StringVar(value="")
        self.launcher_edit_kind_var = tk.StringVar(value="")
        self.launcher_edit_original_var = tk.StringVar(value="")
        self.alias_name_var = tk.StringVar(value="")
        self.alias_target_var = tk.StringVar(value="")
        self.launcher_search_var = tk.StringVar(value="")
        self.profile_autosave_var = tk.BooleanVar(value=True)
        self.toast_notifications_var = tk.BooleanVar(value=bool(self.cfg.get("toast_notifications", True)))
        self.system_event_toasts_var = tk.BooleanVar(value=bool(self.cfg.get("system_event_toasts", True)))
        self.toast_window = None
        self.toast_after_id = None
        self.quickbar_window = None
        self.quickbar_entry = None
        self.quickbar_hint_var = None
        self.is_hidden_to_tray = False
        self.tray_icon = None
        self.tray_thread = None
        self.startup_recovery_window = None
        self.system_unread_count = 0
        self.system_nav_var = tk.StringVar(value="Системный журнал")
        self.system_category_var = tk.StringVar(value="все")
        self.system_unread_only_var = tk.BooleanVar(value=False)
        self.onboarding_open_after_var = tk.BooleanVar(value=True)
        self.onboarding_launch_settings_var = tk.BooleanVar(value=True)
        self.onboarding_launch_launcher_var = tk.BooleanVar(value=True)
        self.data_health_summary_var = tk.StringVar(value="Проверка данных ещё не запускалась")
        self.palette_query_var = tk.StringVar(value="")
        self.palette_status_var = tk.StringVar(value="Ctrl+K — открыть палитру команд")
        self.palette_result_count_var = tk.StringVar(value="0 результатов")
        self.command_palette_window = None
        self.command_palette_entry = None
        self.command_palette_listbox = None
        self.command_palette_hint_var = None
        self.command_palette_popup_items = []
        self.command_palette_items = []
        self.command_palette_page_items = []

        self.build_styles()
        self.build_ui()
        self.bind_hotkeys()
        self.root.after(200, self.update_clock)
        self.root.after(200, self.animate_visualizer)
        self.root.after(250, self.show_startup_splash)
        self.root.after(1000, self.check_reminders)
        self.apply_all_opacity(initial=True)
        self.apply_topmost_flags()

        self.post_log(f"{APP_TITLE} запущен")
        self.append_system_event("startup", f"JARVIS запущен • data={STORAGE_MODE}", toast=False)
        voice_diag = diagnose_voice_environment()
        model = find_vosk_model()
        if model:
            self.model_var.set(f"Модель Vosk: {model.name}")
            self.post_log(f"[jarvis] Найдена модель: {model.name}")
        else:
            self.model_var.set("Модель Vosk не найдена — нужна папка model")
            self.post_log("[jarvis] Модель Vosk не найдена. Положите распакованную модель в папку model рядом с JARVIS.exe.")
        self.post_log("[diagnostics] " + format_voice_diagnostics(voice_diag).replace("\n", " | "))
        if voice_diag.get("issues"):
            self.append_system_event("voice", "Диагностика голоса: есть проблемы с моделью или микрофоном", toast=True)

        self.auto_find_all(silent=True)
        self.load_notes()
        self.refresh_memory_ui()
        self.show_page("dashboard")
        if self.overlay_var.get():
            self.toggle_overlay(force=True)
        self.root.after(600, self.startup_recovery_flow)
        if self.start_minimized_var.get():
            self.append_system_event("startup", "Включён старт сразу в tray", toast=False)
            self.root.after(900, self.hide_to_tray)
        self.root.after(3000, self.session_autosave_tick)
        self.root.after(15000, self.autosave_profile_tick)
        self.root.after(1200, self.maybe_show_first_run_wizard)
        self.root.after(2600, self.maybe_show_model_setup_wizard)
        self.root.after(1800, self.auto_start_voice_if_enabled)


    def auto_start_voice_if_enabled(self):
        if not bool(self.cfg.get("auto_start_voice", True)):
            self.post_log("[voice] auto-start выключен в настройках")
            self.set_voice_pipeline_status("auto-start disabled")
            return
        if self.voice_worker and self.voice_worker.is_alive():
            return
        self.post_log("[voice] auto-start: запускаю голосовой режим")
        self.append_system_event("voice", "Голосовой режим запущен автоматически", toast=True)
        try:
            self.start_voice()
        except Exception as exc:
            self.post_log(f"[voice] auto-start ошибка: {exc}")
            self.set_status("ошибка голоса")
            self.set_voice_pipeline_status("auto-start failed")


    def log_tts_threadsafe(self, text: str):
        try:
            self.root.after(0, lambda: self._log_tts(text))
        except Exception:
            pass


    def _log_tts(self, text: str):
        lower = str(text).lower()
        if "старт озвучки" in lower:
            self.tts_busy = True
            self.voice_ignore_until = time.time() + 3600.0
        elif "озвучка завершена" in lower or "временный mp3 удалён" in lower or "ошибка озвучки" in lower:
            self.tts_busy = False
            # Small cooldown catches the last echo from speakers/microphone after playback ends.
            self.voice_ignore_until = time.time() + 1.8
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] [tts] {text}"
        self.post_log(line)
        widget = getattr(self, "tts_diag_text", None)
        if widget is not None:
            widget.insert("end", line + "\n")
            widget.see("end")


    def build_styles(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except Exception:
            pass
        s.configure("Jarvis.TNotebook", background=BG, borderwidth=0)
        s.configure("Jarvis.TNotebook.Tab", background=CARD_ALT, foreground=MUTED, padding=(18, 10), borderwidth=0)
        s.map("Jarvis.TNotebook.Tab", background=[("selected", PANEL_2), ("active", CARD)], foreground=[("selected", ACCENT), ("active", TEXT)])
        s.configure("Jarvis.TCombobox", fieldbackground=BG, background=CARD_ALT, foreground=TEXT, bordercolor=BORDER, arrowcolor=ACCENT)


    def make_button(self, parent, text, command, variant="secondary", width=None, font=("Segoe UI", 10, "bold"), padx=12, pady=8):
        if variant == "primary":
            bg = ACCENT
            fg = "#04111c"
            active_bg = "#9eeaff"
            active_fg = "#04111c"
            border = ACCENT
        elif variant == "success":
            bg = ACCENT_2
            fg = "#08150f"
            active_bg = "#b9ffd2"
            active_fg = "#08150f"
            border = ACCENT_2
        elif variant == "danger":
            bg = "#5a2030"
            fg = TEXT
            active_bg = "#743046"
            active_fg = TEXT
            border = "#8e3c58"
        elif variant == "ghost":
            bg = CARD
            fg = TEXT
            active_bg = PANEL_2
            active_fg = ACCENT
            border = BORDER
        else:
            bg = PANEL_2
            fg = TEXT
            active_bg = CARD
            active_fg = ACCENT
            border = BORDER
        btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg, activebackground=active_bg, activeforeground=active_fg, relief="flat", bd=0, cursor="hand2", font=font, padx=padx, pady=pady, highlightthickness=1, highlightbackground=border, highlightcolor=border)
        if width is not None:
            btn.configure(width=width)
        self.bind_hover_lift(btn, bg, active_bg)
        return btn


    def style_entry_widget(self, widget, font=("Segoe UI", 12), bg_override=None):
        bg = bg_override or BG
        widget.configure(bg=bg, fg=TEXT, insertbackground=TEXT, relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT, font=font)
        return widget


    def style_text_widget(self, widget):
        widget.configure(bg=BG, fg=TEXT, insertbackground=TEXT, relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT)
        return widget


    def style_listbox_widget(self, widget, font=("Segoe UI", 10)):
        widget.configure(bg=BG, fg=TEXT, relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER, selectbackground=PANEL_2, selectforeground=ACCENT, activestyle="none", font=font)
        return widget


    def bind_hover_lift(self, widget, normal_bg, hover_bg, targets=None):
        targets = targets or []
        def _paint(color):
            try:
                widget.configure(bg=color)
            except Exception:
                pass
            for child in targets:
                try:
                    child.configure(bg=color)
                except Exception:
                    pass
        widget.bind("<Enter>", lambda e: _paint(hover_bg), add="+")
        widget.bind("<Leave>", lambda e: _paint(normal_bg), add="+")
        return widget


    def nav_button(self, parent, key, text):
        icons = {
            "dashboard": "⌂",
            "chat": "⌘",
            "launch": "◫",
            "control": "◎",
            "memory": "◌",
            "palette": "⌕",
            "settings": "⚙",
            "system": "◉",
        }
        prefix = icons.get(key, "•")
        display = text if isinstance(text, tk.Variable) else f"{prefix}  {text}"
        btn = tk.Button(
            parent,
            textvariable=display if isinstance(display, tk.Variable) else None,
            text="" if isinstance(display, tk.Variable) else display,
            command=lambda k=key: self.show_page(k),
            bg=CARD_ALT,
            fg=TEXT,
            activebackground=PANEL_2,
            activeforeground=ACCENT,
            relief="flat",
            bd=0,
            font=("Segoe UI Semibold", 11),
            anchor="w",
            padx=18,
            pady=13,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        self.bind_hover_lift(btn, CARD_ALT, PANEL_2)
        btn.pack(fill="x", padx=12, pady=5)
        self.page_buttons[key] = btn

    def start_window_drag(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()


    def do_window_drag(self, event):
        dx = getattr(self, "_drag_x", 0)
        dy = getattr(self, "_drag_y", 0)
        self.root.geometry(f"+{event.x_root - dx}+{event.y_root - dy}")


    def toggle_max_restore(self):
        try:
            zoomed = bool(self.root.state() == "zoomed")
        except Exception:
            zoomed = False
        try:
            if zoomed:
                self.root.state("normal")
                self.root.geometry("1460x900")
            else:
                self.root.state("zoomed")
        except Exception:
            pass


    def build_ui(self):
        try:
            self.root.overrideredirect(True)
        except Exception:
            pass

        shell = tk.Frame(self.root, bg=BORDER, highlightthickness=0)
        shell.pack(fill="both", expand=True)

        titlebar = tk.Frame(shell, bg=PANEL_2, height=34)
        titlebar.pack(fill="x", side="top")
        titlebar.pack_propagate(False)
        for widget in (titlebar,):
            widget.bind("<ButtonPress-1>", self.start_window_drag)
            widget.bind("<B1-Motion>", self.do_window_drag)

        title_left = tk.Frame(titlebar, bg=PANEL_2)
        title_left.pack(side="left", fill="x", expand=True)
        title_left.bind("<ButtonPress-1>", self.start_window_drag)
        title_left.bind("<B1-Motion>", self.do_window_drag)
        tk.Label(title_left, text=f"  {APP_TITLE} •  {self.cfg['user_name']}", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 10, "bold")).pack(side="left", pady=6)

        title_buttons = tk.Frame(titlebar, bg=PANEL_2)
        title_buttons.pack(side="right")
        tk.Button(title_buttons, text="—", command=self.minimize_window, bg=PANEL_2, fg=TEXT, relief="flat", bd=0, width=4, cursor="hand2", activebackground=CARD_ALT, activeforeground=ACCENT).pack(side="left")
        tk.Button(title_buttons, text="▢", command=self.toggle_max_restore, bg=PANEL_2, fg=TEXT, relief="flat", bd=0, width=4, cursor="hand2", activebackground=CARD_ALT, activeforeground=ACCENT).pack(side="left")
        tk.Button(title_buttons, text="✕", command=self.on_root_close, bg=PANEL_2, fg=TEXT, relief="flat", bd=0, width=4, cursor="hand2", activebackground="#5a1f2a", activeforeground="#ffffff").pack(side="left")

        root_container = tk.Frame(shell, bg=BG)
        root_container.pack(fill="both", expand=True, padx=1, pady=(0, 1))

        sidebar = tk.Frame(root_container, bg=PANEL, width=270, highlightbackground=BORDER, highlightthickness=1)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        main = tk.Frame(root_container, bg=BG)
        main.pack(side="left", fill="both", expand=True)

        brand = tk.Frame(sidebar, bg=PANEL)
        brand.pack(fill="x", padx=14, pady=(14, 8))
        tk.Label(brand, text=f"JARVIS {APP_VERSION}", bg=PANEL, fg=ACCENT, font=("Segoe UI", 26, "bold")).pack(anchor="w")
        tk.Label(brand, text=APP_CODENAME, bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w")

        info = self.card(sidebar, bg=CARD_ALT)
        info.pack(fill="x", padx=12, pady=(8, 10))
        tk.Label(info, text="Пользователь", bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(12, 0))
        tk.Label(info, text=self.cfg.get("user_name", "Пользователь"), bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=14)
        tk.Label(info, textvariable=self.clock_var, bg=CARD_ALT, fg=ACCENT_2, font=("Consolas", 12, "bold")).pack(anchor="w", padx=14, pady=(4, 12))

        nav_wrap = tk.Frame(sidebar, bg=PANEL)
        nav_wrap.pack(fill="x", pady=(6, 8))
        self.nav_button(nav_wrap, "dashboard", "Панель")
        self.nav_button(nav_wrap, "chat", "Команды и лог")
        self.nav_button(nav_wrap, "launch", "Быстрый запуск")
        self.nav_button(nav_wrap, "control", "Центр управления")
        self.nav_button(nav_wrap, "memory", "Память")
        self.nav_button(nav_wrap, "palette", "Палитра команд")
        self.nav_button(nav_wrap, "settings", "Настройки")
        self.nav_button(nav_wrap, "system", self.system_nav_var)

        quick = self.card(sidebar, bg=CARD_ALT)
        quick.pack(fill="x", padx=12, pady=(8, 12))
        tk.Label(quick, text="Быстрые действия", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 8))
        for text, cmd in [
            ("▶ Старт голоса", self.start_voice),
            ("■ Стоп голоса", self.stop_voice),
            ("✕ Сбить речь", self.stop_speaking),
            ("◱ Оверлей", self.toggle_overlay),
("⌘ Палитра / поиск", self.toggle_command_palette),
            ("Telegram", self.open_telegram_ui),
            ("Discord", self.open_discord_ui),
            ("Steam", self.open_steam_ui),
            ("Свернуть в трей", self.hide_to_tray),
            ("Вернуть из трея", self.restore_from_tray),
        ]:
            tk.Button(quick, text=text, command=cmd, bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT,
                      relief="flat", bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2").pack(fill="x", padx=14, pady=4)
        tk.Checkbutton(quick, text="Озвучивать ответы", variable=self.tts_var, command=self.save_ui_config, bg=CARD_ALT, fg=TEXT,
                       activebackground=CARD_ALT, activeforeground=TEXT, selectcolor=CARD_ALT, font=("Segoe UI", 10)).pack(anchor="w", padx=14, pady=(8, 4))
        tk.Checkbutton(quick, text="Мини-оверлей", variable=self.overlay_var, command=self.save_ui_config, bg=CARD_ALT, fg=TEXT,
                       activebackground=CARD_ALT, activeforeground=TEXT, selectcolor=CARD_ALT, font=("Segoe UI", 10)).pack(anchor="w", padx=14, pady=(0, 4))
        tk.Checkbutton(quick, text="Анимация прослушки", variable=self.visualizer_var, command=self.save_ui_config, bg=CARD_ALT, fg=TEXT,
                       activebackground=CARD_ALT, activeforeground=TEXT, selectcolor=CARD_ALT, font=("Segoe UI", 10)).pack(anchor="w", padx=14, pady=(0, 14))

        header = tk.Frame(main, bg=BG)
        header.pack(fill="x", padx=18, pady=(16, 10))
        hero = self.card(header, bg=CARD_ALT)
        hero.pack(side="left", fill="x", expand=True, padx=(0, 10))
        hero_inner = tk.Frame(hero, bg=CARD_ALT)
        hero_inner.pack(fill="both", expand=True, padx=18, pady=16)
        left_head = tk.Frame(hero_inner, bg=CARD_ALT)
        left_head.pack(side="left", fill="both", expand=True)
        tk.Label(left_head, text=APP_TITLE, bg=CARD_ALT, fg=TEXT, font=("Segoe UI Semibold", 30)).pack(anchor="w")
        tk.Label(left_head, text=APP_SUBTITLE, bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 11), wraplength=760, justify="left").pack(anchor="w", pady=(4, 10))
        pills = tk.Frame(left_head, bg=CARD_ALT)
        pills.pack(anchor="w")
        self.pill(pills, "Команды", fg=ACCENT).pack(side="left", padx=(0, 8))
        self.pill(pills, "Быстрый запуск", fg=ACCENT_2).pack(side="left", padx=(0, 8))
        self.pill(pills, "Восстановление", fg=WARN).pack(side="left", padx=(0, 8))
        self.pill(pills, "Журнал событий", fg="#ff9fb2").pack(side="left")

        hero_metrics = tk.Frame(left_head, bg=CARD_ALT)
        hero_metrics.pack(anchor="w", fill="x", pady=(14, 0))
        for idx, (title, var, color) in enumerate([
            ("Статус", self.status_var, ACCENT_2),
            ("Последний ответ", self.response_var, TEXT),
            ("Последнее действие", self.last_action_var, WARN),
        ]):
            metric = tk.Frame(hero_metrics, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
            metric.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 8, 0))
            tk.Label(metric, text=title, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(12, 0))
            tk.Label(metric, textvariable=var, bg=PANEL_2, fg=color, font=("Segoe UI", 12, "bold"), wraplength=230, justify="left").pack(anchor="w", padx=14, pady=(6, 12))
            hero_metrics.grid_columnconfigure(idx, weight=1)

        right_head = tk.Frame(hero_inner, bg=CARD_ALT, width=290)
        right_head.pack(side="left", fill="y", padx=(16, 0))
        right_head.pack_propagate(False)
        status_box = tk.Frame(right_head, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        status_box.pack(fill="x")
        tk.Label(status_box, text="Состояние системы", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(12, 0))
        tk.Label(status_box, textvariable=self.status_var, bg=PANEL_2, fg=ACCENT_2, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=16)
        tk.Label(status_box, textvariable=self.model_var, bg=PANEL_2, fg=TEXT, font=("Segoe UI", 9), wraplength=250, justify="left").pack(anchor="w", padx=16, pady=(2, 6))
        tk.Label(status_box, textvariable=self.overlay_state_var, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9), wraplength=250, justify="left").pack(anchor="w", padx=16, pady=(0, 10))
        quick_pills = tk.Frame(status_box, bg=PANEL_2)
        quick_pills.pack(anchor="w", padx=16, pady=(0, 12))
        self.pill(quick_pills, "Голос", fg=ACCENT).pack(side="left", padx=(0, 6))
        self.pill(quick_pills, "Трей", fg=ACCENT_2).pack(side="left", padx=(0, 6))
        self.pill(quick_pills, "Автосохранение", fg=WARN).pack(side="left")

        glass_bar = self.card(main, bg=CARD_ALT)
        glass_bar.pack(fill="x", padx=18, pady=(0, 10))
        tk.Label(glass_bar, text="Прозрачность", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left", padx=(16, 12), pady=12)
        for label, preset in [("Лёгкая", "ghost"), ("Стекло", "glass"), ("Плотная", "solid")]:
            tk.Button(glass_bar, text=label, command=lambda p=preset: self.apply_glass_preset(p), bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2", padx=12, pady=8, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 8), pady=8)
        tk.Button(glass_bar, text="⌨ Быстрая панель", command=self.toggle_quickbar, bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2", padx=12, pady=8, font=("Segoe UI", 10, "bold")).pack(side="right", padx=(8, 8), pady=8)
        tk.Button(glass_bar, text="📌 Поверх окон: ВКЛ/ВЫКЛ", command=self.toggle_main_topmost_button, bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT_2, relief="flat", bd=0, cursor="hand2", padx=12, pady=8, font=("Segoe UI", 10, "bold")).pack(side="right", padx=(8, 16), pady=8)

        self.page_container = tk.Frame(main, bg=BG)
        self.page_container.pack(fill="both", expand=True, padx=18, pady=(0, 8))

        footer = tk.Frame(main, bg=PANEL_2, height=42, highlightbackground=BORDER, highlightthickness=1)
        footer.pack(fill="x", side="bottom", padx=18, pady=(0, 16))
        footer.pack_propagate(False)
        self.make_shell_badge(footer, "Система", self.status_var.get() if hasattr(self, "status_var") else "Готов", ACCENT_2).pack(side="left", padx=(10, 8), pady=6)
        tk.Label(footer, textvariable=self.footer_var, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 10)).pack(side="left", padx=4)
        self.make_shell_badge(footer, "Версия", APP_VERSION, ACCENT).pack(side="right", padx=(8, 10), pady=6)
        tk.Label(footer, textvariable=self.hotkeys_var, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 10)).pack(side="right", padx=4)

        self.build_dashboard_page()
        self.build_chat_page()
        self.build_launch_page()
        self.build_control_page()
        self.build_memory_page()
        self.build_palette_page()
        self.build_settings_page()
        self.build_system_page()


    def build_dashboard_page(self):
        page = tk.Frame(self.page_container, bg=BG)
        self.pages["dashboard"] = page

        hero_row = tk.Frame(page, bg=BG)
        hero_row.pack(fill="x")
        for title, var, color in [
            ("Статус", self.status_var, ACCENT_2),
            ("Услышано", self.heard_var, ACCENT),
            ("Последний ответ", self.response_var, TEXT),
            ("Последнее действие", self.last_action_var, WARN),
        ]:
            card = self.card(hero_row, bg=CARD_ALT)
            card.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=(0, 10))
            tk.Frame(card, bg=color, height=4).pack(fill="x")
            tk.Label(card, text=title, bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(12, 0))
            wrap = 250 if title != "Последний ответ" else 320
            tk.Label(card, textvariable=var, bg=CARD_ALT, fg=color, font=("Segoe UI", 14, "bold"), justify="left", wraplength=wrap).pack(anchor="w", padx=14, pady=(6, 14))

        events_card = self.card(page, bg=CARD_ALT)
        events_card.pack(fill="x", pady=(0, 10))
        pulse_top = tk.Frame(events_card, bg=CARD_ALT)
        pulse_top.pack(fill="x", padx=16, pady=(14, 0))
        tk.Label(pulse_top, text="Системный пульс", bg=CARD_ALT, fg=TEXT, font=("Segoe UI Semibold", 18)).pack(side="left")
        pulse_pills = tk.Frame(pulse_top, bg=CARD_ALT)
        pulse_pills.pack(side="right")
        self.pill(pulse_pills, "Восстановление", fg=WARN).pack(side="left", padx=(0, 6))
        self.pill(pulse_pills, "Автосохранение", fg=ACCENT_2).pack(side="left", padx=(0, 6))
        self.pill(pulse_pills, "Трей", fg=ACCENT).pack(side="left")
        tk.Label(events_card, text="Последние системные действия JARVIS: запуск, восстановление, автосохранение и работа в трее.", bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 10), wraplength=980, justify="left").pack(anchor="w", padx=16, pady=(6, 10))
        self.dashboard_events_text = tk.Text(events_card, height=5, wrap="word", font=("Consolas", 10))
        self.style_text_widget(self.dashboard_events_text)
        self.dashboard_events_text.pack(fill="x", padx=16, pady=(0, 16))

        command_card = self.card(page, bg=CARD_ALT)
        command_card.pack(fill="x", pady=(0, 10))
        self.section_title(command_card, "Командная строка", "Главная строка управления: ввод команды, быстрый запуск и ответ JARVIS")
        cmd_row = tk.Frame(command_card, bg=CARD_ALT)
        cmd_row.pack(fill="x", padx=16, pady=(14, 10))
        cmd_entry_shell = tk.Frame(cmd_row, bg=BG, highlightbackground=ACCENT, highlightthickness=1)
        cmd_entry_shell.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.dashboard_entry = tk.Entry(cmd_entry_shell)
        self.style_entry_widget(self.dashboard_entry, font=("Segoe UI", 16))
        self.dashboard_entry.pack(fill="x", expand=True, ipady=13, padx=14, pady=11)
        self.dashboard_entry.bind("<Return>", lambda e: self.send_entry(source="dashboard"))
        self.make_button(cmd_row, "Выполнить", lambda: self.send_entry(source="dashboard"), variant="primary", font=("Segoe UI", 11, "bold"), padx=18, pady=13).pack(side="left")
        self.make_button(cmd_row, "Быстрая панель", self.toggle_quickbar, variant="secondary", padx=14, pady=13).pack(side="left", padx=(8,0))
        self.make_button(cmd_row, "⌘ Палитра", self.toggle_command_palette, variant="secondary", padx=14, pady=13).pack(side="left", padx=(8,0))
        self.make_button(cmd_row, "Поверх окон", self.toggle_main_topmost_button, variant="ghost", padx=14, pady=13).pack(side="left", padx=(8,0))
        chips = tk.Frame(command_card, bg=CARD_ALT)
        chips.pack(fill="x", padx=16, pady=(0, 16))
        for idx, cmd in enumerate(["открой телеграм", "рабочий режим", "покажи напоминания", "центр запуска", "system journal", "quick bar"]):
            tk.Button(chips, text=cmd, command=lambda t=cmd: (self.dashboard_entry.delete(0, "end"), self.dashboard_entry.insert(0, t), self.dashboard_entry.focus_set()),
                      bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2", padx=12, pady=8).grid(row=0, column=idx, padx=(0 if idx == 0 else 6, 0), pady=0, sticky="w")

        center = tk.Frame(page, bg=BG)
        center.pack(fill="both", expand=True)

        left = tk.Frame(center, bg=BG)
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(center, bg=BG, width=390)
        right.pack(side="left", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        reactor = self.card(left, bg=CARD_ALT)
        reactor.pack(fill="x", pady=(0, 10))
        self.section_title(reactor, "Голосовое ядро", "Пульс и статус меняются во время прослушивания, распознавания и озвучивания ответа.")
        viz_wrap = tk.Frame(reactor, bg=CARD_ALT)
        viz_wrap.pack(fill="x", padx=16, pady=(14, 16))
        self.visual_canvas = tk.Canvas(viz_wrap, width=420, height=136, bg=BG, highlightthickness=1, highlightbackground=BORDER)
        self.visual_canvas.pack(side="left", fill="x", expand=True)
        controls = tk.Frame(viz_wrap, bg=CARD_ALT)
        controls.pack(side="left", padx=(16, 0), fill="y")
        for text, cmd, color in [
            ("▶ Слушать", self.start_voice, ACCENT),
            ("■ Стоп микрофон", self.stop_voice, WARN),
            ("✕ Прервать речь", self.stop_speaking, DANGER),
            ("◱ Оверлей", self.toggle_overlay, ACCENT_2),
            ("◉ Призрак", lambda: self.apply_glass_preset("ghost"), ACCENT),
            ("◉ Стекло", lambda: self.apply_glass_preset("glass"), ACCENT_2),
            ("◉ Плотный", lambda: self.apply_glass_preset("solid"), WARN),
        ]:
            btn = tk.Button(controls, text=text, command=cmd, bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=color,
                      relief="flat", bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2", padx=12, pady=10)
            btn.pack(fill="x", pady=4)
            self.bind_hover_lift(btn, PANEL_2, CARD)

        actions = self.card(left, bg=CARD_ALT)
        actions.pack(fill="both", expand=True)
        self.section_title(actions, "Быстрые действия", "Частые команды собраны в одном месте.")
        grid = tk.Frame(actions, bg=CARD_ALT)
        grid.pack(fill="both", expand=True, padx=16, pady=(14, 16))
        quick_commands = [
            "открой телеграм", "открой дискорд", "открой стим", "открой ютуб",
            "сколько времени", "какая дата", "покажи заметки", "экспорт заметок",
            "рабочий режим", "игровой режим", "тихий режим", "покажи напоминания",
            "открой загрузки", "открой документы", "сверни все окна", "выход"
        ]
        for idx, cmd in enumerate(quick_commands):
            r, c = divmod(idx, 2)
            btn = tk.Button(grid, text=cmd, command=lambda t=cmd: self.handle_command(t), bg=PANEL_2, fg=TEXT,
                            activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0,
                            font=("Segoe UI", 10, "bold"), cursor="hand2", padx=12, pady=14, wraplength=180, justify="left")
            btn.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)
            self.bind_hover_lift(btn, PANEL_2, CARD)
        for i in range(8):
            grid.rowconfigure(i, weight=1)
        for i in range(2):
            grid.columnconfigure(i, weight=1)

        right_top = self.card(right, bg=CARD_ALT)
        right_top.pack(fill="x", pady=(0, 10))
        self.section_title(right_top, "Состояние системы", "Что сейчас включено и в каком режиме работает JARVIS")
        stats_grid = tk.Frame(right_top, bg=CARD_ALT)
        stats_grid.pack(fill="x", padx=16, pady=(12, 10))
        for idx, (caption, var) in enumerate([
            ("Голосовой движок", self.voice_mode_var),
            ("Оверлей", self.overlay_state_var),
            ("Заметок", self.notes_count_var),
            ("История", self.history_count_var),
            ("Напоминания", self.reminder_count_var),
            ("Память", self.memory_count_var),
        ]):
            box = tk.Frame(stats_grid, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
            r, c = divmod(idx, 2)
            box.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
            tk.Label(box, text=caption, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(10, 0))
            tk.Label(box, textvariable=var, bg=PANEL_2, fg=TEXT, font=("Segoe UI", 10, "bold"), wraplength=150, justify="left").pack(anchor="w", padx=12, pady=(4, 10))
        for i in range(2):
            stats_grid.grid_columnconfigure(i, weight=1)
        hotkey_box = tk.Frame(right_top, bg=CARD_ALT)
        hotkey_box.pack(fill="x", padx=16, pady=(0, 10))
        for idx, (label, cmd, color) in enumerate([
            ("Ctrl+K", self.toggle_command_palette, ACCENT),
            ("F6", self.toggle_quickbar, ACCENT_2),
            ("F9", self.toggle_overlay, WARN),
            ("F11", self.toggle_hud_mode, DANGER),
        ]):
            pill = tk.Button(hotkey_box, text=label, command=cmd, bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=color,
                             relief="flat", bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2", padx=10, pady=7)
            pill.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 6, 0))
            self.bind_hover_lift(pill, PANEL_2, CARD)
            hotkey_box.grid_columnconfigure(idx, weight=1)
        self.make_button(right_top, "Очистить лог", self.clear_log, variant="secondary", padx=14, pady=10).pack(fill="x", padx=16, pady=(0, 8))
        self.make_button(right_top, "Открыть журнал событий", lambda: self.show_page("system"), variant="ghost", padx=14, pady=10).pack(fill="x", padx=16, pady=(0, 8))
        self.make_button(right_top, "Открыть настройки", lambda: self.show_page("settings"), variant="ghost", padx=14, pady=10).pack(fill="x", padx=16, pady=(0, 16))

        right_bottom = self.card(right, bg=CARD_ALT)
        right_bottom.pack(fill="both", expand=True)
        self.section_title(right_bottom, "Живой журнал", "Последние действия ассистента в реальном времени")
        self.dashboard_log = tk.Text(right_bottom, font=("Consolas", 10), wrap="word")
        self.style_text_widget(self.dashboard_log)
        self.dashboard_log.pack(fill="both", expand=True, padx=16, pady=(14, 12))
        empty_hint = tk.Frame(right_bottom, bg=CARD_ALT)
        empty_hint.pack(fill="x", padx=16, pady=(0, 16))
        self.pill(empty_hint, "Ctrl+K Палитра", fg=ACCENT).pack(side="left", padx=(0, 6))
        self.pill(empty_hint, "F6 Быстрая панель", fg=ACCENT_2).pack(side="left", padx=(0, 6))
        self.pill(empty_hint, "F9 Оверлей", fg=WARN).pack(side="left", padx=(0, 6))
        self.pill(empty_hint, "F11 Интерфейс", fg=DANGER).pack(side="left")


    def build_chat_page(self):
        page = tk.Frame(self.page_container, bg=BG)
        self.pages["chat"] = page

        self.section_title(page, "Команды и лог", "Ручной ввод, история и ответы ассистента")

        reminder_live = self.card(page, bg=CARD_ALT)
        reminder_live.pack(fill="x", pady=(0, 10))
        live_head = tk.Frame(reminder_live, bg=CARD_ALT)
        live_head.pack(fill="x", padx=18, pady=(14, 8))
        tk.Label(live_head, text="Лента напоминаний", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(live_head, text="Активные напоминания всегда видны прямо сверху, без прокрутки боковой панели.", bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 9), wraplength=920, justify="left").pack(anchor="w", pady=(4, 0))
        self.reminders_live_text = tk.Text(reminder_live, height=4, bg=BG, fg=TEXT, relief="flat", bd=0, highlightthickness=0, wrap="word", insertbackground=TEXT)
        self.reminders_live_text.pack(fill="x", padx=18, pady=(0, 14))
        self.reminders_live_text.configure(state="disabled")

        body = tk.Frame(page, bg=BG)
        body.pack(fill="both", expand=True, pady=(12, 0))

        left = self.card(body)
        left.pack(side="left", fill="both", expand=True)
        right = self.card(body, bg=CARD_ALT)
        right.pack(side="left", fill="y", padx=(10, 0))
        right.configure(width=320)
        right.pack_propagate(False)

        tk.Label(left, text="Журнал", bg=CARD, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        self.log_text = tk.Text(left, font=("Consolas", 11), wrap="word")
        self.style_text_widget(self.log_text)
        self.log_text.pack(fill="both", expand=True, padx=16)
        bottom = tk.Frame(left, bg=CARD)
        bottom.pack(fill="x", padx=16, pady=16)
        chat_entry_shell = tk.Frame(bottom, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        chat_entry_shell.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry = tk.Entry(chat_entry_shell)
        self.style_entry_widget(self.entry, font=("Segoe UI", 15))
        self.entry.pack(fill="x", expand=True, ipady=12, padx=12, pady=10)
        self.entry.bind("<Return>", lambda e: self.send_entry(source="chat"))
        self.make_button(bottom, "Выполнить", lambda: self.send_entry(source="chat"), variant="primary", font=("Segoe UI", 11, "bold"), padx=16, pady=12).pack(side="left")

        tk.Label(right, text="Справка", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        help_text = (
            "Примеры:\n\n"
            "• джарвис открой телеграм\n"
            "• джарвис открой дискорд\n"
            "• открой стим\n"
            "• открой ютуб\n"
            "• сколько времени\n"
            "• какая дата\n"
            "• запомни купить наушники\n"
            "• напомни через 20 минут разморозить курицу\n"
            "• напомни завтра в 9 написать клиенту\n"
            "• покажи заметки\n"
            "• покажи напоминания\n"
            "• открой загрузки / документы / панель управления\n\n"
            "Горячие клавиши:\n"
            "• F8 — старт/стоп микрофона\n"
            "• Esc — прервать озвучку\n"
            "• рабочий режим / игровой режим / тихий режим\n"
            "• F9 — мини-оверлей\n"
        )
        tk.Label(right, text=help_text, bg=CARD_ALT, fg=MUTED, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=16)
        tk.Button(right, text="▶ Старт голоса", command=self.start_voice, bg=PANEL_2, fg=TEXT, activebackground=CARD,
                  activeforeground=ACCENT, relief="flat", bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2").pack(fill="x", padx=16, pady=(12, 6))
        tk.Button(right, text="■ Стоп голоса", command=self.stop_voice, bg=PANEL_2, fg=TEXT, activebackground=CARD,
                  activeforeground=ACCENT, relief="flat", bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2").pack(fill="x", padx=16, pady=(0, 6))
        tk.Button(right, text="✕ Сбить речь", command=self.stop_speaking, bg=PANEL_2, fg=TEXT, activebackground=CARD,
                  activeforeground=DANGER, relief="flat", bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2").pack(fill="x", padx=16)


    def build_memory_page(self):
        page = tk.Frame(self.page_container, bg=BG)
        self.pages["memory"] = page

        self.section_title(page, "Memory Center", "Заметки, профиль и активные напоминания в одном месте")

        hero = self.card(page, bg=CARD_ALT)
        hero.pack(fill="x", pady=(12, 10))
        hero_top = tk.Frame(hero, bg=CARD_ALT)
        hero_top.pack(fill="x", padx=18, pady=(16, 8))
        tk.Label(hero_top, text="ПАМЯТЬ", bg=CARD_ALT, fg=ACCENT_2, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(hero_top, text="Локальная память и личный контекст", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 19, "bold")).pack(anchor="w", pady=(4, 2))
        tk.Label(hero_top, text="Здесь собраны заметки, сохранённые факты, напоминания и профиль пользователя.", bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 10), wraplength=920, justify="left").pack(anchor="w")

        hero_stats = tk.Frame(hero, bg=CARD_ALT)
        hero_stats.pack(fill="x", padx=18, pady=(4, 18))
        stat_defs = [
            ("Profile", self.profile_name_var, ACCENT_2),
            ("Facts", self.memory_count_var, ACCENT),
            ("Notes", self.notes_count_var, TEXT),
            ("Reminders", self.reminder_count_var, ACCENT),
        ]
        for idx, (label, variable, color) in enumerate(stat_defs):
            card = tk.Frame(hero_stats, bg=PANEL_2, highlightthickness=1, highlightbackground=BORDER)
            card.grid(row=0, column=idx, padx=6, sticky="nsew")
            tk.Label(card, text=label, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
            tk.Label(card, textvariable=variable, bg=PANEL_2, fg=color, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=(0, 12))
            hero_stats.columnconfigure(idx, weight=1)

        reminder_strip = tk.Frame(hero, bg=PANEL_2, highlightthickness=1, highlightbackground=BORDER)
        reminder_strip.pack(fill="x", padx=18, pady=(0, 16))
        strip_head = tk.Frame(reminder_strip, bg=PANEL_2)
        strip_head.pack(fill="x", padx=12, pady=(10, 4))
        tk.Label(strip_head, text="Лента напоминаний", bg=PANEL_2, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(strip_head, textvariable=self.reminder_status_var, bg=PANEL_2, fg=ACCENT, font=("Segoe UI", 9, "bold")).pack(side="right")
        self.reminders_hero_label = tk.Label(reminder_strip, textvariable=self.reminder_feed_var, bg=BG, fg=TEXT, justify="left", anchor="w", font=("Consolas", 10), wraplength=980)
        self.reminders_hero_label.pack(fill="x", padx=12, pady=(0, 12))

        memory_feed = self.card(page, bg=CARD_ALT)
        memory_feed.pack(fill="x", pady=(0, 10))
        mf_head = tk.Frame(memory_feed, bg=CARD_ALT)
        mf_head.pack(fill="x", padx=16, pady=(12, 6))
        tk.Label(mf_head, text="Лента напоминаний", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(side="left")
        tk.Label(mf_head, textvariable=self.reminder_status_var, bg=CARD_ALT, fg=ACCENT, font=("Segoe UI", 9, "bold")).pack(side="right")
        self.reminders_memory_feed_label = tk.Label(memory_feed, textvariable=self.reminder_feed_var, bg=BG, fg=TEXT, justify="left", anchor="w", font=("Consolas", 10), wraplength=980)
        self.reminders_memory_feed_label.pack(fill="x", padx=16, pady=(0, 12))

        body = tk.Frame(page, bg=BG)
        body.pack(fill="both", expand=True, pady=(0, 0))

        notes_card = self.card(body)
        notes_card.pack(side="left", fill="both", expand=True)
        side = self.card(body, bg=CARD_ALT)
        side.pack(side="left", fill="y", padx=(10, 0))
        side.configure(width=328)
        side.pack_propagate(False)

        notes_header = tk.Frame(notes_card, bg=CARD)
        notes_header.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(notes_header, text="Заметки", bg=CARD, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(notes_header, text="Главный редактор локальных заметок JARVIS. Здесь можно вести мысли, быстрые записи и любые текстовые черновики.", bg=CARD, fg=MUTED, font=("Segoe UI", 10), wraplength=680, justify="left").pack(anchor="w", pady=(4, 0))

        notes_feed = tk.Frame(notes_card, bg=PANEL_2, highlightthickness=1, highlightbackground=BORDER)
        notes_feed.pack(fill="x", padx=16, pady=(0, 10))
        nf_head = tk.Frame(notes_feed, bg=PANEL_2)
        nf_head.pack(fill="x", padx=12, pady=(10, 4))
        tk.Label(nf_head, text="Лента напоминаний", bg=PANEL_2, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(nf_head, textvariable=self.reminder_status_var, bg=PANEL_2, fg=ACCENT, font=("Segoe UI", 9, "bold")).pack(side="right")
        self.reminders_notes_feed_label = tk.Label(notes_feed, textvariable=self.reminder_feed_short_var, bg=BG, fg=TEXT, justify="left", anchor="w", font=("Consolas", 10), wraplength=760)
        self.reminders_notes_feed_label.pack(fill="x", padx=12, pady=(0, 6))
        self.reminders_notes_feed_listbox = tk.Listbox(notes_feed, height=4, bg=BG, fg=TEXT, relief="flat", bd=0, highlightthickness=0, activestyle="none")
        self.reminders_notes_feed_listbox.pack(fill="x", padx=12, pady=(0, 8))
        notes_feed_btns = tk.Frame(notes_feed, bg=PANEL_2)
        notes_feed_btns.pack(fill="x", padx=12, pady=(0, 10))
        tk.Button(notes_feed_btns, text="Обновить напоминания", command=self.refresh_reminders_ui, bg=CARD_ALT, fg=TEXT, relief="flat", bd=0, cursor="hand2", pady=8).pack(side="left")
        tk.Button(notes_feed_btns, text="Удалить последнее", command=self.delete_last_reminder, bg=CARD_ALT, fg=TEXT, relief="flat", bd=0, cursor="hand2", pady=8).pack(side="left", padx=(8, 0))

        self.notes_text = tk.Text(notes_card, bg=BG, fg=TEXT, insertbackground=TEXT, relief="flat", bd=0, font=("Consolas", 11), wrap="word")
        self.notes_text.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        mem_controls = tk.Frame(notes_card, bg=CARD)
        mem_controls.pack(fill="x", padx=16, pady=(0, 16))
        for title, cmd in [("Обновить", self.load_notes), ("Сохранить как TXT", self.export_notes), ("Сохранить здесь", self.save_notes_from_editor)]:
            tk.Button(mem_controls, text=title, command=cmd, bg=PANEL_2, fg=TEXT, activebackground=CARD_ALT, activeforeground=ACCENT, relief="flat", bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2", padx=12, pady=10).pack(side="left", padx=(0, 8))

        tk.Label(side, text="Профиль памяти", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(side, text="Фразы вроде «запомни что меня зовут...», «запомни мой ник...» и команды памяти теперь собраны отдельно и читаются как полноценный профиль.", bg=CARD_ALT, fg=MUTED, justify="left", font=("Segoe UI", 10), wraplength=280).pack(anchor="w", padx=16)

        profile_box = tk.Frame(side, bg=PANEL_2, highlightthickness=1, highlightbackground=BORDER)
        profile_box.pack(fill="x", padx=16, pady=(12, 10))
        tk.Label(profile_box, text="Профиль", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(profile_box, textvariable=self.profile_name_var, bg=PANEL_2, fg=ACCENT_2, font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=12, pady=(0, 12))

        tk.Label(side, text="Поиск по памяти", bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(2, 0))
        self.memory_search_var = tk.StringVar(value="")
        tk.Entry(side, textvariable=self.memory_search_var, font=("Segoe UI", 10), bg=BG, fg=TEXT, insertbackground=TEXT, relief="flat", bd=0).pack(fill="x", padx=16, pady=(8, 6), ipady=7)
        self.memory_listbox = tk.Listbox(side, bg=BG, fg=TEXT, relief="flat", bd=0, highlightthickness=0, activestyle="none", height=5)
        self.memory_listbox.pack(fill="x", padx=16, pady=(0, 8))

        mem_btns = tk.Frame(side, bg=CARD_ALT)
        mem_btns.pack(fill="x", padx=16, pady=(0, 10))
        tk.Button(mem_btns, text="Обновить память", command=self.refresh_memory_ui, bg=PANEL_2, fg=TEXT, relief="flat", bd=0, cursor="hand2", pady=9).pack(fill="x", pady=(0, 6))
        tk.Button(mem_btns, text="Удалить факт", command=self.delete_selected_memory_fact, bg=PANEL_2, fg=TEXT, relief="flat", bd=0, cursor="hand2", pady=9).pack(fill="x")

        rem_box = tk.Frame(side, bg=PANEL_2, highlightthickness=1, highlightbackground=BORDER)
        rem_box.pack(fill="both", expand=True, padx=16, pady=(8, 10))
        tk.Label(rem_box, text="Очередь напоминаний", bg=PANEL_2, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(rem_box, textvariable=self.reminder_status_var, bg=PANEL_2, fg=ACCENT, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12)
        tk.Label(rem_box, text="Активные локальные напоминания и повторяющиеся задачи, которые JARVIS держит у себя в памяти.", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9), wraplength=260, justify="left").pack(anchor="w", padx=12, pady=(0, 6))
        self.reminders_preview = tk.Text(rem_box, height=5, bg=BG, fg=TEXT, relief="flat", bd=0, highlightthickness=0, wrap="word", insertbackground=TEXT)
        self.reminders_preview.pack(fill="x", padx=12, pady=(4, 8))
        self.reminders_preview.configure(state="disabled")
        self.reminders_listbox = tk.Listbox(rem_box, height=4, bg=BG, fg=TEXT, relief="flat", bd=0, highlightthickness=0, activestyle="none")
        self.reminders_listbox.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        btns = tk.Frame(rem_box, bg=PANEL_2)
        btns.pack(fill="x", padx=12, pady=(0, 12))
        tk.Button(btns, text="Обновить напоминания", command=self.refresh_reminders_ui, bg=CARD_ALT, fg=TEXT, relief="flat", bd=0, cursor="hand2", pady=9).pack(fill="x", pady=(0, 6))
        tk.Button(btns, text="Удалить последнее", command=self.delete_last_reminder, bg=CARD_ALT, fg=TEXT, relief="flat", bd=0, cursor="hand2", pady=9).pack(fill="x", pady=(0, 6))
        tk.Button(btns, text="Удалить выбранное", command=self.delete_selected_reminder, bg=CARD_ALT, fg=TEXT, relief="flat", bd=0, cursor="hand2", pady=9).pack(fill="x")



    def build_palette_page(self):
        page = tk.Frame(self.page_container, bg=BG)
        self.pages["palette"] = page

        self.section_title(page, "Палитра команд", "Глобальный поиск по страницам, элементам быстрого запуска, псевдонимам, системным действиям и готовым командам JARVIS.")

        hero = self.card(page, bg=CARD_ALT)
        hero.pack(fill="x", pady=(12, 10))
        hero_inner = tk.Frame(hero, bg=CARD_ALT)
        hero_inner.pack(fill="both", expand=True, padx=18, pady=16)
        left = tk.Frame(hero_inner, bg=CARD_ALT)
        left.pack(side="left", fill="both", expand=True)
        tk.Label(left, text="ПОИСК ПО JARVIS", bg=CARD_ALT, fg=ACCENT, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left, text="Найди и выполни почти всё из одного окна", bg=CARD_ALT, fg=TEXT, font=("Segoe UI Semibold", 22)).pack(anchor="w", pady=(2, 0))
        tk.Label(left, text="Ищет страницы интерфейса, любимые приложения и сайты, команды-псевдонимы, системные действия и частые готовые фразы. Enter — выполнить. Ctrl+K — открыть всплывающую палитру поверх любого экрана.", bg=CARD_ALT, fg=MUTED, wraplength=780, justify="left", font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 10))
        pills = tk.Frame(left, bg=CARD_ALT)
        pills.pack(anchor="w")
        self.pill(pills, "Ctrl+K", fg=ACCENT).pack(side="left", padx=(0, 8))
        self.pill(pills, "Страницы", fg=ACCENT_2).pack(side="left", padx=(0, 8))
        self.pill(pills, "Запуск", fg=WARN).pack(side="left", padx=(0, 8))
        self.pill(pills, "Системные действия", fg="#ff9fb2").pack(side="left")

        right = tk.Frame(hero_inner, bg=CARD_ALT, width=300)
        right.pack(side="left", fill="y", padx=(16, 0))
        right.pack_propagate(False)
        right_card = tk.Frame(right, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        right_card.pack(fill="both", expand=True)
        tk.Label(right_card, text="Состояние поиска", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(12, 0))
        tk.Label(right_card, textvariable=self.palette_status_var, bg=PANEL_2, fg=TEXT, font=("Segoe UI", 11, "bold"), wraplength=250, justify="left").pack(anchor="w", padx=14, pady=(6, 10))
        self.make_shell_badge(right_card, "Результаты", self.palette_result_count_var.get(), ACCENT_2).pack(anchor="w", padx=14, pady=(0, 8))
        tk.Label(right_card, text="Подсказка: введите «ютуб», «оверлей», «трей», «настройки», «рабочий режим», псевдоним или имя приложения.", bg=PANEL_2, fg=MUTED, wraplength=250, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(0, 14))

        search_shell = tk.Frame(page, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        search_shell.pack(fill="x", pady=(0, 10))
        top = tk.Frame(search_shell, bg=PANEL)
        top.pack(fill="x", padx=14, pady=(14, 10))
        tk.Label(top, text="⌕", bg=PANEL, fg=ACCENT, font=("Segoe UI Symbol", 18)).pack(side="left", padx=(0, 10))
        self.palette_search_entry = tk.Entry(top, textvariable=self.palette_query_var)
        self.style_entry_widget(self.palette_search_entry, font=("Segoe UI", 13), bg_override=PANEL_2)
        self.palette_search_entry.pack(side="left", fill="x", expand=True)
        self.palette_search_entry.bind("<KeyRelease>", lambda e: self.refresh_command_palette_page())
        self.palette_search_entry.bind("<Return>", lambda e: self.execute_command_palette_selection())
        tk.Button(top, text="Очистить", command=self.clear_palette_search, bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2", padx=12, pady=8, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(10, 8))
        tk.Button(top, text="⌘ В отдельном окне", command=self.toggle_command_palette, bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2", padx=12, pady=8, font=("Segoe UI", 10, "bold")).pack(side="left")

        chips = tk.Frame(search_shell, bg=PANEL)
        chips.pack(fill="x", padx=14, pady=(0, 14))
        for cmd in ["overlay", "tray", "settings", "ютуб", "рабочий режим", "покажи напоминания"]:
            tk.Button(chips, text=cmd, command=lambda c=cmd: self.seed_palette_search(c), bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2", padx=10, pady=6, font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))

        body = tk.Frame(page, bg=BG)
        body.pack(fill="both", expand=True)

        left_col = tk.Frame(body, bg=BG)
        left_col.pack(side="left", fill="both", expand=True)
        right_col = tk.Frame(body, bg=BG, width=330)
        right_col.pack(side="left", fill="y", padx=(10, 0))
        right_col.pack_propagate(False)

        list_card = self.card(left_col, bg=CARD_ALT)
        list_card.pack(fill="both", expand=True)
        head = tk.Frame(list_card, bg=CARD_ALT)
        head.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(head, text="Результаты поиска", bg=CARD_ALT, fg=TEXT, font=("Segoe UI Semibold", 18)).pack(side="left")
        tk.Label(head, textvariable=self.palette_result_count_var, bg=CARD_ALT, fg=ACCENT_2, font=("Segoe UI", 10, "bold")).pack(side="right")
        self.palette_results_listbox = tk.Listbox(list_card, height=18)
        self.style_listbox_widget(self.palette_results_listbox, font=("Segoe UI", 11))
        self.palette_results_listbox.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        self.palette_results_listbox.bind("<<ListboxSelect>>", lambda e: self.update_palette_details())
        self.palette_results_listbox.bind("<Double-Button-1>", lambda e: self.execute_command_palette_selection())
        self.palette_results_listbox.bind("<Return>", lambda e: self.execute_command_palette_selection())

        right_card = self.card(right_col, bg=CARD_ALT)
        right_card.pack(fill="both", expand=True)
        tk.Label(right_card, text="Предпросмотр действия", bg=CARD_ALT, fg=TEXT, font=("Segoe UI Semibold", 18)).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(right_card, text="Что именно сработает по выделенному результату.", bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=16)
        self.palette_preview_title_var = tk.StringVar(value="Ничего не выбрано")
        self.palette_preview_meta_var = tk.StringVar(value="Выбери результат слева")
        self.palette_preview_desc_var = tk.StringVar(value="Здесь появится описание действия, страницы или команды.")
        tk.Label(right_card, textvariable=self.palette_preview_title_var, bg=CARD_ALT, fg=ACCENT, font=("Segoe UI", 14, "bold"), wraplength=280, justify="left").pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(right_card, textvariable=self.palette_preview_meta_var, bg=CARD_ALT, fg=WARN, font=("Segoe UI", 10, "bold"), wraplength=280, justify="left").pack(anchor="w", padx=16)
        tk.Label(right_card, textvariable=self.palette_preview_desc_var, bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 10), wraplength=280, justify="left").pack(anchor="w", padx=16, pady=(8, 14))
        action_row = tk.Frame(right_card, bg=CARD_ALT)
        action_row.pack(fill="x", padx=16, pady=(0, 10))
        tk.Button(action_row, text="▶ Выполнить", command=self.execute_command_palette_selection, bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2", padx=12, pady=8, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 8))
        tk.Button(action_row, text="⌘ В отдельном окне", command=self.toggle_command_palette, bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2", padx=12, pady=8, font=("Segoe UI", 10, "bold")).pack(side="left")
        guide = tk.Frame(right_card, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        guide.pack(fill="x", padx=16, pady=(0, 16))
        tk.Label(guide, text="Что ищется", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(10, 0))
        tk.Label(guide, text="• страницы интерфейса\n• приложения, сайты\n• команды-псевдонимы\n• системные действия\n• готовые команды JARVIS", bg=PANEL_2, fg=TEXT, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=12, pady=(6, 12))

        self.refresh_command_palette_page()


    def palette_page_definitions(self):
        return [
            {"name": "Панель", "query": "панель dashboard главная", "type": "page", "value": "dashboard", "desc": "Главная панель с командной строкой и текущими статусами."},
            {"name": "Команды и лог", "query": "команды лог chat console", "type": "page", "value": "chat", "desc": "Текстовые команды, лог и ручной ввод в ядро JARVIS."},
            {"name": "Быстрый запуск", "query": "launcher hub приложения сайты alias псевдонимы", "type": "page", "value": "launch", "desc": "Плитки запуска, псевдонимы, сайты и приложения."},
            {"name": "Центр управления", "query": "режимы hud control", "type": "page", "value": "control", "desc": "Режимы интерфейса, HUD и быстрые команды."},
            {"name": "Память", "query": "memory память заметки reminders facts", "type": "page", "value": "memory", "desc": "Память, заметки, напоминания и профиль пользователя."},
            {"name": "Палитра команд", "query": "palette поиск global search", "type": "page", "value": "palette", "desc": "Глобальный поиск по страницам, командам и действиям JARVIS."},
            {"name": "Настройки", "query": "settings настройки конфиг overlay tray voice", "type": "page", "value": "settings", "desc": "Пути, голос, overlay, tray и автозапуск."},
            {"name": "Журнал событий", "query": "system journal notifications recovery autosave tray", "type": "page", "value": "system", "desc": "Журнал событий, восстановление сессии, работа в трее и экспорт логов."},
        ]


    def get_command_palette_items(self, query=""):
        items = []
        for page in self.palette_page_definitions():
            items.append(page)
        for name, path in self.launcher_ordered_items("apps"):
            items.append({"name": name, "query": f"{name} app приложение launch exe {path}", "type": "app", "value": name, "desc": f"Запуск приложения из Быстрый запуск: {path}"})
        for name, url in self.launcher_ordered_items("sites"):
            items.append({"name": name, "query": f"{name} site сайт open url {url}", "type": "site", "value": name, "desc": f"Открытие сайта из Быстрый запуск: {url}"})
        for alias, target in (self.cfg.get("aliases", {}) or {}).items():
            items.append({"name": alias, "query": f"{alias} alias команда {target}", "type": "alias", "value": alias, "desc": f"Псевдоним → {target}"})
        actions = [
            ("Быстрая панель", "action", "quickbar", "quick bar быстрая панель popup command bar overlay", "Открыть или скрыть плавающую командную панель."),
            ("Мини-оверлей", "action", "overlay", "overlay mini оверлей окно", "Включить или выключить мини-оверлей."),
            ("Скрыть в трей", "action", "tray_hide", "tray hide свернуть в трей", "Спрятать JARVIS в системный трей."),
            ("Вернуть из трея", "action", "tray_restore", "tray restore вернуть окно", "Вернуть окно JARVIS из трея."),
            ("Старт голоса", "action", "voice_start", "voice start голос старт", "Запустить распознавание голоса."),
            ("Стоп голоса", "action", "voice_stop", "voice stop голос стоп", "Остановить распознавание голоса."),
            ("Восстановление сессии", "action", "recovery", "recovery startup autosave session restore", "Открыть восстановление прошлой сессии."),
            ("Проверить данные", "action", "health", "health data repair cleanup diagnostics", "Открыть проверку целостности данных."),
        ]
        for name, typ, value, q, desc in actions:
            items.append({"name": name, "query": q, "type": typ, "value": value, "desc": desc})
        commands = [
            ("рабочий режим", "cmd", "рабочий режим", "Готовая команда: рабочий режим."),
            ("игровой режим", "cmd", "игровой режим", "Готовая команда: игровой режим."),
            ("покажи напоминания", "cmd", "покажи напоминания", "Открыть и озвучить очередь активных напоминаний."),
            ("сколько времени", "cmd", "сколько времени", "Быстрый запрос текущего времени."),
            ("команды", "cmd", "команды", "Показать справку по командам JARVIS."),
        ]
        for name, typ, value, desc in commands:
            items.append({"name": name, "query": f"{name} command команда", "type": typ, "value": value, "desc": desc})
        q = normalize_text(query)
        if not q:
            return items
        scored = []
        for item in items:
            hay = normalize_text(" ".join([item.get("name", ""), item.get("query", ""), item.get("desc", "")]))
            score = 0
            if q in normalize_text(item.get("name", "")):
                score += 5
            if q in hay:
                score += 3
            parts = [part for part in q.split() if part]
            score += sum(1 for part in parts if part in hay)
            if score > 0:
                scored.append((score, item))
        scored.sort(key=lambda x: (-x[0], x[1].get("name", "")))
        return [item for _score, item in scored[:120]]


    def palette_item_label(self, item):
        icons = {"page": "⌂", "app": "▣", "site": "◍", "alias": "↦", "action": "⚙", "cmd": "⌘"}
        suffix = {"page": "СТРАНИЦА", "app": "ПРИЛОЖЕНИЕ", "site": "САЙТ", "alias": "ПСЕВДОНИМ", "action": "ДЕЙСТВИЕ", "cmd": "КОМАНДА"}.get(item.get("type"), "ITEM")
        return f"{icons.get(item.get('type'), '•')}  {item.get('name')}   ·   {suffix}"


    def update_palette_details(self):
        items = getattr(self, "command_palette_page_items", [])
        lb = getattr(self, "palette_results_listbox", None)
        if lb is None or not items:
            self.palette_preview_title_var.set("Ничего не выбрано")
            self.palette_preview_meta_var.set("Выбери результат слева")
            self.palette_preview_desc_var.set("Здесь появится описание действия, страницы или команды.")
            return
        sel = lb.curselection()
        if not sel:
            return
        item = items[sel[0]]
        meta = {"page": "Переход на страницу", "app": "Запуск приложения", "site": "Открытие сайта", "alias": "Команда-псевдоним", "action": "Системное действие", "cmd": "Готовая команда"}.get(item.get("type"), "Элемент")
        self.palette_preview_title_var.set(item.get("name", "—"))
        self.palette_preview_meta_var.set(meta)
        self.palette_preview_desc_var.set(item.get("desc", ""))
        self.palette_status_var.set(f"Выбрано: {item.get('name', '—')}")


    def refresh_command_palette_page(self):
        items = self.get_command_palette_items(self.palette_query_var.get())
        self.command_palette_page_items = items
        lb = getattr(self, "palette_results_listbox", None)
        if lb is None:
            return
        lb.delete(0, "end")
        for item in items:
            lb.insert("end", self.palette_item_label(item))
        count_text = f"{len(items)} результатов" if len(items) != 1 else "1 результат"
        self.palette_result_count_var.set(count_text)
        if items:
            lb.selection_clear(0, "end")
            lb.selection_set(0)
            self.update_palette_details()
        else:
            self.palette_preview_title_var.set("Ничего не найдено")
            self.palette_preview_meta_var.set("Измени запрос")
            self.palette_preview_desc_var.set("Попробуй имя страницы, псевдоним, сайт, приложение или системное действие.")
            self.palette_status_var.set("Нет совпадений")


    def clear_palette_search(self):
        self.palette_query_var.set("")
        self.refresh_command_palette_page()
        if hasattr(self, "palette_search_entry") and self.palette_search_entry is not None:
            self.palette_search_entry.focus_set()


    def seed_palette_search(self, text):
        self.palette_query_var.set(text)
        self.refresh_command_palette_page()
        if hasattr(self, "palette_search_entry") and self.palette_search_entry is not None:
            self.palette_search_entry.focus_set()


    def execute_palette_item(self, item):
        if not item:
            return
        typ = item.get("type")
        value = item.get("value")
        if typ == "page":
            self.show_page(value)
            self.footer_var.set(f"Открыта страница: {item.get('name')}")
            self.append_system_event("palette", f"Открыта страница через палитру: {item.get('name')}", toast=False)
            return
        if typ == "app":
            self.launch_named_app(value)
            self.append_system_event("palette", f"Запуск приложения через палитру: {value}", toast=False)
            return
        if typ == "site":
            self.launch_named_site(value)
            self.append_system_event("palette", f"Открыт сайт через палитру: {value}", toast=False)
            return
        if typ == "alias":
            self.apply_alias_command(value)
            self.append_system_event("palette", f"Псевдоним через палитру: {value}", toast=False)
            return
        if typ == "action":
            if value == "quickbar":
                self.toggle_quickbar()
            elif value == "overlay":
                self.toggle_overlay()
            elif value == "tray_hide":
                self.hide_to_tray()
            elif value == "tray_restore":
                self.restore_from_tray()
            elif value == "voice_start":
                self.start_voice()
            elif value == "voice_stop":
                self.stop_voice()
            elif value == "recovery":
                self.startup_recovery_flow()
            elif value == "health":
                self.show_page("settings")
                self.root.after(150, self.run_data_health_check)
            self.append_system_event("palette", f"Системное действие через палитру: {item.get('name')}", toast=False)
            return
        if typ == "cmd":
            self.handle_command(value, source="palette")
            self.append_system_event("palette", f"Команда через палитру: {value}", toast=False)


    def execute_command_palette_selection(self):
        lb = getattr(self, "palette_results_listbox", None)
        items = getattr(self, "command_palette_page_items", [])
        if lb is None or not items:
            return
        sel = lb.curselection()
        if not sel:
            return
        self.execute_palette_item(items[sel[0]])


    def refresh_command_palette_popup(self, query=""):
        items = self.get_command_palette_items(query)
        self.command_palette_popup_items = items
        lb = getattr(self, "command_palette_listbox", None)
        if lb is None:
            return
        lb.delete(0, "end")
        for item in items[:40]:
            lb.insert("end", self.palette_item_label(item))
        if items:
            lb.selection_set(0)
        hint = getattr(self, "command_palette_hint_var", None)
        if hint is not None:
            hint.set(f"{len(items)} совпадений • Enter — выполнить • Esc — закрыть")


    def command_palette_popup_execute(self, event=None):
        lb = getattr(self, "command_palette_listbox", None)
        items = getattr(self, "command_palette_popup_items", [])
        if lb is None or not items:
            return
        sel = lb.curselection()
        if not sel:
            return
        self.execute_palette_item(items[sel[0]])
        self.close_command_palette()


    def close_command_palette(self, event=None):
        win = getattr(self, "command_palette_window", None)
        if win is not None:
            try:
                win.destroy()
            except Exception:
                pass
        self.command_palette_window = None
        self.command_palette_entry = None
        self.command_palette_listbox = None
        self.command_palette_hint_var = None


    def toggle_command_palette(self):
        if self.command_palette_window is not None and self.command_palette_window.winfo_exists():
            self.close_command_palette()
            return
        win = tk.Toplevel(self.root)
        self.command_palette_window = win
        win.title("JARVIS Палитра команд")
        win.transient(self.root)
        win.configure(bg=BORDER)
        win.attributes("-topmost", True)
        width, height = 760, 520
        rx = self.root.winfo_rootx() + max(40, (self.root.winfo_width() - width) // 2)
        ry = self.root.winfo_rooty() + 90
        win.geometry(f"{width}x{height}+{rx}+{ry}")
        shell = tk.Frame(win, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        shell.pack(fill="both", expand=True)
        top = tk.Frame(shell, bg=CARD_ALT)
        top.pack(fill="x", padx=18, pady=(16, 12))
        tk.Label(top, text="⌘", bg=CARD_ALT, fg=ACCENT, font=("Segoe UI Symbol", 24)).pack(side="left", padx=(0, 10))
        entry = tk.Entry(top)
        self.command_palette_entry = entry
        self.style_entry_widget(entry, font=("Segoe UI", 14), bg_override=PANEL_2)
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<KeyRelease>", lambda e: self.refresh_command_palette_popup(entry.get()))
        entry.bind("<Return>", self.command_palette_popup_execute)
        entry.bind("<Escape>", self.close_command_palette)
        tk.Button(top, text="×", command=self.close_command_palette, bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2", padx=12, pady=8, font=("Segoe UI", 12, "bold")).pack(side="left", padx=(10, 0))
        chips = tk.Frame(shell, bg=CARD_ALT)
        chips.pack(fill="x", padx=18, pady=(0, 10))
        for cmd in ["settings", "ютуб", "overlay", "tray", "рабочий режим", "health"]:
            tk.Button(chips, text=cmd, command=lambda c=cmd: (entry.delete(0, "end"), entry.insert(0, c), self.refresh_command_palette_popup(c)), bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2", padx=10, pady=6, font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        lb = tk.Listbox(shell, height=16)
        self.command_palette_listbox = lb
        self.style_listbox_widget(lb, font=("Segoe UI", 11))
        lb.pack(fill="both", expand=True, padx=18, pady=(0, 12))
        lb.bind("<Double-Button-1>", self.command_palette_popup_execute)
        lb.bind("<Return>", self.command_palette_popup_execute)
        lb.bind("<Escape>", self.close_command_palette)
        self.command_palette_hint_var = tk.StringVar(value="Начни вводить команду или имя страницы")
        bottom = tk.Frame(shell, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        bottom.pack(fill="x", padx=18, pady=(0, 18))
        tk.Label(bottom, textvariable=self.command_palette_hint_var, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(side="left", padx=12, pady=10)
        self.make_shell_badge(bottom, "Клавиши", "Ctrl+K", ACCENT).pack(side="right", padx=(8, 12), pady=6)
        self.make_shell_badge(bottom, "Поиск", "по всему JARVIS", ACCENT_2).pack(side="right", padx=(8, 0), pady=6)
        self.refresh_command_palette_popup("")
        entry.focus_set()
        self.append_system_event("palette", "Палитра команд открыта в отдельном окне", toast=False)


    def bind_hotkeys(self):
        self.root.bind("<F6>", lambda e: self.toggle_quickbar())
        self.root.bind("<Control-k>", lambda e: self.toggle_command_palette())
        self.root.bind("<F8>", lambda e: self.toggle_voice_hotkey())
        self.root.bind("<Escape>", lambda e: self.stop_speaking())
        self.root.bind("<F9>", lambda e: self.toggle_overlay())
        self.root.bind("<F11>", lambda e: self.toggle_hud_mode())
        self.root.bind("<Control-minus>", lambda e: self.step_window_opacity(-0.04))
        self.root.bind("<Control-equal>", lambda e: self.step_window_opacity(0.04))
        self.root.bind("<Control-plus>", lambda e: self.step_window_opacity(0.04))
        self.root.bind("<Control-Shift-minus>", lambda e: self.step_hud_opacity(-0.04))
        self.root.bind("<Control-underscore>", lambda e: self.step_hud_opacity(-0.04))
        self.root.bind("<Control-Shift-equal>", lambda e: self.step_hud_opacity(0.04))
        self.root.bind("<Control-Shift-plus>", lambda e: self.step_hud_opacity(0.04))
        self.root.bind("<Control-Alt-Key-1>", lambda e: self.apply_glass_preset("ghost"))
        self.root.bind("<Control-Alt-Key-2>", lambda e: self.apply_glass_preset("glass"))
        self.root.bind("<Control-Alt-Key-3>", lambda e: self.apply_glass_preset("solid"))


    def toggle_voice_hotkey(self):
        if self.voice_worker and self.voice_worker.is_alive():
            self.stop_voice()
        else:
            self.start_voice()


    def show_startup_splash(self):
        splash = tk.Toplevel(self.root)
        splash.overrideredirect(True)
        splash.attributes("-topmost", True)
        try:
            splash.attributes("-alpha", self.clamp_opacity(self.splash_opacity_var.get()))
        except Exception:
            pass
        splash.configure(bg=BG)
        width, height = 520, 220
        x = max(100, (self.root.winfo_screenwidth() - width) // 2)
        y = max(80, (self.root.winfo_screenheight() - height) // 2)
        splash.geometry(f"{width}x{height}+{x}+{y}")
        box = tk.Frame(splash, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        box.pack(fill="both", expand=True, padx=8, pady=8)
        tk.Label(box, text=f"JARVIS {APP_VERSION}", bg=PANEL, fg=ACCENT, font=("Segoe UI", 28, "bold")).pack(pady=(34, 6))
        tk.Label(box, text="Голосовой помощник • команды • напоминания", bg=PANEL, fg=TEXT, font=("Segoe UI", 12)).pack()
        tk.Label(box, text=f"Пользователь: {self.cfg.get('user_name', 'Пользователь')}", bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).pack(pady=(10, 0))
        splash.after(1400, splash.destroy)


    def show_page(self, key):
        same_page = self.current_page == key
        if not same_page:
            if self.current_page and self.current_page in self.pages:
                self.pages[self.current_page].pack_forget()
            self.pages[key].pack(fill="both", expand=True)
            self.current_page = key
            for name, btn in self.page_buttons.items():
                active = name == key
                btn.configure(bg=PANEL_2 if active else CARD_ALT, fg=ACCENT if active else TEXT, highlightbackground=ACCENT if active else BORDER)
        if key == "chat":
            self.entry.focus_set()
        elif key == "dashboard":
            self.dashboard_entry.focus_set()
        elif key == "palette":
            if hasattr(self, "palette_search_entry") and self.palette_search_entry is not None:
                self.palette_search_entry.focus_set()
                self.refresh_command_palette_page()
        elif key == "system":
            self.mark_system_events_read()
        elif key == "memory":
            self.load_notes()
            self.refresh_reminders_ui()
        self.save_session_state(silent=True)

    def update_clock(self):
        self.clock_var.set(datetime.now().strftime("%H:%M:%S  •  %d.%m.%Y"))
        if self.overlay_window is not None:
            try:
                self.overlay_window.title(f"JARVIS overlay • {datetime.now().strftime('%H:%M:%S')}")
            except Exception:
                pass
        self.root.after(1000, self.update_clock)


    def build_session_payload(self):
        state = {
            "version": APP_VERSION,
            "saved_at": now_iso(),
            "current_page": self.current_page or "dashboard",
            "root_geometry": self.root.winfo_geometry(),
            "main_topmost": bool(self.always_on_top_var.get()),
            "overlay_enabled": bool(self.overlay_var.get()),
            "quickbar_open": bool(self.quickbar_window is not None and self.quickbar_window.winfo_exists()),
            "quickbar_topmost": bool(self.quick_bar_topmost_var.get()),
            "launcher_search": self.launcher_search_var.get().strip() if hasattr(self, "launcher_search_var") else "",
        }
        if state["quickbar_open"] and self.quickbar_window is not None:
            try:
                state["quickbar_geometry"] = self.quickbar_window.winfo_geometry()
            except Exception:
                state["quickbar_geometry"] = ""
            try:
                state["quickbar_text"] = self.quickbar_entry.get().strip() if self.quickbar_entry is not None else ""
            except Exception:
                state["quickbar_text"] = ""
        return state


    def save_session_state(self, silent=True):
        try:
            SESSION_STATE_PATH.write_text(json.dumps(self.build_session_payload(), ensure_ascii=False, indent=2), encoding="utf-8")
            self.append_system_event("session", "UI-сессия сохранена" if silent else "UI-сессия сохранена вручную", toast=not silent)
            if not silent:
                self.footer_var.set("Сессия сохранена")
        except Exception as e:
            if not silent:
                self.footer_var.set(f"Не удалось сохранить сессию: {e}")
            self.append_system_event("session", f"Ошибка сохранения UI-сессии: {e}", toast=not silent)


    def save_session_state_manual(self):
        self.save_ui_config()
        self.save_session_state(silent=False)


    def restore_session_state(self, silent=True):
        if not SESSION_STATE_PATH.exists():
            if not silent:
                self.footer_var.set("Сохранённая сессия не найдена")
            self.append_system_event("session", "Сохранённая UI-сессия не найдена", toast=not silent)
            return False
        try:
            state = json.loads(SESSION_STATE_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            if not silent:
                self.footer_var.set(f"Не удалось прочитать сессию: {e}")
            self.append_system_event("session", f"Ошибка чтения UI-сессии: {e}", toast=not silent)
            return False

        page = state.get("current_page")
        if page in self.pages:
            self.show_page(page)
        geometry = str(state.get("root_geometry", "")).strip()
        if geometry:
            try:
                self.root.geometry(geometry)
            except Exception:
                pass
        search_value = str(state.get("launcher_search", "")).strip()
        if hasattr(self, "launcher_search_var"):
            self.launcher_search_var.set(search_value)
            try:
                self.refresh_launcher_ui()
            except Exception:
                pass
        self.always_on_top_var.set(bool(state.get("main_topmost", self.always_on_top_var.get())))
        self.quick_bar_topmost_var.set(bool(state.get("quickbar_topmost", self.quick_bar_topmost_var.get())))
        self.apply_topmost_flags()

        want_overlay = bool(state.get("overlay_enabled", self.overlay_var.get()))
        self.overlay_var.set(want_overlay)
        if want_overlay and self.overlay_window is None:
            self.toggle_overlay(force=True)
        elif not want_overlay and self.overlay_window is not None:
            self.toggle_overlay(force=False)

        want_quickbar = bool(state.get("quickbar_open", False))
        has_quickbar = bool(self.quickbar_window is not None and self.quickbar_window.winfo_exists())
        if want_quickbar and not has_quickbar:
            self.toggle_quickbar()
        elif not want_quickbar and has_quickbar:
            self.toggle_quickbar()

        if want_quickbar and self.quickbar_window is not None:
            qb_geometry = str(state.get("quickbar_geometry", "")).strip()
            if qb_geometry:
                try:
                    self.quickbar_window.geometry(qb_geometry)
                except Exception:
                    pass
            qb_text = str(state.get("quickbar_text", ""))
            try:
                if self.quickbar_entry is not None:
                    self.quickbar_entry.delete(0, "end")
                    self.quickbar_entry.insert(0, qb_text)
            except Exception:
                pass
            try:
                self.on_quickbar_topmost_toggle()
            except Exception:
                pass

        self.append_system_event("session", "UI-сессия восстановлена", toast=not silent)
        if not silent:
            self.footer_var.set("Последняя сессия восстановлена")
        return True


    def restore_session_state_manual(self):
        self.restore_session_state(silent=False)


    def restore_last_session_on_startup(self):
        if bool(self.restore_last_session_var.get()):
            self.restore_session_state(silent=True)


    def startup_recovery_flow(self):
        if getattr(self, "start_minimized_var", None) is not None and bool(self.start_minimized_var.get()):
            self.restore_last_session_on_startup()
            return
        has_session = SESSION_STATE_PATH.exists()
        has_autosave = AUTOSAVE_PROFILE_PATH.exists()
        if not has_session and not has_autosave:
            self.append_system_event("recovery", "Данные восстановления при старте не найдены", toast=False)
            self.restore_last_session_on_startup()
            return
        if not bool(getattr(self, "startup_recovery_prompt_var", tk.BooleanVar(value=False)).get()):
            self.append_system_event("recovery", "Окно восстановления выключено — применяю обычный старт", toast=False)
            self.restore_last_session_on_startup()
            return
        self.show_startup_recovery_dialog(has_session=has_session, has_autosave=has_autosave)


    def show_startup_recovery_dialog(self, has_session=False, has_autosave=False):
        try:
            if hasattr(self, "startup_recovery_window") and self.startup_recovery_window is not None and self.startup_recovery_window.winfo_exists():
                self.startup_recovery_window.lift()
                self.startup_recovery_window.focus_force()
                return
        except Exception:
            pass

        self.append_system_event("recovery", "Показано окно восстановления при старте", toast=False)
        win, body = self.create_modal_shell("Восстановление сессии", "JARVIS нашёл сохранённую сессию или профиль. Выберите, что восстановить.", width=620, height=430)
        self.startup_recovery_window = win
        win.title("JARVIS — восстановление")
        card = tk.Frame(body, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True)

        info = tk.Frame(card, bg=CARD_ALT)
        info.pack(fill="x", padx=20, pady=(18, 10))
        session_text = f"Сессия UI: {'найдена' if has_session else 'не найдена'}"
        autosave_text = f"Автосохранение профиля: {'найдено' if has_autosave else 'не найдено'}"
        tk.Label(info, text=session_text, bg=CARD_ALT, fg=ACCENT_2 if has_session else MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(info, text=autosave_text, bg=CARD_ALT, fg=ACCENT_2 if has_autosave else MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 0))

        btns = tk.Frame(card, bg=CARD_ALT)
        stats = tk.Frame(card, bg=CARD_ALT)
        stats.pack(fill="x", padx=20, pady=(18, 12))
        self.make_shell_badge(stats, "Состояние интерфейса", "найдена" if has_session else "не найдена", ACCENT_2 if has_session else MUTED).pack(side="left", fill="x", expand=True, padx=(0,8))
        self.make_shell_badge(stats, "Автосохранение профиля", "найден" if has_autosave else "не найден", WARN if has_autosave else MUTED).pack(side="left", fill="x", expand=True)

        btns.pack(fill="x", padx=20, pady=(10, 8))
        tk.Button(btns, text="Восстановить прошлую сессию", state=("normal" if has_session else "disabled"), command=lambda: self._startup_recovery_choice("session"), bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2", padx=12, pady=10, font=("Segoe UI", 10, "bold")).pack(fill="x", pady=(0, 8))
        tk.Button(btns, text="Восстановить автосохранение профиля", state=("normal" if has_autosave else "disabled"), command=lambda: self._startup_recovery_choice("autosave"), bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2", padx=12, pady=10, font=("Segoe UI", 10, "bold")).pack(fill="x", pady=(0, 8))
        tk.Button(btns, text="Поднять всё", state=("normal" if (has_session or has_autosave) else "disabled"), command=lambda: self._startup_recovery_choice("both"), bg=ACCENT, fg="#001420", activebackground="#86e5ff", activeforeground="#001420", relief="flat", bd=0, cursor="hand2", padx=12, pady=10, font=("Segoe UI", 10, "bold")).pack(fill="x", pady=(0, 8))
        tk.Button(btns, text="Чистый старт", command=lambda: self._startup_recovery_choice("clean"), bg="#173048", fg=TEXT, activebackground=CARD, activeforeground=TEXT, relief="flat", bd=0, cursor="hand2", padx=12, pady=10, font=("Segoe UI", 10, "bold")).pack(fill="x")

        bottom = tk.Frame(card, bg=CARD_ALT)
        bottom.pack(fill="x", padx=20, pady=(8, 18))
        tk.Checkbutton(bottom, text="Показывать это окно при старте", variable=self.startup_recovery_prompt_var, bg=CARD_ALT, fg=TEXT, activebackground=CARD_ALT, activeforeground=TEXT, selectcolor=CARD_ALT, font=("Segoe UI", 10)).pack(side="left")
        tk.Button(bottom, text="Закрыть", command=lambda: self._startup_recovery_choice("clean"), bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2", padx=12, pady=8).pack(side="right")
        win.protocol("WM_DELETE_WINDOW", lambda: self._startup_recovery_choice("clean"))


    def _startup_recovery_choice(self, mode="clean"):
        try:
            self.save_ui_config()
        except Exception:
            pass
        self.append_system_event("recovery", f"Выбран recovery-режим: {mode}")
        if mode in {"session", "both"} and SESSION_STATE_PATH.exists():
            self.restore_session_state(silent=True)
        elif mode == "clean":
            self.last_action_var.set("Чистый старт")
        if mode in {"autosave", "both"} and AUTOSAVE_PROFILE_PATH.exists():
            self.restore_autosave_profile()
        elif mode == "session":
            self.post_response("Поднял прошлую UI-сессию.")
        elif mode == "clean":
            self.post_response("Запустил JARVIS без восстановления.")
        try:
            if hasattr(self, "startup_recovery_window") and self.startup_recovery_window is not None:
                self.startup_recovery_window.destroy()
        except Exception:
            pass
        self.startup_recovery_window = None
        try:
            self.root.lift()
            self.root.focus_force()
        except Exception:
            pass


    def session_autosave_tick(self):
        self.save_session_state(silent=True)
        try:
            self.root.after(3000, self.session_autosave_tick)
        except Exception:
            pass


    def build_profile_payload(self):
        return {
            "version": APP_VERSION,
            "exported_at": now_iso(),
            "user_name": self.cfg.get("user_name", ""),
            "favorite_apps": dict(self.cfg.get("favorite_apps", {}) or {}),
            "favorite_sites": dict(self.cfg.get("favorite_sites", {}) or {}),
            "launcher_order_apps": list(self.cfg.get("launcher_order_apps", []) or []),
            "launcher_order_sites": list(self.cfg.get("launcher_order_sites", []) or []),
            "launcher_app_icons": dict(self.cfg.get("launcher_app_icons", {}) or {}),
            "launcher_site_icons": dict(self.cfg.get("launcher_site_icons", {}) or {}),
            "aliases": dict(self.cfg.get("aliases", {}) or {}),
            "notes": NOTES_PATH.read_text(encoding="utf-8") if NOTES_PATH.exists() else "",
            "memory": self.memory,
            "reminders": self.reminders,
        }


    def apply_profile_payload(self, data):
        self.cfg["favorite_apps"] = dict(data.get("favorite_apps", {}) or {})
        self.cfg["favorite_sites"] = dict(data.get("favorite_sites", {}) or {})
        self.cfg["launcher_order_apps"] = list(data.get("launcher_order_apps", []) or [])
        self.cfg["launcher_order_sites"] = list(data.get("launcher_order_sites", []) or [])
        self.cfg["launcher_app_icons"] = dict(data.get("launcher_app_icons", {}) or {})
        self.cfg["launcher_site_icons"] = dict(data.get("launcher_site_icons", {}) or {})
        self.cfg["aliases"] = dict(data.get("aliases", {}) or {})
        save_config(self.cfg)
        notes = data.get("notes")
        if isinstance(notes, str):
            NOTES_PATH.write_text(notes, encoding="utf-8")
            self.load_notes()
        mem = data.get("memory")
        if isinstance(mem, dict):
            self.memory = mem
            save_memory_profile(self.memory)
            self.refresh_memory_ui()
        rems = data.get("reminders")
        if isinstance(rems, list):
            self.reminders = rems
            save_reminders(self.reminders)
            self.refresh_reminders_ui()
        self.refresh_launcher_ui()
        self.update_stats()


    def quick_backup_profile(self):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = BACKUP_DIR / f"jarvis_profile_backup_{stamp}.json"
        try:
            target.write_text(json.dumps(self.build_profile_payload(), ensure_ascii=False, indent=2), encoding="utf-8")
            self.last_action_var.set("Создана резервная копия профиля")
            self.append_system_event("backup", f"Создана резервная копия профиля: {target.name}")
            self.post_response(f"Бэкап профиля создан: {target.name}")
        except Exception as exc:
            self.post_log(f"[backup] ошибка: {exc}")
            self.append_system_event("backup", f"Ошибка создания резервной копии: {exc}")
            self.post_response("Не смог создать резервную копию профиля.")


    def autosave_profile_tick(self):
        try:
            if self.profile_autosave_var.get():
                AUTOSAVE_PROFILE_PATH.write_text(json.dumps(self.build_profile_payload(), ensure_ascii=False, indent=2), encoding="utf-8")
                self.footer_var.set(f"Автосейв профиля: {datetime.now().strftime('%H:%M:%S')}")
                self.append_system_event("autosave", "Профиль автоматически сохранён", toast=False)
        except Exception as exc:
            self.post_log(f"[autosave] ошибка: {exc}")
            self.append_system_event("autosave", f"Ошибка автосохранения профиля: {exc}")
        finally:
            try:
                self.root.after(15000, self.autosave_profile_tick)
            except Exception:
                pass


    def restore_autosave_profile(self):
        if not AUTOSAVE_PROFILE_PATH.exists():
            self.post_response("Автосохранение профиля пока не найдено.")
            return
        try:
            data = json.loads(AUTOSAVE_PROFILE_PATH.read_text(encoding="utf-8"))
            self.apply_profile_payload(data)
            self.last_action_var.set("Восстановлен автосохранённый профиль")
            self.append_system_event("recovery", "Восстановлен профиль из автосохранения")
            self.post_response("Восстановил профиль из автосохранения.")
        except Exception as exc:
            self.post_log(f"[autosave-restore] ошибка: {exc}")
            self.append_system_event("recovery", f"Ошибка восстановления автосохранения: {exc}")
            self.post_response("Не смог восстановить автосохранённый профиль.")


    def backup_dir_snapshot(self, source_dir: Path, label: str):
        if not source_dir.exists():
            return None
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = BACKUP_DIR / f"{label}_{stamp}"
        try:
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)
            shutil.copytree(source_dir, target)
            return target
        except Exception:
            return None


    def migrate_data_between_modes(self, target_mode: str, include_backups=True):
        target_mode = str(target_mode or "portable").strip().lower()
        if target_mode not in {"portable", "installed"}:
            messagebox.showerror("Перенос данных", "Неизвестный режим назначения.")
            return
        source_dir = DATA_DIR
        dest_dir = get_data_dir_for_mode(target_mode)
        same_place = source_dir.resolve() == dest_dir.resolve()
        if same_place:
            self.post_response(f"JARVIS уже использует режим хранения: {target_mode}. Перенос не нужен.")
            return
        backup = self.backup_dir_snapshot(source_dir, f"pre_migration_{STORAGE_MODE}_to_{target_mode}")
        copied = 0
        try:
            for item in source_dir.iterdir():
                if item.name == "backups" and not include_backups:
                    continue
                target = dest_dir / item.name
                if item.is_dir():
                    if target.exists():
                        shutil.rmtree(target, ignore_errors=True)
                    shutil.copytree(item, target)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target)
                copied += 1
            self.cfg["install_mode"] = target_mode
            self.cfg["last_data_dir"] = str(dest_dir)
            save_config(self.cfg)
            self.append_system_event("backup", f"Мастер перенёс данные в режим {target_mode} • элементов: {copied}")
            if backup is not None:
                self.append_system_event("backup", f"Перед переносом создана резервная копия: {backup.name}", toast=False)
            self.last_action_var.set(f"Данные перенесены → {target_mode}")
            self.post_response(f"Перенос завершён. Данные скопированы в {dest_dir}")
            messagebox.showinfo("Перенос данных", f"Готово. Скопировано элементов: {copied}\n\nНовая папка данных:\n{dest_dir}\n\nДо перезапуска текущая сессия продолжит работать из прежней папки. Режим хранения задаётся файлом portable_mode.flag или установщиком.")
        except Exception as exc:
            self.post_log(f"[migration] ошибка: {exc}")
            self.append_system_event("backup", f"Ошибка мастера переноса: {exc}")
            messagebox.showerror("Перенос данных", f"Не удалось перенести данные:\n{exc}")


    def show_migration_wizard(self):
        win, body = self.create_modal_shell("Перенос данных", "Безопасный перенос данных между портативным режимом и обычной установкой. Перед копированием создаётся резервная копия.", width=760, height=520)
        hero = tk.Frame(body, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        hero.pack(fill="x", pady=(0, 12))
        tk.Label(hero, text="Перенос данных", bg=CARD_ALT, fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(hero, text="Копирует настройки, заметки, напоминания, память, сессию и данные быстрого запуска в другой режим хранения. Исходные файлы не удаляются.", bg=CARD_ALT, fg=MUTED, wraplength=680, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 14))
        mode_var = tk.StringVar(value="installed" if STORAGE_MODE == "portable" else "portable")
        include_backups_var = tk.BooleanVar(value=True)
        grid = tk.Frame(body, bg=BG)
        grid.pack(fill="both", expand=True)
        left = tk.Frame(grid, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right = tk.Frame(grid, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))
        src = tk.Frame(left, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        src.pack(fill="x", pady=(0, 10))
        tk.Label(src, text="Источник", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        self.make_shell_badge(src, "Текущий режим", STORAGE_MODE, ACCENT_2).pack(fill="x", padx=16, pady=(0, 8))
        self.make_shell_badge(src, "Папка данных", str(DATA_DIR), ACCENT).pack(fill="x", padx=16, pady=(0, 14))
        dest = tk.Frame(left, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        dest.pack(fill="x")
        tk.Label(dest, text="Назначение", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        for value, title, desc in [
            ("portable", f"Портативный режим → {get_data_dir_for_mode('portable')}", "Данные хранятся рядом с приложением — удобно для переносимой сборки."),
            ("installed", f"Обычная установка → {get_data_dir_for_mode('installed')}", "Данные хранятся в профиле Windows пользователя."),
        ]:
            row = tk.Frame(dest, bg=CARD_ALT)
            row.pack(fill="x", padx=14, pady=4)
            tk.Radiobutton(row, text=title, value=value, variable=mode_var, bg=CARD_ALT, fg=TEXT, activebackground=CARD_ALT, activeforeground=TEXT, selectcolor=PANEL_2, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(row, text=desc, bg=CARD_ALT, fg=MUTED, wraplength=300, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=(24,0))
        tk.Checkbutton(dest, text="Копировать резервные копии", variable=include_backups_var, bg=CARD_ALT, fg=TEXT, activebackground=CARD_ALT, activeforeground=TEXT, selectcolor=CARD_ALT, font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(8, 12))
        guide = tk.Frame(right, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        guide.pack(fill="both", expand=True)
        tk.Label(guide, text="Что делает мастер", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        tk.Label(guide, text="1. Создаёт резервную копию текущих данных.\n2. Копирует файлы в другой режим хранения.\n3. Обновляет служебные настройки путей.\n4. Не удаляет исходные данные.\n5. Новый путь начнёт использоваться после перезапуска.", bg=CARD_ALT, fg=MUTED, wraplength=300, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 12))
        self.make_shell_badge(guide, "Портативный путь", str(get_data_dir_for_mode('portable')), ACCENT_2).pack(fill="x", padx=16, pady=(0, 8))
        self.make_shell_badge(guide, "Путь установки", str(get_data_dir_for_mode('installed')), WARN).pack(fill="x", padx=16, pady=(0, 14))
        btns = tk.Frame(body, bg=BG)
        btns.pack(fill="x", pady=(12, 0))
        self.make_button(btns, "Закрыть", win.destroy, variant="ghost", font=("Segoe UI", 10, "bold"), padx=12, pady=8).pack(side="left")
        self.make_button(btns, "Запустить миграцию", lambda: [self.migrate_data_between_modes(mode_var.get(), include_backups_var.get()), win.destroy()], variant="primary", font=("Segoe UI", 10, "bold"), padx=12, pady=8).pack(side="right")


    def create_portable_export_package(self):
        target_root = filedialog.askdirectory(title="Выберите папку для портативного пакета")
        if not target_root:
            return
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_dir = Path(target_root) / f"JARVIS_portable_package_{stamp}"
        package_dir.mkdir(parents=True, exist_ok=True)
        data_target = package_dir / "data"
        manifest = {
            "version": APP_VERSION,
            "created_at": now_iso(),
            "storage_mode": STORAGE_MODE,
            "source_data_dir": str(DATA_DIR),
            "includes": ["data", "portable_mode.flag", "profile_export.json", "PORTABLE_PACKAGE_README_RU.txt"],
        }
        try:
            if data_target.exists():
                shutil.rmtree(data_target, ignore_errors=True)
            shutil.copytree(DATA_DIR, data_target)
            (package_dir / "portable_mode.flag").write_text("1", encoding="utf-8")
            (package_dir / "profile_export.json").write_text(json.dumps(self.build_profile_payload(), ensure_ascii=False, indent=2), encoding="utf-8")
            (package_dir / "portable_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            readme = (
                "JARVIS Portable Package\n\n"
                "Что внутри:\n"
                "- data/ — текущие данные ассистента\n"
                "- portable_mode.flag — принудительный portable-режим\n"
                "- profile_export.json — отдельный экспорт профиля\n\n"
                "Как использовать:\n"
                "1. Положите эти файлы рядом с JARVIS.exe или рядом с исходниками main.py.\n"
                "2. При запуске ассистент возьмёт data из локальной папки.\n"
                "3. Исходная папка пользователя не меняется.\n"
            )
            (package_dir / "PORTABLE_PACKAGE_README_RU.txt").write_text(readme, encoding="utf-8")
            archive_path = shutil.make_archive(str(package_dir), "zip", root_dir=package_dir)
            self.append_system_event("backup", f"Собран портативный пакет: {Path(archive_path).name}")
            self.post_response(f"Portable package готов: {archive_path}")
            messagebox.showinfo("Портативная копия", f"Готово.\n\nПапка: {package_dir}\nZIP: {archive_path}")
        except Exception as exc:
            self.post_log(f"[portable-export] ошибка: {exc}")
            self.append_system_event("backup", f"Ошибка создания портативного пакета: {exc}")
            messagebox.showerror("Портативная копия", f"Не удалось собрать портативный пакет:\n{exc}")


    def show_portable_export_wizard(self):
        win, body = self.create_modal_shell("Портативная копия", "Собирает переносимый пакет текущих данных и ZIP-архив для резервной копии или переноса на другой компьютер.", width=720, height=460)
        top = tk.Frame(body, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        top.pack(fill="x", pady=(0, 12))
        tk.Label(top, text="Портативный пакет", bg=CARD_ALT, fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(top, text="Подходит для переноса JARVIS на другой компьютер или создания резервной копии текущих данных.", bg=CARD_ALT, fg=MUTED, wraplength=640, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 14))
        mid = tk.Frame(body, bg=BG)
        mid.pack(fill="both", expand=True)
        left = tk.Frame(mid, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right = tk.Frame(mid, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(left, text="Что войдёт", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        tk.Label(left, text="• data/\n• portable_mode.flag\n• profile_export.json\n• portable_manifest.json\n• README по быстрому запуску", bg=CARD_ALT, fg=MUTED, justify="left", wraplength=280, font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 12))
        self.make_shell_badge(left, "Источник", str(DATA_DIR), ACCENT_2).pack(fill="x", padx=16, pady=(0, 14))
        tk.Label(right, text="Что получишь", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        tk.Label(right, text="Мастер создаёт отдельную папку с данными и сразу упаковывает её в ZIP. EXE в пакет не входит.", bg=CARD_ALT, fg=MUTED, justify="left", wraplength=280, font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 12))
        self.make_shell_badge(right, "Режим сейчас", STORAGE_MODE, WARN if STORAGE_MODE == "installed" else ACCENT).pack(fill="x", padx=16, pady=(0, 14))
        btns = tk.Frame(body, bg=BG)
        btns.pack(fill="x", pady=(12, 0))
        self.make_button(btns, "Закрыть", win.destroy, variant="ghost", font=("Segoe UI", 10, "bold"), padx=12, pady=8).pack(side="left")
        self.make_button(btns, "Собрать портативный пакет", lambda: [win.destroy(), self.create_portable_export_package()], variant="primary", font=("Segoe UI", 10, "bold"), padx=12, pady=8).pack(side="right")


    def clear_log(self):
        self.log_text.delete("1.0", "end")
        self.dashboard_log.delete("1.0", "end")
        self.footer_var.set("Лог очищен")


    def post_log(self, text: str):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {text}"
        for widget in (getattr(self, "log_text", None), getattr(self, "dashboard_log", None)):
            if widget is not None:
                widget.insert("end", line + "\n")
                widget.see("end")
        append_history(line)
        self.update_stats()
        self.refresh_reminders_ui()


    def should_ignore_voice_result(self, text: str) -> bool:
        """Ignore transcripts captured while JARVIS is speaking, except stop/interrupt commands."""
        normalized = normalize_text(text)
        guard_active = bool(getattr(self, "tts_busy", False)) or time.time() < float(getattr(self, "voice_ignore_until", 0.0) or 0.0)
        if not guard_active:
            return False
        if self.match_any(normalized, getattr(self, "interrupt_phrases", [])):
            return False
        self.post_log(f"[voice-guard] ignored during TTS: {normalized[:100]}")
        return True


    def post_response(self, text: str):
        self.response_var.set(text)
        self.post_log(f"[jarvis] {text}")
        self.footer_var.set(text)
        if getattr(self, "quickbar_window", None) is not None and getattr(self, "quickbar_hint_var", None) is not None:
            self.quickbar_hint_var.set(text)
        self.update_overlay_view()
        lowered = normalize_text(text)
        if any(marker in lowered for marker in ["открываю", "открыл", "напоминание", "удалил", "удалено"]):
            try:
                self.show_toast("JARVIS", text)
            except Exception:
                pass
        if self.tts_var.get():
            # Mark busy before the TTS worker emits its async log, so voice recognizer
            # cannot process our own response in the gap between queueing and playback.
            self.tts_busy = True
            self.voice_ignore_until = time.time() + 2.0
            self.tts.say(text)


    def update_stats(self):
        if NOTES_PATH.exists():
            notes = [line for line in NOTES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.notes_count_var.set(str(len(notes)))
        else:
            self.notes_count_var.set("0")
        if HISTORY_PATH.exists():
            count = len([line for line in HISTORY_PATH.read_text(encoding="utf-8").splitlines() if line.strip()])
            self.history_count_var.set(str(count))
        else:
            self.history_count_var.set("0")
        self.reminder_count_var.set(str(len([r for r in self.reminders if not r.get("done")])) )
        facts = self.memory.get("facts", []) if hasattr(self, "memory") else []
        self.memory_count_var.set(str(len(facts)))
        profile = (self.memory.get("profile", {}) if hasattr(self, "memory") else {}) or {}
        display_name = profile.get("nickname") or profile.get("name") or "—"
        self.profile_name_var.set(display_name)


    def add_note(self, text):
        with NOTES_PATH.open("a", encoding="utf-8") as f:
            f.write(text.strip() + "\n")
        self.load_notes()


    def save_memory(self):
        save_memory_profile(self.memory)
        self.update_stats()


    def add_memory_fact(self, text: str, kind: str = "fact"):
        fact = {"id": f"m{int(time.time()*1000)}", "kind": kind, "text": text.strip(), "created_at": now_iso()}
        self.memory.setdefault("facts", []).append(fact)
        self.save_memory()
        self.refresh_memory_ui()
        return fact


    def set_profile_field(self, key: str, value: str):
        self.memory.setdefault("profile", {})[key] = value.strip()
        self.save_memory()
        self.refresh_memory_ui()


    def refresh_memory_ui(self):
        if hasattr(self, "memory_listbox"):
            self.memory_listbox.delete(0, "end")
            query = normalize_text(self.memory_search_var.get()) if hasattr(self, "memory_search_var") else ""
            facts = self.memory.get("facts", []) or []
            for fact in reversed(facts):
                raw = fact.get("text", "")
                if query and query not in normalize_text(raw):
                    continue
                self.memory_listbox.insert("end", raw)
        self.update_stats()


    def delete_selected_memory_fact(self):
        if not hasattr(self, "memory_listbox"):
            return
        sel = self.memory_listbox.curselection()
        if not sel:
            return
        query = normalize_text(self.memory_search_var.get()) if hasattr(self, "memory_search_var") else ""
        facts = list(reversed(self.memory.get("facts", []) or []))
        visible = [f for f in facts if (not query or query in normalize_text(f.get("text", "")))]
        idx = sel[0]
        if idx >= len(visible):
            return
        target_id = visible[idx].get("id")
        self.memory["facts"] = [f for f in self.memory.get("facts", []) if f.get("id") != target_id]
        self.save_memory()
        self.refresh_memory_ui()
        self.post_response("Удалил факт из памяти.")


    def answer_memory_overview(self):
        self.show_page("memory")
        self.refresh_memory_ui()
        self.post_response(describe_memory_profile(self.memory))


    def load_notes(self):
        if not NOTES_PATH.exists():
            NOTES_PATH.write_text("", encoding="utf-8")
        data = NOTES_PATH.read_text(encoding="utf-8")
        if hasattr(self, "notes_text"):
            self.notes_text.delete("1.0", "end")
            self.notes_text.insert("1.0", data)
        self.update_stats()
        self.refresh_memory_ui()


    def save_notes_from_editor(self):
        NOTES_PATH.write_text(self.notes_text.get("1.0", "end").strip() + "\n", encoding="utf-8")
        self.update_stats()
        self.post_response("Заметки сохранены прямо из редактора.")


    def export_notes(self):
        target = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT", "*.txt")], title="Сохранить заметки")
        if target:
            Path(target).write_text(self.notes_text.get("1.0", "end").strip(), encoding="utf-8")
            self.post_response("Экспортировал заметки.")


    def default_intent_variants(self, label):
        return list(INTENT_DEFAULTS.get(label, []))


    def build_vosk_grammar(self):
        phrases = ["[unk]"]
        wake = self.get_wake_variants()

        def add_phrase(value: str):
            p = normalize_text(value)
            if not p:
                return
            phrases.append(p)
            for w in wake:
                phrases.append(f"{w} {p}")

        for variants in INTENT_DEFAULTS.values():
            for phrase in variants:
                add_phrase(phrase)

        for variants in BRAND_ALIASES.values():
            for phrase in variants:
                add_phrase(phrase)
                add_phrase(f"открой {phrase}")
                add_phrase(f"запусти {phrase}")

        # Command-mode grammar: короткие команды и прерывание речи.
        command_templates = [
                        "замолчи",
            "стоп речь",
            "перестань говорить",
            "стоп",
            "тихо",
            "открой яндекс музыку",
            "запусти яндекс музыку",
            "яндекс музыка",
            "музыка",
            "открой браузер",
            "запусти браузер",
            "браузер",
            "открой сайт [unk]",
            "найди [unk]",
            "найди в интернете [unk]",
            "спроси [unk]",
            "ответь [unk]",
            "объясни [unk]",
            "расскажи [unk]",
            "что такое [unk]",
            "почему [unk]",
            "как сделать [unk]",
            "какая погода [unk]",
            "какая погода в [unk]",
            "погода [unk]",
            "погода в [unk]",
            "сколько градусов в [unk]",
            "температура в [unk]",
            "что с погодой в [unk]",
        ]
        for phrase in command_templates:
            add_phrase(phrase)

        for custom_list in (self.cfg.get("custom_intents", {}) or {}).values():
            for phrase in custom_list:
                add_phrase(phrase)

        phrases = sorted(set([p for p in phrases if p]))
        return json.dumps(phrases, ensure_ascii=False)


    def bump_visualizer(self, amount=0.35):
        self.speech_visual_boost = min(1.0, self.speech_visual_boost + amount)


    def animate_visualizer(self):
        if hasattr(self, "visual_canvas"):
            self.visual_canvas.delete("all")
            w = int(self.visual_canvas.winfo_width() or 420)
            h = int(self.visual_canvas.winfo_height() or 130)
            cx, cy = w // 2, h // 2
            base = 22
            pulse = 10 * math.sin(self.speech_visual_phase)
            active_bonus = 12 if self.listening and self.visualizer_var.get() else 0
            boost_bonus = 16 * self.speech_visual_boost if self.visualizer_var.get() else 0
            radius = base + max(0, pulse) + active_bonus + boost_bonus
            self.visual_canvas.create_oval(cx-44, cy-44, cx+44, cy+44, outline="#1b3f5a", width=2)
            self.visual_canvas.create_oval(cx-62, cy-62, cx+62, cy+62, outline="#16314b", width=1)
            fill = ACCENT if self.listening else PANEL_2
            self.visual_canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, fill=fill, outline="")
            self.visual_canvas.create_text(cx, cy, text="J", fill=BG, font=("Segoe UI", 26, "bold"))
            bars = 18
            for i in range(bars):
                x = 24 + i * ((w - 48) / max(1, bars - 1))
                wave = (math.sin(self.speech_visual_phase * 1.4 + i * 0.5) + 1) / 2
                amp = (8 + wave * 28 + self.speech_visual_boost * 20) if self.listening and self.visualizer_var.get() else 10
                self.visual_canvas.create_line(x, h - 18, x, h - 18 - amp, fill=ACCENT_2 if i % 2 else ACCENT, width=4)
        self.speech_visual_phase += 0.18
        self.speech_visual_boost = max(0.0, self.speech_visual_boost * 0.9)
        self.update_overlay_view()
        self.root.after(50, self.animate_visualizer)


    def update_overlay_view(self):
        return ui_overlay.update_overlay_view(self)


    def toggle_overlay(self, force=None):
        return ui_overlay.toggle_overlay(self, force=force)


    def draw_overlay_orb(self):
        return ui_overlay.draw_overlay_orb(self)


    def open_runtime_settings_dialog(self):
        return ui_open_runtime_settings_dialog(self)



    def _find_helper_script(self, filename: str) -> Path | None:
        """Find helper BAT in source folder, installed EXE folder, or PyInstaller temp folder."""
        candidates = [Path(APP_DIR) / filename]
        try:
            candidates.append(Path(getattr(sys, "_MEIPASS", APP_DIR)) / filename)
        except Exception:
            pass
        try:
            candidates.append(Path(__file__).resolve().parents[2] / filename)
        except Exception:
            pass
        for candidate in candidates:
            try:
                if candidate.exists():
                    return candidate
            except Exception:
                continue
        return None

    def _run_helper_bat(self, filename: str, action_title: str, not_found_message: str):
        script = self._find_helper_script(filename)
        if not script:
            self.post_response(not_found_message)
            return False
        self.last_action_var.set(action_title)
        try:
            os.startfile(str(script))
            return True
        except Exception:
            try:
                subprocess.Popen(["cmd", "/c", "start", "", str(script)], cwd=str(script.parent))
                return True
            except Exception as exc:
                self.post_response(f"Не смог запустить {filename}: {exc}")
                return False

    def setup_local_model_ollama(self):
        """Open local model setup script for Ollama + model."""
        self.post_response("Открываю настройку локального режима. В новом окне нажми Enter. Если Windows спросит разрешение — разреши установку Ollama.")
        self._run_helper_bat(
            "SETUP_LOCAL_MODEL_WINDOWS.bat",
            "Запуск подготовки локальной модели",
            "Файл SETUP_LOCAL_MODEL_WINDOWS.bat не найден рядом с JARVIS. Скачайте полную сборку или установите Ollama вручную: ollama pull llama3.2:1b",
        )

    def check_local_model_ollama(self):
        """Open local model check helper."""
        self.post_response("Открываю проверку локального режима Ollama.")
        self._run_helper_bat(
            "CHECK_LOCAL_MODEL_WINDOWS.bat",
            "Проверка локальной модели",
            "Файл CHECK_LOCAL_MODEL_WINDOWS.bat не найден рядом с JARVIS.",
        )

    def setup_cloud_key_helper(self):
        """Open helper that saves cloud key into Windows environment."""
        self.post_response("Открываю помощник для API-ключа. Вставьте ключ в новое окно, затем полностью перезапустите JARVIS.")
        self._run_helper_bat(
            "SET_CLOUD_KEY_WINDOWS.bat",
            "Настройка cloud key",
            "Файл SET_CLOUD_KEY_WINDOWS.bat не найден рядом с JARVIS. Ключ можно указать в поле Cloud API key в настройках и нажать «Сохранить».",
        )

    def handle_command(self, raw_text: str, source="generic"):

        original_text = normalize_text(raw_text)
        if not original_text:
            return

        wake_variants = self.get_wake_variants()
        text = strip_wake_words(original_text, wake_variants)

        if source == "voice" and bool(self.cfg.get("wake_word_enabled", False)):
            self.post_log(f"[wake-raw] {original_text}")
            wake_ok, wake_tail, matched_wake = extract_wake_tail(original_text, wake_variants)
            if not wake_ok:
                self.post_log(f"[wake] пропуск без wake word: {original_text}")
                return
            self.post_log(f"[wake-ok] {matched_wake}")
            if not wake_tail:
                self.post_response("Слушаю.")
                return
            text = wake_tail
            self.post_log(f"[wake-tail] {text}")

        if not text:
            self.post_response("Да?")
            return

        self.post_log(f"[heard] {text}")
        reminder_probe = _normalize_reminder_command_text(text)
        if source == "voice" and reminder_probe != normalize_text(text) and reminder_probe:
            self.post_log(f"[voice-guard] sanitized → {reminder_probe}")
            text = reminder_probe
        elif source == "voice" and _looks_like_reminder_request(text):
            coerced = _coerce_to_reminder_phrase(text)
            if coerced and coerced != text:
                self.post_log(f"[voice-reminder] coerced → {coerced}")
                text = coerced
        if source == "voice" and is_free_text_command(text):
            self.post_log("[hybrid] detected free-text command path")
        predicted_intent, predicted_phrase, predicted_score = self.smart_match_intent(text)
        if predicted_intent:
            self.post_log(f"[intent-candidate] {predicted_intent} ← {predicted_phrase} ({predicted_score:.2f})")
        # If the matcher is highly confident about a launcher intent, execute it
        # before sequential fuzzy checks so lower-quality matches cannot steal the winner.
        if predicted_intent in {"open_telegram", "open_discord", "open_steam", "open_twitch", "open_youtube"} and predicted_score >= 0.95:
            self.post_log(f"[intent-winner] {predicted_intent} (fast-path {predicted_score:.2f})")
            if predicted_intent == "open_discord":
                if self.open_discord():
                    self.last_action_var.set("Открыт Discord")
                    self.post_response("Открываю Discord.")
                else:
                    self.post_response("Не смог открыть Discord. Укажи путь в настройках.")
                return
            if predicted_intent == "open_telegram":
                if self.open_telegram():
                    self.last_action_var.set("Открыт Telegram")
                    self.post_response("Открываю Telegram.")
                else:
                    self.post_response("Не смог открыть Telegram. Укажи путь в настройках.")
                return
            if predicted_intent == "open_steam":
                if self.open_steam():
                    self.last_action_var.set("Открыт Steam")
                    self.post_response("Открываю Steam.")
                else:
                    self.post_response("Не смог открыть Steam. Укажи путь в настройках.")
                return
            if predicted_intent == "open_twitch":
                webbrowser.open("https://www.twitch.tv/")
                self.last_action_var.set("Открыт Twitch")
                self.post_response("Открываю Twitch.")
                return
            if predicted_intent == "open_youtube":
                webbrowser.open("https://www.youtube.com")
                self.last_action_var.set("Открыт YouTube")
                self.post_response("Открываю YouTube.")
                return

        if self.match_any(text, self.interrupt_phrases + ["сбрось речь", "прерви речь"]):
            self.stop_speaking()
            return

        if self.match_any(text, ["palette", "палитра", "командная палитра", "поиск команд", "global search"]):
            self.show_page("palette")
            self.last_action_var.set("Открыта Палитра команд")
            self.post_response("Открываю палитру команд.")
            return

        if self.match_any(text, ["команды", "помощь", "что ты умеешь", "список команд", "show commands"]):
            self.last_action_var.set("Показан список команд")
            self.post_response(build_command_help_text())
            return

        if self.match_any(text, ["подготовь локальный режим", "подготовь локальный режим", "подготовь бес", "локальный режим", "локальный режим", "установи оламу", "установи олламу", "установи ollama", "установи алан", "установи олан", "установи ламу", "скачай оламу", "скачай ollama", "установи оламу", "установи ollama", "настрой локальный режим", "подключи локальный режим", "установи локальную модель", "установи локальную модель"]):
            self.setup_local_model_ollama()
            return

        if self.match_any(text, ["куда вставить ключ", "вставить ключ", "открой ключ", "облачный ключ", "опенай ключ", "api ключ", "ключ api"]):
            self.show_page("settings")
            self.setup_cloud_key_helper()
            return

        if self.intent_match(text, "test_voice", ["тест голоса", "проверь голос", "проверка голоса", "проверить голос"]):
            self.test_voice()
            return

        if self.intent_match(text, "voice_off", ["без голоса", "выключи голос", "молча", "тихий режим", "режим без звука"]):
            self.set_tts_enabled(False)
            return

        if self.intent_match(text, "voice_on", ["включи голос", "верни голос", "озвучка включена", "говори"]):
            self.set_tts_enabled(True)
            return

        if self.intent_match(text, "overlay_on", ["включи оверлей", "покажи оверлей", "overlay"]):
            self.toggle_overlay(force=True)
            self.post_response("Включил мини-оверлей.")
            return

        if self.intent_match(text, "overlay_off", ["скрой оверлей", "убери оверлей"]):
            self.toggle_overlay(force=False)
            self.post_response("Спрятал мини-оверлей.")
            return
        if self.match_any(text, ["открой яндекс музыку", "запусти яндекс музыку", "яндекс музыка", "музыка"]):
            webbrowser.open("https://music.yandex.ru")
            self.last_action_var.set("Открыта Яндекс Музыка")
            self.post_response("Открываю Яндекс Музыку.")
            return

        if self.match_any(text, ["открой браузер", "запусти браузер", "браузер"]):
            webbrowser.open("https://www.google.com")
            self.last_action_var.set("Открыт браузер")
            self.post_response("Открываю браузер.")
            return


        value = extract_after_prefix(text, ["запомни что меня зовут", "запомни мое имя", "запомни моё имя", "имя"])
        if value is not None and not looks_like_bad_memory_value(value):
            self.set_profile_field("name", value)
            self.last_action_var.set(f"Запомнено имя: {value}")
            self.post_response(f"Запомнил. Тебя зовут {value}.")
            return

        value = extract_after_prefix(text, ["запомни мой ник", "мой ник", "ник"])
        if value is not None:
            if looks_like_bad_memory_value(value):
                self.last_action_var.set("Ник не распознан")
                self.post_response("Ник расслышал плохо. Скажи ещё раз: джарвис мой ник ...")
                return
            self.set_profile_field("nickname", value)
            self.last_action_var.set(f"Запомнен ник: {value}")
            self.post_response(f"Запомнил ник: {value}.")
            return

        value = extract_after_prefix(text, ["запомни мой город", "мой город", "город"])
        if value is not None:
            if looks_like_bad_memory_value(value):
                self.last_action_var.set("Город не распознан")
                self.post_response("Город расслышал плохо. Скажи ещё раз: джарвис мой город ...")
                return
            self.set_profile_field("city", value)
            self.last_action_var.set(f"Запомнен город: {value}")
            self.post_response(f"Запомнил город: {value}.")
            return

        value = extract_after_prefix(text, ["запомни обо мне", "обо мне"])
        if value is not None and not looks_like_bad_memory_value(value):
            self.set_profile_field("about", value)
            self.last_action_var.set("Обновлен профиль")
            self.post_response("Сохранил это в профиле.")
            return

        if self.match_any(text, ["как меня зовут", "какое у меня имя", "что ты знаешь обо мне", "что ты обо мне помнишь", "мой профиль"]):
            self.answer_memory_overview()
            return

        # Мягкий fallback для голосовых memory-команд: после wake word Vosk может искажать
        # длинные фразы, поэтому пытаемся вытащить смысл по ключевым кускам.
        if source == "voice":
            compact = compact_text(text)
            recovered = text
            if "менязовут" in compact or "моеимя" in compact or "моеимя" in compact:
                m2 = re.search(r"(?:меня\s*зовут|мое\s*имя|моё\s*имя)\s+(.+)$", recovered)
                if m2:
                    value = cleanup_memory_value(m2.group(1))
                    if not looks_like_bad_memory_value(value):
                        self.set_profile_field("name", value)
                        self.last_action_var.set(f"Запомнено имя: {value}")
                        self.post_response(f"Запомнил. Тебя зовут {value}.")
                        return
            if "мойник" in compact or compact.startswith("ник"):
                m2 = re.search(r"(?:мой\s*ник|ник)\s+(.+)$", recovered)
                if m2:
                    value = cleanup_memory_value(m2.group(1))
                    if looks_like_bad_memory_value(value):
                        self.last_action_var.set("Ник не распознан")
                        self.post_response("Ник расслышал плохо. Скажи ещё раз: джарвис мой ник ...")
                        return
                    self.set_profile_field("nickname", value)
                    self.last_action_var.set(f"Запомнен ник: {value}")
                    self.post_response(f"Запомнил ник: {value}.")
                    return
            if "мойгород" in compact or compact.startswith("город"):
                m2 = re.search(r"(?:мой\s*город|город)\s+(.+)$", recovered)
                if m2:
                    value = cleanup_memory_value(m2.group(1))
                    if looks_like_bad_memory_value(value):
                        self.last_action_var.set("Город не распознан")
                        self.post_response("Город расслышал плохо. Скажи ещё раз: джарвис мой город ...")
                        return
                    self.set_profile_field("city", value)
                    self.last_action_var.set(f"Запомнен город: {value}")
                    self.post_response(f"Запомнил город: {value}.")
                    return
            if "обомне" in compact:
                m2 = re.search(r"обо\s*мне\s+(.+)$", recovered)
                if m2:
                    value = cleanup_memory_value(m2.group(1))
                    if not looks_like_bad_memory_value(value):
                        self.set_profile_field("about", value)
                        self.last_action_var.set("Обновлен профиль")
                        self.post_response("Сохранил это в профиле.")
                        return
        unified_reminder = parse_unified_reminder_request(text)
        if unified_reminder:
            kind = unified_reminder.get("kind")
            if kind == "create":
                item = self.add_reminder(unified_reminder["dt"], unified_reminder["body"])
                self.last_action_var.set(f"Добавлено напоминание: {unified_reminder['body']}")
                self.show_page("memory")
                self.post_response(f"Поставил напоминание на {datetime.fromisoformat(item['when']).strftime('%d.%m %H:%M')}: {unified_reminder['body']}")
                return
            if kind == "delete":
                if self.handle_delete_reminder_command(unified_reminder.get("text", text)):
                    return
            if kind == "show":
                self.show_page("memory")
                self.refresh_reminders_ui()
                active = self.get_active_reminders()
                self.last_action_var.set("Открыт список напоминаний")
                if not active:
                    self.post_response("Активных напоминаний нет.")
                else:
                    lines = []
                    for idx, item in enumerate(active, 1):
                        try:
                            when_text = datetime.fromisoformat(item.get('when', '')).strftime('%d.%m %H:%M')
                        except Exception:
                            when_text = item.get('when', '')
                        lines.append(f"{idx}. {when_text} — {item.get('text','')}")
                    self.post_response("Напоминания:\n" + "\n".join(lines[:8]))
                return
            if kind == "unclear" and source == "voice":
                self.last_action_var.set("Напоминание расслышано не полностью")
                self.post_log("[voice] reminder unclear -> без TTS, чтобы не ловить петлю распознавания")
                return

        recurring_dt, recurring_text, recurring_mode = parse_recurring_reminder(text)
        if recurring_dt and recurring_text and recurring_mode:
            item = self.add_reminder(recurring_dt, recurring_text, repeat=recurring_mode)
            label = "каждый день" if recurring_mode == "daily" else "по будням"
            self.last_action_var.set(f"Повторяющееся напоминание: {recurring_text}")
            self.post_response(f"Поставил напоминание {label} на {datetime.fromisoformat(item['when']).strftime('%H:%M')}: {recurring_text}")
            return

        if text.startswith("запомни ") or text.startswith("добавь задачу "):
            payload = text.split(" ", 1)[1].strip()
            if payload:
                if len(payload.split()) <= 8:
                    self.add_memory_fact(payload)
                    self.last_action_var.set(f"Добавлен факт: {payload}")
                    self.post_response(f"Запомнил факт: {payload}")
                else:
                    self.add_note(payload)
                    self.last_action_var.set(f"Добавлена заметка: {payload}")
                    self.post_response(f"Запомнил: {payload}")
                return

        if self.intent_match(text, "notes_show", ["покажи заметки", "покажи память", "заметки", "память"]):
            self.load_notes()
            self.show_page("memory")
            self.last_action_var.set("Открыт экран памяти")
            self.post_response("Открыл заметки.")
            return

        if self.intent_match(text, "notes_export", ["экспорт заметок", "сохрани заметки"]):
            self.last_action_var.set("Экспорт заметок")
            self.export_notes()
            return

        reminder_dt, reminder_text = parse_simple_reminder(text)
        if not reminder_dt and _looks_like_reminder_request(text):
            recovered_text = _coerce_to_reminder_phrase(text)
            if recovered_text != text:
                self.post_log(f"[reminder-retry] {recovered_text}")
            reminder_dt, reminder_text = parse_simple_reminder(recovered_text)
        if not reminder_dt and _looks_like_reminder_request(text):
            loose_dt, loose_text = parse_loose_reminder(text)
            if loose_dt and loose_text:
                self.post_log(f"[reminder-loose] {loose_text}")
                reminder_dt, reminder_text = loose_dt, loose_text
        if reminder_dt and reminder_text:
            item = self.add_reminder(reminder_dt, reminder_text)
            self.last_action_var.set(f"Добавлено напоминание: {reminder_text}")
            self.show_page("memory")
            self.post_response(f"Поставил напоминание на {datetime.fromisoformat(item['when']).strftime('%d.%m %H:%M')}: {reminder_text}")
            return

        if self.handle_delete_reminder_command(text):
            return

        if self.intent_match(text, "reminders_show", ["покажи напоминания", "покажи напоминалки", "напоминания", "мои напоминания"]):
            self.show_page("memory")
            self.refresh_reminders_ui()
            active = self.get_active_reminders()
            self.last_action_var.set("Открыт список напоминаний")
            if not active:
                self.post_response("Активных напоминаний нет.")
            else:
                lines = []
                for idx, item in enumerate(active, 1):
                    try:
                        when_text = datetime.fromisoformat(item.get('when', '')).strftime('%d.%m %H:%M')
                    except Exception:
                        when_text = item.get('when', '')
                    lines.append(f"{idx}. {when_text} — {item.get('text','')}")
                self.post_response("Напоминания:\n" + "\n".join(lines[:8]))
            return

        reminder_rescue_inputs = [text, original_text, reminder_probe]
        for rescue_text in reminder_rescue_inputs:
            if not rescue_text:
                continue
            rescue_dt, rescue_body = parse_loose_reminder(rescue_text)
            if rescue_dt and rescue_body:
                item = self.add_reminder(rescue_dt, rescue_body)
                self.last_action_var.set(f"Добавлено напоминание: {rescue_body}")
                self.show_page("memory")
                self.post_log(f"[reminder-rescue] {rescue_body}")
                self.post_response(f"Поставил напоминание на {datetime.fromisoformat(item['when']).strftime('%d.%m %H:%M')}: {rescue_body}")
                return
            if self.handle_delete_reminder_command(rescue_text):
                self.post_log(f"[reminder-delete-rescue] {rescue_text}")
                return

        system_action = self.detect_system_voice_action(text)
        if system_action:
            self.post_log(f"[system-intent] {system_action['kind']} ← {system_action['normalized']} | steps={system_action.get('steps',1)}")
            if self.execute_system_voice_action(system_action):
                return

        if self.apply_alias_command(text):
            return

        if self.open_launcher_site_or_app(text):
            return

        if text.startswith("открой сайт "):
            if self.open_site_from_text(text):
                return

        if self.intent_match(text, "dashboard", ["панель", "главная", "главный экран", "dashboard"]):
            self.show_page("dashboard")
            self.last_action_var.set("Открыта панель")
            self.post_response("Открыл главную панель.")
            return

        if self.intent_match(text, "time_now", ["сколько времени", "который час", "время"]):
            self.last_action_var.set("Запрошено текущее время")
            self.post_response(f"Сейчас {datetime.now().strftime('%H:%M')}")
            return
        if self.intent_match(text, "date_today", ["какая дата", "какое сегодня число", "сегодняшняя дата", "дата"]):
            self.last_action_var.set("Запрошена текущая дата")
            self.post_response(f"Сегодня {datetime.now().strftime('%d.%m.%Y')}")
            return

        if looks_like_weather_request(text):
            self.start_weather_lookup(text)
            return

        if self.intent_match(text, "open_twitch", ["открой твич", "запусти твич", "твич", "твитч", "твичь", "твиттер", "twitch", "twitch tv"]):
            webbrowser.open("https://www.twitch.tv/")
            self.last_action_var.set("Открыт Twitch")
            self.post_response("Открываю Twitch.")
            return

        if self.intent_match(text, "open_youtube", ["открой ютуб", "зайди на ютуб", "ютуб", "ютюб", "ю туб", "youtube", "you tube"]):
            webbrowser.open("https://www.youtube.com")
            self.last_action_var.set("Открыт YouTube")
            self.post_response("Открываю YouTube.")
            return

        if self.intent_match(text, "open_telegram", ["открой телеграм", "запусти телеграм", "телеграм", "телеграмм", "телегу", "телега", "telegram"]):
            if self.open_telegram():
                self.last_action_var.set("Открыт Telegram")
                self.post_response("Открываю Telegram.")
            else:
                self.post_response("Не смог открыть Telegram. Укажи путь в настройках.")
            return

        if self.intent_match(text, "open_discord", ["открой дискорд", "запусти дискорд", "дискорд", "дискор", "дис корд", "дисс корд", "дис корт", "дисс корт", "де скотт", "де скот", "discord"]):
            if self.open_discord():
                self.last_action_var.set("Открыт Discord")
                self.post_response("Открываю Discord.")
            else:
                self.post_response("Не смог открыть Discord. Укажи путь в настройках.")
            return

        if self.intent_match(text, "open_steam", ["открой стим", "запусти стим", "стим", "steam", "с тим", "в тим", "тим"]):
            if self.open_steam():
                self.last_action_var.set("Открыт Steam")
                self.post_response("Открываю Steam.")
            else:
                self.post_response("Не смог открыть Steam. Укажи путь в настройках.")
            return

        if self.intent_match(text, "open_downloads", ["открой загрузки", "покажи загрузки", "загрузки"]):
            if self.open_folder("downloads"):
                self.last_action_var.set("Открыты загрузки")
                self.post_response("Открываю загрузки.")
            else:
                self.post_response("Не смог открыть папку загрузок.")
            return

        if self.intent_match(text, "open_documents", ["открой документы", "покажи документы", "документы"]):
            if self.open_folder("documents"):
                self.last_action_var.set("Открыты документы")
                self.post_response("Открываю документы.")
            else:
                self.post_response("Не смог открыть документы.")
            return

        if self.intent_match(text, "open_desktop", ["открой рабочий стол"]):
            if self.open_folder("desktop"):
                self.last_action_var.set("Открыт рабочий стол")
                self.post_response("Открываю рабочий стол.")
            else:
                self.post_response("Не смог открыть рабочий стол.")
            return

        if self.intent_match(text, "open_taskmgr", ["открой диспетчер задач", "диспетчер задач", "task manager"]):
            if self.open_taskmgr():
                self.last_action_var.set("Открыт диспетчер задач")
                self.post_response("Открываю диспетчер задач.")
            else:
                self.post_response("Не смог открыть диспетчер задач.")
            return

        if self.intent_match(text, "open_control_panel", ["открой панель управления", "панель управления", "control panel"]):
            if self.open_control_panel():
                self.last_action_var.set("Открыта панель управления")
                self.post_response("Открываю панель управления.")
            else:
                self.post_response("Не смог открыть панель управления.")
            return

        if self.intent_match(text, "show_desktop", ["сверни все окна", "свернуть все окна"]):
            if self.show_desktop_windows():
                self.last_action_var.set("Все окна свёрнуты")
                self.post_response("Сворачиваю все окна.")
            else:
                self.post_response("Не смог свернуть все окна.")
            return

        if self.intent_match(text, "launch_hub", ["launcher hub", "лаунчер", "launcher", "центр запуска", "плитки запуска"]):
            self.show_page("launch")
            self.last_action_var.set("Открыт Быстрый запуск")
            self.post_response("Открыл Быстрый запуск.")
            return

        if self.intent_match(text, "control_center", ["центр управления", "панель управления", "control center"]):
            self.show_page("control")
            self.last_action_var.set("Открыт Центр управления")
            self.post_response("Открыл Центр управления.")
            return

        if self.intent_match(text, "glass_ghost", ["режим призрак", "ghost mode", "включи призрак"]):
            self.apply_glass_preset("ghost")
            self.post_response("Включил ghost режим.")
            return

        if self.intent_match(text, "glass_glass", ["режим стекло", "glass mode", "включи стекло"]):
            self.apply_glass_preset("glass")
            self.post_response("Включил glass режим.")
            return

        if self.intent_match(text, "glass_solid", ["режим плотный", "solid mode", "плотный режим"]):
            self.apply_glass_preset("solid")
            self.post_response("Включил плотный режим.")
            return

        if self.intent_match(text, "window_top_on", ["окно сверху", "главное окно сверху", "закрепи окно"]):
            self.always_on_top_var.set(True)
            self.on_main_topmost_toggle()
            self.post_response("Закрепил главное окно сверху.")
            return

        if self.intent_match(text, "window_top_off", ["убери окно сверху", "открепи окно"]):
            self.always_on_top_var.set(False)
            self.on_main_topmost_toggle()
            self.post_response("Главное окно больше не закреплено сверху.")
            return

        if self.intent_match(text, "window_more_transparent", ["сделай прозрачнее", "уменьши прозрачность", "снизь прозрачность"]):
            self.step_window_opacity(-0.06)
            self.post_response(f"Сделал окно прозрачнее до {int(self.window_opacity_var.get()*100)} процентов.")
            return

        if self.intent_match(text, "window_more_solid", ["сделай плотнее", "сделай менее прозрачным", "увеличь прозрачность"]):
            self.step_window_opacity(0.06)
            self.post_response(f"Сделал окно плотнее до {int(self.window_opacity_var.get()*100)} процентов.")
            return

        if self.intent_match(text, "hud_more_transparent", ["худ прозрачнее", "сделай худ прозрачнее", "уменьши прозрачность худа"]):
            self.step_hud_opacity(-0.06)
            self.post_response(f"Сделал HUD прозрачнее до {int(self.hud_opacity_var.get()*100)} процентов.")
            return

        if self.intent_match(text, "hud_more_solid", ["худ плотнее", "сделай худ плотнее", "сделай худ менее прозрачным"]):
            self.step_hud_opacity(0.06)
            self.post_response(f"Сделал HUD плотнее до {int(self.hud_opacity_var.get()*100)} процентов.")
            return

        if self.intent_match(text, "hud_on", ["включи худ", "hud", "полный экран"]):
            if not self.cfg.get("hud_mode", False):
                self.toggle_hud_mode()
            self.post_response("Включил HUD-режим.")
            return

        if self.intent_match(text, "hud_off", ["выключи худ", "убери hud", "сверни худ"]):
            if self.cfg.get("hud_mode", False):
                self.toggle_hud_mode()
            self.post_response("Выключил HUD-режим.")
            return

        if self.intent_match(text, "theme_red", ["красная тема", "red theme"]):
            self.apply_theme("red")
            self.post_response("Переключил тему на Red Combat.")
            return

        if self.intent_match(text, "theme_green", ["зеленая тема", "зелёная тема", "green theme"]):
            self.apply_theme("green")
            self.post_response("Переключил тему на Green Reactor.")
            return

        if self.intent_match(text, "theme_cyan", ["синяя тема", "голубая тема", "cyan theme"]):
            self.apply_theme("cyan")
            self.post_response("Переключил тему на Cyan JARVIS.")
            return


        if self.intent_match(text, "scenario_work", ["рабочий режим", "режим работа", "режим работы", "подготовь работу", "запусти рабочий режим"]):
            self.run_scenario("work")
            return

        if self.intent_match(text, "scenario_game", ["игровой режим", "режим игра", "режим игры", "запусти игровой режим", "подготовь игру"]):
            self.run_scenario("game")
            return

        if self.intent_match(text, "scenario_silent", ["тихий режим", "режим тишина", "ночной режим", "режим молчания", "запусти тихий режим"]):
            self.run_scenario("silent", voiced=False)
            return

        if self.intent_match(text, "greeting", ["привет", "здарова", "здравствуй"]):
            self.last_action_var.set("Приветствие")
            self.post_response(f"Привет, {self.cfg['user_name']}. На связи.")
            return

        if self.intent_match(text, "shutdown", ["выключись", "закройся", "выход"]):
            self.last_action_var.set("Завершение работы")
            self.post_response("Выключаюсь.")
            self.root.after(700, self.root.destroy)
            return

        if predicted_intent and predicted_score >= 0.80:
            self.post_log(f"[intent-auto] повторная попытка по ядру: {predicted_intent}")
            if predicted_intent == "open_discord":
                if self.open_discord():
                    self.last_action_var.set("Открыт Discord")
                    self.post_response("Открываю Discord.")
                else:
                    self.post_response("Не смог открыть Discord. Укажи путь в настройках.")
                return
            if predicted_intent == "open_telegram":
                if self.open_telegram():
                    self.last_action_var.set("Открыт Telegram")
                    self.post_response("Открываю Telegram.")
                else:
                    self.post_response("Не смог открыть Telegram. Укажи путь в настройках.")
                return
            if predicted_intent == "open_steam":
                if self.open_steam():
                    self.last_action_var.set("Открыт Steam")
                    self.post_response("Открываю Steam.")
                else:
                    self.post_response("Не смог открыть Steam. Укажи путь в настройках.")
                return
            if predicted_intent == "open_twitch":
                webbrowser.open("https://www.twitch.tv/")
                self.last_action_var.set("Открыт Twitch")
                self.post_response("Открываю Twitch.")
                return
            if predicted_intent == "open_youtube":
                webbrowser.open("https://www.youtube.com")
                self.last_action_var.set("Открыт YouTube")
                self.post_response("Открываю YouTube.")
                return
            if predicted_intent == "open_downloads" and self.open_folder("downloads"):
                self.last_action_var.set("Открыты загрузки")
                self.post_response("Открываю загрузки.")
                return
            if predicted_intent == "open_documents" and self.open_folder("documents"):
                self.last_action_var.set("Открыты документы")
                self.post_response("Открываю документы.")
                return

        if self.should_use_model_for_text(text, source=source):
            self.start_model_chat(text)
            return

        if source == "voice" and predicted_score < 0.80 and _looks_like_asr_garbage(text):
            self.last_action_var.set("Шумовая голосовая фраза пропущена")
            self.post_log(f"[voice-skip] garbage ignored ← {text}")
            return
        self.last_action_var.set("Неизвестная команда")
        self.post_log(f"[intent] unknown ← {text}")
        hint = "Команду пока не понял. Попробуй короче: открой телеграм, открой дискорд, открой стим, открой ютуб, какая дата."
        if predicted_intent and predicted_score >= 0.60:
            friendly = {
                "open_telegram": "Похоже, ты хотел открыть Telegram.",
                "open_discord": "Похоже, ты хотел открыть Discord.",
                "open_steam": "Похоже, ты хотел открыть Steam.",
                "open_youtube": "Похоже, ты хотел открыть YouTube.",
                "reminders_show": "Похоже, ты хотел показать напоминания.",
                "reminders_delete": "Похоже, ты хотел удалить напоминание.",
                "create_reminder": "Похоже, ты хотел создать напоминание.",
            }.get(predicted_intent, "")
            if friendly:
                hint = friendly + " Скажи коротко и чётко ещё раз."
        elif any(token in text for token in ["напомни", "напомнить", "завтра", "сегодня", "послезавтра", "через"]):
            hint = "Похоже на напоминание. Скажи так: джарвис напомни завтра в 11 купить хлеб."
        self.set_voice_pipeline_status("intent unclear")
        self.post_response(hint)



    def post_status_only(self, text: str):
        self.response_var.set(text)
        self.footer_var.set(text)
        self.post_log(f"[jarvis] {text}")
        self.update_overlay_view()


    def start_weather_lookup(self, text: str):
        """Get real current weather through a small no-key web request.

        Weather must not be sent to the local LLM: a local model does not know
        live weather and can hallucinate. This command uses internet when
        available and gives a clear offline message when it is not.
        """
        if getattr(self, "weather_busy", False):
            self.post_response("Уже проверяю погоду. Секунду.")
            return
        self.weather_busy = True
        self.last_action_var.set("Проверка погоды")
        self.set_voice_pipeline_status("weather request")
        self.post_status_only("Смотрю погоду...")

        def worker():
            try:
                answer = get_weather_answer(text, config=self.cfg, memory=self.memory)
            except Exception as exc:
                answer = f"Не смог получить погоду: {str(exc)[:160]}"
            def done():
                self.weather_busy = False
                self.last_action_var.set("Погода")
                self.set_voice_pipeline_status("weather answered")
                self.post_response(answer)
            try:
                self.root.after(0, done)
            except Exception:
                self.weather_busy = False
        threading.Thread(target=worker, daemon=True).start()


    def should_use_model_for_text(self, text: str, source: str = "generic") -> bool:
        if not bool(self.cfg.get("model_answers_enabled", True)):
            return False
        norm = normalize_text(text)
        if not norm:
            return False
        if looks_like_weather_request(norm):
            return False
        if looks_like_model_request(norm, allow_questions=True):
            return True
        if source in {"voice", "text", "chat", "generic"} and bool(self.cfg.get("model_fallback_unknown", True)):
            if norm.startswith(("открой ", "запусти ", "покажи ", "выключи ", "включи ", "удали ", "убери ", "напомни ", "напоминай ")):
                return False
            if len(norm.split()) >= 3 and not _looks_like_asr_garbage(norm):
                return True
        return False


    def start_model_chat(self, text: str):
        if getattr(self, "model_busy", False):
            self.post_response("Я ещё отвечаю на прошлый вопрос. Скажи стоп, если нужно прервать речь.")
            return
        self.model_busy = True
        clean_text = strip_model_prefix(text)
        if not clean_text:
            clean_text = text
        self.last_action_var.set("Запрос к модели")
        self.set_voice_pipeline_status("model request")
        self.post_status_only("Думаю над ответом...")

        def worker():
            try:
                answer = ask_model(clean_text, self.cfg, getattr(self, "model_chat_history", []))
            except Exception as exc:
                answer = f"MODEL_ERROR: {exc}"
            def done():
                self.model_busy = False
                self.handle_model_answer(clean_text, answer)
            try:
                self.root.after(0, done)
            except Exception:
                self.model_busy = False
        threading.Thread(target=worker, daemon=True).start()


    def handle_model_answer(self, user_text: str, answer: str):
        answer = str(answer or "").strip()
        if answer.startswith("MODEL_OFF:"):
            self.last_action_var.set("Модель не настроена")
            self.post_response(answer.replace("MODEL_OFF:", "").strip())
            return
        if answer.startswith("MODEL_ERROR:"):
            self.last_action_var.set("Ошибка модели")
            self.post_response(answer.replace("MODEL_ERROR:", "").strip())
            return
        self.model_chat_history.append({"role": "user", "content": user_text})
        self.model_chat_history.append({"role": "assistant", "content": answer})
        self.model_chat_history = self.model_chat_history[-10:]
        self.last_action_var.set("Ответ модели")
        self.set_voice_pipeline_status("model answered")
        self.post_response(answer)


    def toggle_main_topmost_button(self):
        self.always_on_top_var.set(not bool(self.always_on_top_var.get()))
        self.on_main_topmost_toggle()


    def on_quickbar_topmost_toggle(self):
        self.cfg["quick_bar_topmost"] = bool(self.quick_bar_topmost_var.get())
        if self.quickbar_window is not None:
            try:
                self.quickbar_window.attributes("-topmost", bool(self.quick_bar_topmost_var.get()))
            except Exception:
                pass
        save_config(self.cfg)
        self.footer_var.set("Быстрая панель закреплена сверху" if self.quick_bar_topmost_var.get() else "Быстрая панель может уходить назад")


    def toggle_quickbar_pin(self):
        self.quick_bar_topmost_var.set(not bool(self.quick_bar_topmost_var.get()))
        self.on_quickbar_topmost_toggle()


    def quickbar_submit(self, event=None):
        if self.quickbar_entry is None:
            return
        text = self.quickbar_entry.get().strip()
        if not text:
            return
        self.quickbar_entry.delete(0, "end")
        self.heard_var.set(text)
        self.overlay_heard_var.set(text)
        self.post_log(f"[quickbar] {text}")
        self.handle_command(text, source="quickbar")


    def toggle_quickbar(self):
        if self.quickbar_window is not None and self.quickbar_window.winfo_exists():
            try:
                self.quickbar_window.destroy()
            except Exception:
                pass
            self.quickbar_window = None
            self.quickbar_entry = None
            self.quickbar_hint_var = None
            self.footer_var.set("Быстрая панель скрыта")
            self.save_session_state(silent=True)
            return

        qb = tk.Toplevel(self.root)
        self.quickbar_window = qb
        qb.title("JARVIS — быстрая панель")
        qb.configure(bg=BORDER)
        qb.resizable(False, False)
        qb.geometry("760x170+460+70")
        try:
            qb.attributes("-topmost", bool(self.quick_bar_topmost_var.get()))
        except Exception:
            pass
        qb.protocol("WM_DELETE_WINDOW", self.toggle_quickbar)

        shell = tk.Frame(qb, bg=BG, highlightbackground=BORDER, highlightthickness=1)
        shell.pack(fill="both", expand=True, padx=1, pady=1)
        frame = tk.Frame(shell, bg=PANEL, highlightbackground=BORDER, highlightthickness=0)
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        stripe = tk.Frame(frame, bg=ACCENT, height=3)
        stripe.pack(fill="x")
        top = tk.Frame(frame, bg=PANEL)
        top.pack(fill="x", padx=12, pady=(10, 4))
        tk.Label(top, text="Быстрая панель", bg=PANEL, fg=ACCENT, font=("Segoe UI Semibold", 16)).pack(side="left")
        tk.Label(top, text="быстрый вызов команд поверх окон", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(side="left", padx=(10, 0))
        self.pill(top, "F6", fg=ACCENT_2).pack(side="left", padx=(12, 0))
        self.make_button(top, "📌", self.toggle_quickbar_pin, variant="secondary", font=("Segoe UI", 9, "bold"), padx=10, pady=6).pack(side="right", padx=(6, 0))
        self.make_button(top, "✕", self.toggle_quickbar, variant="secondary", font=("Segoe UI", 9, "bold"), padx=10, pady=6).pack(side="right")

        self.quickbar_hint_var = tk.StringVar(value="Напиши команду, жми Enter или выбери подсказку ниже")
        tk.Label(frame, textvariable=self.quickbar_hint_var, bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=12)

        row = tk.Frame(frame, bg=PANEL)
        row.pack(fill="x", padx=12, pady=(8, 8))
        self.quickbar_entry = tk.Entry(row, font=("Segoe UI", 14))
        self.style_entry_widget(self.quickbar_entry, font=("Segoe UI", 14))
        self.quickbar_entry.pack(side="left", fill="x", expand=True, ipady=10)
        self.quickbar_entry.bind("<Return>", self.quickbar_submit)
        self.make_button(row, "Выполнить", self.quickbar_submit, variant="primary", pady=10).pack(side="left", padx=(10, 0))

        chips = tk.Frame(frame, bg=PANEL)
        chips.pack(fill="x", padx=12, pady=(0, 8))
        quick_suggestions = self.get_quickbar_suggestions()
        for text in quick_suggestions:
            self.make_button(chips, text, lambda t=text: self.insert_quickbar_command(t), variant="ghost", font=("Segoe UI", 9, "bold"), padx=10, pady=6).pack(side="left", padx=(0, 6))

        foot = tk.Frame(frame, bg=PANEL)
        foot.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(foot, text="ENTER → выполнить   •   F6 → скрыть   •   📌 → закрепить поверх окон", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")

        self.quickbar_entry.focus_set()
        self.save_session_state(silent=True)
        self.footer_var.set("Быстрая панель открыта")

    def insert_quickbar_command(self, text):
        if self.quickbar_entry is None:
            return
        self.quickbar_entry.delete(0, "end")
        self.quickbar_entry.insert(0, text)
        self.quickbar_entry.focus_set()
        self.save_session_state(silent=True)


    def get_quickbar_suggestions(self):
        suggestions = []
        for name, _path in self.launcher_ordered_items("apps")[:2]:
            suggestions.append(f"запусти {name}")
        for name, _url in self.launcher_ordered_items("sites")[:2]:
            suggestions.append(f"открой {name}")
        for alias, _target in list((self.cfg.get("aliases", {}) or {}).items())[:2]:
            suggestions.append(alias)
        base = ["рабочий режим", "покажи напоминания", "сколько времени", "сверни все окна"]
        for item in base:
            suggestions.append(item)
        result = []
        seen = set()
        for item in suggestions:
            key = normalize_text(item)
            if key and key not in seen:
                seen.add(key)
                result.append(item)
            if len(result) >= 6:
                break
        return result


    def get_startup_bat_path(self):
        appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
        return appdata / "Microsoft/Windows/Start Menu/Programs/Startup/JARVIS_Autostart.bat"


    def ensure_autostart_state(self):
        startup_bat = self.get_startup_bat_path()
        enabled = bool(self.autostart_enabled_var.get())
        self.cfg["autostart_enabled"] = enabled
        if os.name != "nt":
            self.tray_status_var.set("Трей: автозапуск доступен только в Windows") if hasattr(self, "tray_status_var") else None
            return False
        try:
            if enabled:
                startup_bat.parent.mkdir(parents=True, exist_ok=True)
                startup_bat.write_text(f'@echo off\ncd /d "{APP_DIR}"\nstart "" pythonw "{APP_DIR / "main.py"}"\n', encoding="utf-8")
            elif startup_bat.exists():
                startup_bat.unlink()
            return True
        except Exception as exc:
            self.post_log(f"[autostart] ошибка: {exc}")
            return False


    def on_autostart_toggle(self):
        ok = self.ensure_autostart_state()
        save_config(self.cfg)
        if ok:
            self.footer_var.set("Автозапуск обновлён")
        else:
            self.footer_var.set("Не удалось обновить автозапуск")


    def create_tray_image(self):
        return ui_tray.create_tray_image()


    def ensure_tray_state(self):
        return ui_tray.ensure_tray_state(self)


    def hide_to_tray(self):
        return ui_tray.hide_to_tray(self)


    def restore_from_tray(self):
        return ui_tray.restore_from_tray(self)


    def stop_tray_icon(self):
        return ui_tray.stop_tray_icon(self)


    def handle_tk_exception(self, exc_type, exc_value, exc_tb):
        details = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        log_app_exception("tk_callback", exc_value, details)
        try:
            self.post_log(f"[ui] callback error: {exc_value}")
        except Exception:
            pass
        try:
            self.append_system_event("app", f"UI callback error: {exc_value}")
        except Exception:
            pass
        try:
            messagebox.showerror("JARVIS", f"Произошла ошибка интерфейса:\n{exc_value}")
        except Exception:
            pass


    def on_root_close(self):
        self.save_session_state(silent=True)
        self.append_system_event("app", "Нажат крестик главного окна", toast=False)
        if bool(self.close_to_tray_var.get()):
            self.hide_to_tray()
        else:
            self.full_exit()


    def full_exit(self):
        self.save_session_state(silent=True)
        self.append_system_event("app", "Полный выход из JARVIS")
        self.stop_tray_icon()
        try:
            self.tts.stop()
        except Exception:
            pass
        self.root.destroy()


    def minimize_window(self):
        if bool(getattr(self, "minimize_to_tray_var", tk.BooleanVar(value=False)).get()):
            self.hide_to_tray()
            return
        try:
            self.root.overrideredirect(False)
            self.root.iconify()
            self.root.after(200, lambda: self.root.overrideredirect(True))
        except Exception:
            self.root.iconify()




def main():
    root = None
    try:
        root = tk.Tk()
        app = JarvisApp(root)
        root.mainloop()
    except Exception as exc:
        log_app_exception("startup", exc)
        try:
            messagebox.showerror("Ошибка запуска JARVIS", f"JARVIS не смог запуститься:\n{exc}\n\nПодробности сохранены в data/startup_crash.log")
        except Exception:
            pass
        raise
    finally:
        if root is not None:
            try:
                root.update_idletasks()
            except Exception:
                pass


if __name__ == "__main__":
    main()
