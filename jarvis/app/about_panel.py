from .main_window_shared import *


class AboutPanelMixin:
    def build_control_page(self):
        page = tk.Frame(self.page_container, bg=BG)
        self.pages["control"] = page

        self.section_title(page, "Центр управления", "Режимы интерфейса, быстрые команды и системный контроль")

        hero = self.card(page, bg=CARD_ALT)
        hero.pack(fill="x", pady=(12, 10))
        hero_top = tk.Frame(hero, bg=CARD_ALT)
        hero_top.pack(fill="x", padx=18, pady=(16, 8))
        tk.Label(hero_top, text="УПРАВЛЕНИЕ", bg=CARD_ALT, fg=ACCENT, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(hero_top, text="Центр быстрого запуска", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 19, "bold")).pack(anchor="w", pady=(4, 2))
        tk.Label(hero_top, text="Здесь собраны HUD-режимы, прозрачность, темы интерфейса и быстрые команды JARVIS.", bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 10), justify="left", wraplength=920).pack(anchor="w")

        hero_stats = tk.Frame(hero, bg=CARD_ALT)
        hero_stats.pack(fill="x", padx=18, pady=(4, 10))
        stat_defs = [
            ("HUD", "Оверлей / F11", ACCENT),
            ("Стекло", "Лёгкая · Стекло · Плотная", ACCENT_2),
            ("Темы", "Цветовая палитра", TEXT),
            ("Команды", "Быстрые действия", ACCENT),
        ]
        for idx, (label, value, color) in enumerate(stat_defs):
            card = tk.Frame(hero_stats, bg=PANEL_2, highlightthickness=1, highlightbackground=BORDER)
            card.grid(row=0, column=idx, padx=6, sticky="nsew")
            tk.Label(card, text=label, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
            tk.Label(card, text=value, bg=PANEL_2, fg=color, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(0, 12))
            hero_stats.columnconfigure(idx, weight=1)

        top = tk.Frame(page, bg=BG)
        top.pack(fill="x", pady=(0, 10))

        left = self.card(top, bg=CARD_ALT)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = self.card(top)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="HUD и оверлей", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(left, text="Быстрые режимы интерфейса, прозрачность окна и управление речью.", bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 10), wraplength=420, justify="left").pack(anchor="w", padx=16)
        buttons = tk.Frame(left, bg=CARD_ALT)
        buttons.pack(fill="x", padx=16, pady=(14, 12))
        for text_btn, cmd in [
            ("Полный HUD / F11", self.toggle_hud_mode),
            ("Показать оверлей", lambda: self.toggle_overlay(force=True)),
            ("Спрятать оверлей", lambda: self.toggle_overlay(force=False)),
            ("Прервать речь", self.stop_speaking),
        ]:
            tk.Button(buttons, text=text_btn, command=cmd, bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2", padx=12, pady=12).pack(fill="x", pady=4)

        glass = tk.Frame(left, bg=CARD_ALT)
        glass.pack(fill="x", padx=16, pady=(0, 16))
        tk.Label(glass, text="Прозрачность", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))
        tk.Label(glass, text="Быстрые пресеты прозрачности для окна и HUD без ручной крутки каждого параметра.", bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 9), wraplength=360, justify="left").pack(anchor="w", pady=(0, 8))
        tk.Button(glass, text="Сделать прозрачнее", command=lambda: self.step_window_opacity(-0.06), bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2").pack(fill="x", pady=4)
        tk.Button(glass, text="Сделать плотнее", command=lambda: self.step_window_opacity(0.06), bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2").pack(fill="x", pady=(0, 4))
        tk.Button(glass, text="HUD прозрачнее", command=lambda: self.step_hud_opacity(-0.06), bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT_2, relief="flat", bd=0, cursor="hand2").pack(fill="x", pady=4)
        tk.Button(glass, text="HUD плотнее", command=lambda: self.step_hud_opacity(0.06), bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT_2, relief="flat", bd=0, cursor="hand2").pack(fill="x", pady=(0, 4))
        preset_row = tk.Frame(glass, bg=CARD_ALT)
        preset_row.pack(fill="x", pady=(6, 0))
        for idx, (label, preset) in enumerate([("Лёгкая", "ghost"), ("Стекло", "glass"), ("Плотная", "solid")]):
            tk.Button(preset_row, text=label, command=lambda p=preset: self.apply_glass_preset(p), bg=PANEL_2, fg=TEXT, activebackground=CARD, activeforeground=ACCENT, relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold")).grid(row=0, column=idx, padx=4, sticky="ew")
            preset_row.columnconfigure(idx, weight=1)

        tk.Label(right, text="Темы интерфейса", bg=CARD, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(right, text="Смена цветовой темы и быстрые режимы главного окна JARVIS.", bg=CARD, fg=MUTED, font=("Segoe UI", 10), wraplength=420, justify="left").pack(anchor="w", padx=16)
        theme_grid = tk.Frame(right, bg=CARD)
        theme_grid.pack(fill="x", padx=16, pady=(14, 16))
        for idx, key in enumerate(THEMES):
            tk.Button(theme_grid, text=THEMES[key]["name"], command=lambda k=key: self.apply_theme(k), bg=PANEL_2, fg=TEXT, activebackground=CARD_ALT, activeforeground=ACCENT, relief="flat", bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2", padx=12, pady=14).grid(row=0, column=idx, padx=6, sticky="ew")
            theme_grid.columnconfigure(idx, weight=1)

        bottom = self.card(page)
        bottom.pack(fill="both", expand=True)
        tk.Label(bottom, text="Быстрые команды", bg=CARD, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(bottom, text="Готовые команды: нажмите карточку — JARVIS выполнит действие без ручного ввода.", bg=CARD, fg=MUTED, font=("Segoe UI", 10), wraplength=920, justify="left").pack(anchor="w", padx=16)
        commands_grid = tk.Frame(bottom, bg=CARD)
        commands_grid.pack(fill="both", expand=True, padx=16, pady=(12, 16))
        commands = [
            ("Открыть Telegram", "открой телеграм"),
            ("Открыть Discord", "открой дискорд"),
            ("Открыть Steam", "открой стим"),
            ("Открыть YouTube", "открой ютуб"),
            ("Показать заметки", "покажи заметки"),
            ("Рабочий режим", "рабочий режим"),
            ("Игровой режим", "игровый режим"),
            ("Тихий режим", "тихий режим"),
            ("Сколько времени", "сколько времени"),
            ("Какая дата", "какая дата"),
            ("Приветствие", "привет"),
            ("Команды", "команды"),
        ]
        for idx, (caption, cmd) in enumerate(commands):
            r, c = divmod(idx, 4)
            tile = tk.Frame(commands_grid, bg=PANEL_2, highlightthickness=1, highlightbackground=BORDER)
            tile.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            accent = tk.Frame(tile, bg=ACCENT if idx % 2 == 0 else ACCENT_2, height=3)
            accent.pack(fill="x")
            tk.Label(tile, text=caption, bg=PANEL_2, fg=TEXT, font=("Segoe UI", 11, "bold"), wraplength=160, justify="left").pack(anchor="w", padx=12, pady=(12, 4))
            tk.Label(tile, text=cmd, bg=PANEL_2, fg=MUTED, font=("Consolas", 9), wraplength=170, justify="left").pack(anchor="w", padx=12)
            tk.Button(tile, text="Выполнить", command=lambda t=cmd: self.handle_command(t), bg=PANEL_2, fg=ACCENT, activebackground=CARD_ALT, activeforeground=ACCENT_2, relief="flat", bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2").pack(anchor="w", padx=10, pady=(10, 10))
        for i in range(3):
            commands_grid.rowconfigure(i, weight=1)
        for i in range(4):
            commands_grid.columnconfigure(i, weight=1)



    def show_onboarding_next_steps(self):
        win, body = self.create_modal_shell("Следующие шаги", "Короткая настройка после первого запуска: основные пути, быстрый запуск и журнал событий.", width=760, height=520)
        hero = tk.Frame(body, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        hero.pack(fill="x", pady=(0, 12))
        tk.Label(hero, text="JARVIS готов к первому запуску", bg=CARD_ALT, fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(hero, text="Мастер помогает выбрать режим хранения, указать основные параметры и подготовить JARVIS к работе.", bg=CARD_ALT, fg=MUTED, wraplength=680, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 14))
        steps = tk.Frame(body, bg=BG)
        steps.pack(fill="both", expand=True)
        for idx, (title, desc, cmd, variant) in enumerate([
            ("1. Настройки", "Укажите пути к Telegram, Discord и Steam, затем проверьте оверлей.", lambda: self._open_onboarding_page(win, "settings"), "secondary"),
            ("2. Быстрый запуск", "Добавьте нужные сайты, приложения и свои команды-псевдонимы.", lambda: self._open_onboarding_page(win, "launcher"), "secondary"),
            ("3. Журнал событий", "Проверьте восстановление сессии, автосохранение и журнал событий.", lambda: self._open_onboarding_page(win, "system"), "ghost"),
        ]):
            card = tk.Frame(steps, bg=CARD_ALT if idx < 2 else CARD, highlightbackground=BORDER, highlightthickness=1)
            card.pack(fill="x", pady=(0, 10))
            tk.Label(card, text=title, bg=card.cget("bg"), fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=16, pady=(12, 2))
            tk.Label(card, text=desc, bg=card.cget("bg"), fg=MUTED, wraplength=680, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 10))
            self.make_button(card, "Открыть", cmd, variant=variant, font=("Segoe UI", 10, "bold"), padx=12, pady=8).pack(anchor="w", padx=16, pady=(0, 14))
        bottom = tk.Frame(body, bg=BG)
        bottom.pack(fill="x", pady=(8, 0))
        self.make_button(bottom, "Закрыть", win.destroy, variant="ghost", font=("Segoe UI", 10, "bold"), padx=12, pady=8).pack(side="left")
        self.make_button(bottom, "Открыть выбранные стартовые страницы", lambda: self.finish_onboarding_shortcuts(win), variant="primary", font=("Segoe UI", 10, "bold"), padx=12, pady=8).pack(side="right")


    def _open_onboarding_page(self, win, page_name):
        try:
            win.destroy()
        except Exception:
            pass
        self.show_page(page_name)
        self.append_system_event("startup", f"После настройки открыта страница: {page_name}", toast=False)


    def finish_onboarding_shortcuts(self, win):
        try:
            win.destroy()
        except Exception:
            pass
        if bool(self.onboarding_launch_settings_var.get()):
            self.show_page("settings")
        if bool(self.onboarding_launch_launcher_var.get()):
            self.root.after(140, lambda: self.show_page("launcher"))
        self.append_system_event("startup", "Показан список следующих шагов после первичной настройки", toast=False)
        self.post_response("Первичная настройка открыта. Проверьте настройки и быстрый запуск.")


    def maybe_show_first_run_wizard(self):
        # Config is the source of truth. Do not re-open the wizard after a completed first run.
        if bool(self.cfg.get("first_run_completed", False)):
            return
        if not bool(self.cfg.get("show_first_run_wizard", False)):
            return
        self.show_first_run_wizard()


    def complete_first_run(self, win, install_mode, user_name, assistant_name, accept_license, launch_overlay, enable_toasts, close_after):
        self.cfg["user_name"] = user_name.strip() or self.cfg.get("user_name", "Пользователь")
        self.cfg["assistant_name"] = assistant_name.strip() or self.cfg.get("assistant_name", "JARVIS")
        self.cfg["install_mode"] = install_mode
        self.cfg["license_accepted"] = bool(accept_license)
        self.cfg["toast_notifications"] = bool(enable_toasts)
        # Never force-switch a working Распознавание речи from the first-run wizard.
        self.cfg["voice_input_engine"] = str(self.cfg.get("voice_input_engine", "vosk") or "vosk")
        self.cfg["first_run_completed"] = True
        self.cfg["show_first_run_wizard"] = not bool(close_after)
        self.cfg["last_data_dir"] = str(DATA_DIR)
        self.toast_notifications_var.set(bool(enable_toasts))
        self.overlay_var.set(bool(launch_overlay))
        save_config(self.cfg)
        try:
            FIRST_RUN_MARKER.write_text(now_iso(), encoding="utf-8")
        except Exception:
            pass
        self.root.title(f"{APP_TITLE} — {self.cfg['user_name']}")
        if launch_overlay and self.overlay_window is None:
            self.toggle_overlay(force=True)
        elif (not launch_overlay) and self.overlay_window is not None:
            self.toggle_overlay(force=False)
        self.append_system_event("startup", f"Первый запуск завершён • режим данных: {install_mode}", toast=True)
        self.footer_var.set(f"Первичная настройка завершена • данные: {install_mode}")
        try:
            win.destroy()
        except Exception:
            pass
        if close_after:
            self.cfg["show_first_run_wizard"] = False
            save_config(self.cfg)
        # Keep in-memory config synced with what was saved on disk.
        self.cfg = load_config()

        def _after_model_prompt():
            if bool(self.onboarding_open_after_var.get()):
                self.show_onboarding_next_steps()

        if bool(self.cfg.get("show_model_setup_wizard", False)) and not bool(self.cfg.get("local_model_setup_completed", False)):
            self.root.after(180, lambda: self.show_model_setup_wizard(after_close=_after_model_prompt))
        elif bool(self.onboarding_open_after_var.get()):
            self.root.after(150, self.show_onboarding_next_steps)


    def _persist_first_run_draft(self, install_mode, user_name, assistant_name, accept_license, launch_overlay, enable_toasts, close_after):
        self.cfg["user_name"] = user_name.strip() or self.cfg.get("user_name", "Пользователь")
        self.cfg["assistant_name"] = assistant_name.strip() or self.cfg.get("assistant_name", "JARVIS")
        self.cfg["install_mode"] = install_mode
        self.cfg["license_accepted"] = bool(accept_license)
        self.cfg["toast_notifications"] = bool(enable_toasts)
        self.cfg["voice_input_engine"] = str(self.cfg.get("voice_input_engine", "vosk") or "vosk")
        self.cfg["last_data_dir"] = str(DATA_DIR)
        if close_after:
            self.cfg["show_first_run_wizard"] = False
            self.cfg["first_run_completed"] = True
        save_config(self.cfg)
        self.cfg = load_config()


    def maybe_show_model_setup_wizard(self):
        """Show one-time model setup choice after first launch/install."""
        if not bool(self.cfg.get("first_run_completed", False)):
            return
        if not bool(self.cfg.get("show_model_setup_wizard", False)):
            return
        if bool(self.cfg.get("local_model_setup_completed", False)):
            return
        if getattr(self, "model_setup_window", None) is not None:
            try:
                if self.model_setup_window.winfo_exists():
                    return
            except Exception:
                pass
        self.show_model_setup_wizard()


    def _close_model_setup_wizard(self, win=None, mark_completed=False, after_close=None):
        if mark_completed:
            self.cfg["local_model_setup_completed"] = True
            self.cfg["show_model_setup_wizard"] = False
            save_config(self.cfg)
        try:
            if win is not None:
                win.destroy()
        except Exception:
            pass
        self.model_setup_window = None
        if after_close:
            try:
                after_close()
            except Exception:
                pass


    def show_model_setup_wizard(self, after_close=None):
        """First-run choice: install local model now, skip, or decide later."""
        if getattr(self, "model_setup_window", None) is not None:
            try:
                if self.model_setup_window.winfo_exists():
                    self.model_setup_window.lift()
                    return
            except Exception:
                pass

        win, body = self.create_modal_shell(
            "Локальные ответы для JARVIS",
            "Можно сразу подготовить Ollama, а можно пользоваться обычными командами без дополнительных моделей.",
            width=760,
            height=560,
        )
        self.model_setup_window = win

        hero = tk.Frame(body, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        hero.pack(fill="x", pady=(0, 12))
        tk.Label(hero, text="Хотите включить локальные ответы?", bg=CARD_ALT, fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(hero, text="Обычные команды уже работают. Для дополнительных ответов через локальную модель можно один раз установить Ollama и модель llama3.2:1b.", bg=CARD_ALT, fg=MUTED, wraplength=690, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 14))

        cards = tk.Frame(body, bg=BG)
        cards.pack(fill="both", expand=True)

        left = tk.Frame(cards, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(left, text="Да, подготовить локальный режим", bg=CARD_ALT, fg=ACCENT_2, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 6))
        tk.Label(left, text="JARVIS запустит SETUP_LOCAL_MODEL_WINDOWS.bat. Скрипт попробует установить Ollama через winget и загрузить модель llama3.2:1b. Нужен интернет. После установки JARVIS лучше перезапустить.", bg=CARD_ALT, fg=MUTED, wraplength=310, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(0, 12))
        self.make_button(left, "Подготовить локальный режим", lambda: install_now(), variant="primary", font=("Segoe UI", 10, "bold"), padx=14, pady=10).pack(fill="x", padx=16, pady=(0, 12))

        right = tk.Frame(cards, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(right, text="Нет, только обычный JARVIS", bg=CARD, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 6))
        tk.Label(right, text="Ollama можно не устанавливать. Локальные команды всё равно работают: открыть блокнот, проводник, загрузки, калькулятор, сайты и напоминания. Облачный режим можно подключить позже своим API-ключом.", bg=CARD, fg=MUTED, wraplength=310, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(0, 12))
        self.make_button(right, "Пока без моделей", lambda: skip_ai(), variant="secondary", font=("Segoe UI", 10, "bold"), padx=14, pady=10).pack(fill="x", padx=16, pady=(0, 8))

        note = tk.Frame(body, bg=BG)
        note.pack(fill="x", pady=(12, 0))
        tk.Label(note, text="Выбор «Позже» оставит напоминание на следующий запуск. Выбор «Пока без моделей» отключит это окно.", bg=BG, fg=WARN, wraplength=710, justify="left", font=("Segoe UI", 9)).pack(anchor="w")

        def install_now():
            self.cfg["model_provider"] = "local"
            self.cfg["local_model_setup_completed"] = True
            self.cfg["show_model_setup_wizard"] = False
            save_config(self.cfg)
            try:
                if hasattr(self, "model_provider_var"):
                    self.model_provider_var.set("local")
            except Exception:
                pass
            self._close_model_setup_wizard(win, mark_completed=False, after_close=after_close)
            self.setup_local_model_ollama()

        def skip_ai():
            self._close_model_setup_wizard(win, mark_completed=True, after_close=after_close)
            self.post_response("Ок, работаем как обычный JARVIS. Локальный режим можно включить позже в настройках.")

        def later():
            self._close_model_setup_wizard(win, mark_completed=False, after_close=after_close)
            self.post_response("Ок, спросим про локальный режим позже. Локальные команды работают и без него.")

        try:
            win.protocol("WM_DELETE_WINDOW", later)
        except Exception:
            pass
        try:
            if hasattr(win, "_jarvis_close_btn"):
                win._jarvis_close_btn.configure(command=later)
        except Exception:
            pass

        btns = tk.Frame(body, bg=BG)
        btns.pack(fill="x", pady=(12, 0))
        self.make_button(btns, "Позже", later, variant="ghost", font=("Segoe UI", 10, "bold"), padx=14, pady=9).pack(side="left")
        self.make_button(btns, "Обычный JARVIS", skip_ai, variant="secondary", font=("Segoe UI", 10, "bold"), padx=14, pady=9).pack(side="right", padx=(0, 8))
        self.make_button(btns, "Да, подготовить", install_now, variant="primary", font=("Segoe UI", 10, "bold"), padx=14, pady=9).pack(side="right")


    def show_first_run_wizard(self):
        win, body = self.create_modal_shell("Первый запуск", "Быстрая настройка JARVIS: имя, хранение данных и параметры запуска.", width=760, height=700)
        note = tk.Frame(body, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        note.pack(fill="x", pady=(0, 12))
        tk.Label(note, text="Добро пожаловать в JARVIS", bg=CARD_ALT, fg=ACCENT, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(note, text="Мастер помогает выбрать место хранения данных и основные параметры первого запуска.", bg=CARD_ALT, fg=MUTED, wraplength=620, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 14))

        grid = tk.Frame(body, bg=BG)
        grid.pack(fill="both", expand=True)
        left = tk.Frame(grid, bg=BG)
        right = tk.Frame(grid, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        identity = tk.Frame(left, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        identity.pack(fill="x", pady=(0, 10))
        tk.Label(identity, text="Имена", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        tk.Label(identity, text="Как обращаться к тебе и как будет называться ассистент в окне.", bg=CARD_ALT, fg=MUTED, wraplength=290, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(0, 8))
        user_var = tk.StringVar(value=self.cfg.get("user_name", "Пользователь"))
        assistant_var = tk.StringVar(value=self.cfg.get("assistant_name", "JARVIS"))
        user_entry = tk.Entry(identity, textvariable=user_var)
        self.style_entry_widget(user_entry)
        user_entry.pack(fill="x", padx=16, pady=(0, 8), ipady=8)
        assistant_entry = tk.Entry(identity, textvariable=assistant_var)
        self.style_entry_widget(assistant_entry)
        assistant_entry.pack(fill="x", padx=16, pady=(0, 14), ipady=8)

        data_card = tk.Frame(left, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        data_card.pack(fill="x")
        tk.Label(data_card, text="Хранение данных", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        tk.Label(data_card, text="В портативном режиме данные хранятся рядом с JARVIS.exe. При обычной установке — в %APPDATA%\\JARVIS.", bg=CARD_ALT, fg=MUTED, wraplength=290, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(0, 8))
        mode_var = tk.StringVar(value=str(self.cfg.get("install_mode", STORAGE_MODE)))
        for value, title, desc in [("portable", "Портативный режим", "Данные рядом с приложением. Подходит для переноса на другой компьютер."), ("installed", "Обычная установка", "Данные в профиле пользователя Windows.")]:
            row = tk.Frame(data_card, bg=CARD_ALT)
            row.pack(fill="x", padx=14, pady=4)
            tk.Radiobutton(row, text=title, value=value, variable=mode_var, bg=CARD_ALT, fg=TEXT, activebackground=CARD_ALT, activeforeground=TEXT, selectcolor=PANEL_2, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(row, text=desc, bg=CARD_ALT, fg=MUTED, wraplength=260, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=(24,0))
        tk.Label(data_card, text=f"Текущая папка данных: {DATA_DIR}", bg=CARD_ALT, fg=ACCENT_2, wraplength=300, justify="left", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(8, 14))

        options = tk.Frame(right, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        options.pack(fill="x", pady=(0, 10))
        tk.Label(options, text="Параметры запуска", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        overlay_var = tk.BooleanVar(value=bool(self.cfg.get("overlay_enabled", False)))
        toast_var = tk.BooleanVar(value=bool(self.cfg.get("toast_notifications", True)))
        accept_var = tk.BooleanVar(value=bool(self.cfg.get("license_accepted", False)))
        keep_var = tk.BooleanVar(value=False)
        for txt,var in [
            ("Сразу открыть мини-оверлей", overlay_var),
            ("Оставить всплывающие уведомления включёнными", toast_var),
            ("Показать короткий список следующих шагов", self.onboarding_open_after_var),
            ("После мастера открыть настройки", self.onboarding_launch_settings_var),
            ("После мастера открыть быстрый запуск", self.onboarding_launch_launcher_var),
            ("Я понимаю, что это локальный проект и данные хранятся на моём компьютере", accept_var),
            ("Больше не показывать этот мастер", keep_var),
        ]:
            tk.Checkbutton(options, text=txt, variable=var, bg=CARD_ALT, fg=TEXT, activebackground=CARD_ALT, activeforeground=TEXT, selectcolor=CARD_ALT, font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=2)
        tk.Label(options, text="Режим хранения можно изменить позже через мастер переноса в настройках. Перед копированием JARVIS создаёт резервную копию данных.", bg=CARD_ALT, fg=WARN, wraplength=300, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(8, 14))

        guide = tk.Frame(right, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        guide.pack(fill="x", pady=(0, 0))
        tk.Label(guide, text="Что дальше", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=16, pady=(10, 4))
        tk.Label(guide, text="После сохранения можно открыть настройки и быстрый запуск. Для голосового ввода рядом с EXE нужна папка model с моделью Vosk.", bg=CARD_ALT, fg=MUTED, justify="left", wraplength=300, font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(0, 10))

        def save_and_close():
            self._persist_first_run_draft(
                mode_var.get(),
                user_var.get(),
                assistant_var.get(),
                accept_var.get(),
                overlay_var.get(),
                toast_var.get(),
                keep_var.get(),
            )
            try:
                win.destroy()
            except Exception:
                pass

        def cancel_and_close():
            try:
                win.destroy()
            except Exception:
                pass

        try:
            win.protocol("WM_DELETE_WINDOW", cancel_and_close)
        except Exception:
            pass
        try:
            if hasattr(win, "_jarvis_close_btn"):
                win._jarvis_close_btn.configure(command=cancel_and_close)
        except Exception:
            pass

        btns = tk.Frame(body, bg=BG)
        btns.pack(fill="x", pady=(12, 0))
        self.make_button(btns, "Отмена", cancel_and_close, variant="ghost", font=("Segoe UI", 10, "bold"), padx=14, pady=9).pack(side="left")
        self.make_button(btns, "OK", save_and_close, variant="ghost", font=("Segoe UI", 10, "bold"), padx=14, pady=9).pack(side="right", padx=(0, 8))
        self.make_button(btns, "Сохранить и стартовать", lambda: self.complete_first_run(win, mode_var.get(), user_var.get(), assistant_var.get(), accept_var.get(), overlay_var.get(), toast_var.get(), keep_var.get()), variant="primary", font=("Segoe UI", 10, "bold"), padx=14, pady=9).pack(side="right")


    def create_modal_shell(self, title, subtitle=None, width=620, height=400):
        win = tk.Toplevel(self.root)
        win.configure(bg=BORDER)
        win.resizable(True, True)
        win.transient(self.root)
        try:
            win.grab_set()
        except Exception:
            pass
        sx = max(40, int((win.winfo_screenwidth() - width) / 2))
        sy = max(40, int((win.winfo_screenheight() - height) / 2))
        win.geometry(f"{width}x{height}+{sx}+{sy}")

        shell = tk.Frame(win, bg=BG, highlightbackground=BORDER, highlightthickness=1)
        shell.pack(fill="both", expand=True, padx=1, pady=1)
        header = tk.Frame(shell, bg=PANEL_2, height=44)
        header.pack(fill="x")
        header.pack_propagate(False)
        left = tk.Frame(header, bg=PANEL_2)
        left.pack(side="left", fill="both", expand=True)
        tk.Label(left, text=title, bg=PANEL_2, fg=TEXT, font=("Segoe UI Semibold", 14)).pack(anchor="w", padx=16, pady=(8, 0))
        if subtitle:
            tk.Label(left, text=subtitle, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(0, 8))
        close_btn = self.make_button(header, "✕", lambda w=win: w.destroy(), variant="ghost", font=("Segoe UI", 9, "bold"), padx=10, pady=6)
        close_btn.pack(side="right", padx=10, pady=7)
        win._jarvis_close_btn = close_btn
        body = tk.Frame(shell, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=16)
        return win, body


    def make_shell_badge(self, parent, title, value, accent=ACCENT):
        badge = tk.Frame(parent, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        tk.Label(badge, text=title, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=10, pady=(8, 0))
        tk.Label(badge, text=value, bg=PANEL_2, fg=accent, font=("Segoe UI Semibold", 10)).pack(anchor="w", padx=10, pady=(3, 8))
        return badge


    def card(self, parent, bg=CARD, padx=16, pady=16):
        frame = tk.Frame(parent, bg=bg, highlightbackground=BORDER, highlightthickness=1, bd=0)
        frame.pack_propagate(False)
        return frame


    def section_title(self, parent, title, subtitle=None):
        tk.Label(parent, text=title, bg=parent.cget("bg"), fg=TEXT, font=("Segoe UI Semibold", 20)).pack(anchor="w")
        if subtitle:
            tk.Label(parent, text=subtitle, bg=parent.cget("bg"), fg=MUTED, font=("Segoe UI", 10), wraplength=860, justify="left").pack(anchor="w", pady=(5, 0))


    def render_empty_state(self, parent, title, subtitle, icon="✦", accent=None, bg=None):
        bg = bg or parent.cget("bg")
        accent = accent or ACCENT
        box = tk.Frame(parent, bg=bg, highlightbackground=BORDER, highlightthickness=1)
        tk.Label(box, text=icon, bg=bg, fg=accent, font=("Segoe UI Symbol", 24, "bold")).pack(pady=(16, 4))
        tk.Label(box, text=title, bg=bg, fg=TEXT, font=("Segoe UI", 12, "bold")).pack()
        tk.Label(box, text=subtitle, bg=bg, fg=MUTED, font=("Segoe UI", 9), wraplength=260, justify="center").pack(padx=18, pady=(6, 16))
        return box


    def pill(self, parent, text, fg=ACCENT, bg=PANEL_2):
        label = tk.Label(parent, text=text, bg=bg, fg=fg, font=("Segoe UI", 9, "bold"), padx=10, pady=5)
        return label


