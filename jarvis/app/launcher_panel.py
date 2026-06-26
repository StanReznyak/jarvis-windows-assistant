from .main_window_shared import *


class LauncherPanelMixin:
    def build_launch_page(self):
        page = tk.Frame(self.page_container, bg=BG)
        self.pages["launch"] = page

        self.section_title(page, "Быстрый запуск", "Приложения, сайты, короткие команды и редактор элементов")

        hero = tk.Frame(page, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        hero.pack(fill="x", pady=(12, 12))
        hero_top = tk.Frame(hero, bg=PANEL)
        hero_top.pack(fill="x", padx=18, pady=(16, 12))
        hero_left = tk.Frame(hero_top, bg=PANEL)
        hero_left.pack(side="left", fill="both", expand=True)
        tk.Label(hero_left, text="БЫСТРЫЙ ЗАПУСК", bg=PANEL, fg=ACCENT, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(hero_left, text="Быстрый запуск приложений и сайтов", bg=PANEL, fg=TEXT, font=("Segoe UI Semibold", 22)).pack(anchor="w", pady=(3, 0))
        tk.Label(hero_left, text="Поиск сверху фильтрует приложения, сайты, короткие команды и список элементов. Плитки слева — для быстрого запуска, редактор справа — для настройки списка.", bg=PANEL, fg=MUTED, wraplength=760, justify="left", font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 0))
        hero_right = tk.Frame(hero_top, bg=PANEL)
        hero_right.pack(side="right", anchor="n")
        self.pill(hero_right, "Быстрый запуск", fg=ACCENT).pack(side="left", padx=(0, 8))
        self.pill(hero_right, "Команды", fg=ACCENT_2).pack(side="left", padx=(0, 8))
        self.pill(hero_right, "Резервная копия", fg=WARN).pack(side="left")

        stats = tk.Frame(hero, bg=PANEL)
        stats.pack(fill="x", padx=18, pady=(0, 16))
        self.launcher_stat_apps_var = tk.StringVar(value="0")
        self.launcher_stat_sites_var = tk.StringVar(value="0")
        self.launcher_stat_alias_var = tk.StringVar(value="0")
        self.launcher_stat_search_var = tk.StringVar(value="Фильтр: нет")
        for title, var, accent_color in [
            ("Приложения", self.launcher_stat_apps_var, ACCENT),
            ("Сайты", self.launcher_stat_sites_var, ACCENT_2),
            ("Alias", self.launcher_stat_alias_var, WARN),
            ("Поиск", self.launcher_stat_search_var, TEXT),
        ]:
            box = tk.Frame(stats, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
            box.pack(side="left", fill="x", expand=True, padx=(0, 10))
            tk.Label(box, text=title, bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
            tk.Label(box, textvariable=var, bg=CARD_ALT, fg=accent_color, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=12, pady=(2, 10))

        search_row = tk.Frame(page, bg=BG)
        search_row.pack(fill="x", pady=(0, 10))
        search_shell = tk.Frame(search_row, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        search_shell.pack(side="left", fill="x", expand=True)
        tk.Label(search_shell, text="⌕", bg=PANEL, fg=ACCENT, font=("Segoe UI Symbol", 14, "bold")).pack(side="left", padx=(12, 8))
        search_entry = tk.Entry(search_shell, textvariable=self.launcher_search_var)
        self.style_entry_widget(search_entry, font=("Segoe UI", 11))
        search_entry.configure(bg=PANEL, highlightthickness=0)
        search_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 12), pady=10)
        self.make_button(search_row, "Найти", self.refresh_launcher_ui, variant="ghost", pady=10).pack(side="left", padx=(10, 0))
        self.make_button(search_row, "Сбросить", lambda: (self.launcher_search_var.set(""), self.refresh_launcher_ui()), variant="secondary", pady=10).pack(side="left", padx=(8, 0))

        top = tk.Frame(page, bg=BG)
        top.pack(fill="both", expand=True, pady=(0, 10))

        left = self.card(top)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = self.card(top, bg=CARD_ALT)
        right.pack(side="left", fill="y")
        right.configure(width=390)
        right.pack_propagate(False)

        hub = tk.Frame(left, bg=CARD)
        hub.pack(fill="both", expand=True, padx=16, pady=16)

        quick_row = tk.Frame(hub, bg=CARD)
        quick_row.pack(fill="x", pady=(0, 14))
        quick_left = tk.Frame(quick_row, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        quick_left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(quick_left, text="Быстрый запуск", bg=PANEL_2, fg=ACCENT, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 0))
        tk.Label(quick_left, text="Плитки запуска", bg=PANEL_2, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=14, pady=(3, 0))
        tk.Label(quick_left, text="Нажмите плитку — JARVIS сразу откроет нужный сайт или приложение. Здесь лучше держать только самые частые элементы.", bg=PANEL_2, fg=MUTED, wraplength=420, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(6, 12))
        quick_right = tk.Frame(quick_row, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        quick_right.pack(side="left", fill="y")
        tk.Label(quick_right, text="Быстрые команды", bg=CARD_ALT, fg=ACCENT_2, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(12, 2))
        quick_buttons = tk.Frame(quick_right, bg=CARD_ALT)
        quick_buttons.pack(fill="x", padx=12, pady=(0, 12))
        for label, command in [("Панель", "панель"), ("Быстрая панель", "quick bar"), ("Работа", "рабочий режим"), ("Тишина", "тихий режим")]:
            self.make_button(quick_buttons, label, lambda t=command: self.handle_command(t), variant="ghost", font=("Segoe UI", 9, "bold"), padx=12, pady=8).pack(fill="x", pady=(0, 6))

        apps_panel = tk.Frame(hub, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        apps_panel.pack(fill="x", pady=(0, 12))
        apps_head = tk.Frame(apps_panel, bg=CARD)
        apps_head.pack(fill="x", padx=14, pady=(12, 0))
        tk.Label(apps_head, text="Любимые приложения", bg=CARD, fg=ACCENT, font=("Segoe UI", 12, "bold")).pack(side="left")
        self.pill(apps_head, "ПРИЛОЖЕНИЯ", fg=ACCENT, bg=PANEL_2).pack(side="right")
        tk.Label(apps_panel, text="EXE и рабочие инструменты, которые ты запускаешь чаще всего.", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(4, 8))
        self.launcher_apps_grid = tk.Frame(apps_panel, bg=CARD)
        self.launcher_apps_grid.pack(fill="x", padx=8, pady=(0, 10))

        sites_panel = tk.Frame(hub, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        sites_panel.pack(fill="x", pady=(0, 8))
        sites_head = tk.Frame(sites_panel, bg=CARD)
        sites_head.pack(fill="x", padx=14, pady=(12, 0))
        tk.Label(sites_head, text="Любимые сайты", bg=CARD, fg=ACCENT_2, font=("Segoe UI", 12, "bold")).pack(side="left")
        self.pill(sites_head, "САЙТЫ", fg=ACCENT_2, bg=PANEL_2).pack(side="right")
        tk.Label(sites_panel, text="Частые ссылки, сервисы и рабочие точки входа в один клик.", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(4, 8))
        self.launcher_sites_grid = tk.Frame(sites_panel, bg=CARD)
        self.launcher_sites_grid.pack(fill="x", padx=8, pady=(0, 10))

        tk.Label(right, text="Редактор быстрого запуска", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        tk.Label(right, text="Добавляйте приложения, сайты и короткие команды. Выберите элемент, измените название, путь, ссылку или иконку и сохраните без ручной правки файлов.", bg=CARD_ALT, fg=MUTED, wraplength=330, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=16)

        editor_pill_row = tk.Frame(right, bg=CARD_ALT)
        editor_pill_row.pack(fill="x", padx=16, pady=(10, 8))
        self.pill(editor_pill_row, "Редактор", fg=ACCENT, bg=PANEL_2).pack(side="left", padx=(0, 8))
        self.pill(editor_pill_row, "Профиль", fg=ACCENT_2, bg=PANEL_2).pack(side="left", padx=(0, 8))
        self.pill(editor_pill_row, "Копия", fg=WARN, bg=PANEL_2).pack(side="left")

        app_box = tk.Frame(right, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        app_box.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(app_box, text="Приложение", bg=PANEL_2, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
        app_name = tk.Entry(app_box, textvariable=self.launcher_app_name_var)
        self.style_entry_widget(app_name, font=("Segoe UI", 10))
        app_name.configure(bg=BG)
        app_name.pack(fill="x", ipady=7, pady=(6, 6), padx=12)
        app_path = tk.Entry(app_box, textvariable=self.launcher_app_path_var)
        self.style_entry_widget(app_path, font=("Segoe UI", 10))
        app_path.configure(bg=BG)
        app_path.pack(fill="x", ipady=7, pady=(0, 6), padx=12)
        app_btns = tk.Frame(app_box, bg=PANEL_2)
        app_btns.pack(fill="x", padx=12, pady=(0, 12))
        self.make_button(app_btns, "Выбрать EXE", self.pick_launcher_app_path, variant="secondary").pack(side="left", padx=(0, 6))
        self.make_button(app_btns, "Сохранить приложение", self.save_launcher_app, variant="primary").pack(side="left")

        site_box = tk.Frame(right, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        site_box.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(site_box, text="Сайт", bg=PANEL_2, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
        site_name = tk.Entry(site_box, textvariable=self.launcher_site_name_var)
        self.style_entry_widget(site_name, font=("Segoe UI", 10))
        site_name.configure(bg=BG)
        site_name.pack(fill="x", ipady=7, pady=(6, 6), padx=12)
        site_url = tk.Entry(site_box, textvariable=self.launcher_site_url_var)
        self.style_entry_widget(site_url, font=("Segoe UI", 10))
        site_url.configure(bg=BG)
        site_url.pack(fill="x", ipady=7, pady=(0, 6), padx=12)
        self.make_button(site_box, "Сохранить сайт", self.save_launcher_site, variant="success").pack(anchor="w", padx=12, pady=(0, 12))

        icon_box = tk.Frame(right, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        icon_box.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(icon_box, text="Иконка плитки", bg=PANEL_2, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
        icon_entry = tk.Entry(icon_box, textvariable=self.launcher_icon_var)
        self.style_entry_widget(icon_entry, font=("Segoe UI", 10))
        icon_entry.configure(bg=BG)
        icon_entry.pack(fill="x", ipady=7, pady=(6, 6), padx=12)
        tk.Label(icon_box, text="Примеры: 🚀  🎮  ✈  🌐  💼", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(0, 10))

        alias_box = tk.Frame(right, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        alias_box.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(alias_box, text="Команда-псевдоним", bg=PANEL_2, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
        alias_name = tk.Entry(alias_box, textvariable=self.alias_name_var)
        self.style_entry_widget(alias_name, font=("Segoe UI", 10))
        alias_name.configure(bg=BG)
        alias_name.pack(fill="x", ipady=7, pady=(6, 6), padx=12)
        alias_target = tk.Entry(alias_box, textvariable=self.alias_target_var)
        self.style_entry_widget(alias_target, font=("Segoe UI", 10))
        alias_target.configure(bg=BG)
        alias_target.pack(fill="x", ipady=7, pady=(0, 6), padx=12)
        self.make_button(alias_box, "Сохранить псевдоним", self.save_alias_mapping, variant="ghost").pack(anchor="w", padx=12, pady=(0, 12))

        tk.Label(right, text="Что писать:\n• приложение: Telegram Work / C:/Tools/app.exe\n• сайт: работа / https://github.com\n• псевдоним: работа / открой сайт github", bg=CARD_ALT, fg=MUTED, justify="left", wraplength=330, font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(4, 6))
        self.launcher_summary_var = tk.StringVar(value="Быстрый запуск готов")
        tk.Label(right, textvariable=self.launcher_summary_var, bg=CARD_ALT, fg=ACCENT, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16, pady=(0, 8))

        lists = tk.Frame(right, bg=CARD_ALT)
        lists.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        alias_wrap = tk.Frame(lists, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        alias_wrap.pack(fill="x", pady=(0, 10))
        tk.Label(alias_wrap, text="Сохранённые псевдонимы", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=12, pady=(10, 0))
        self.alias_listbox = tk.Listbox(alias_wrap, height=6)
        self.style_listbox_widget(self.alias_listbox, font=("Segoe UI", 10))
        self.alias_listbox.pack(fill="x", padx=12, pady=(6, 6))
        self.make_button(alias_wrap, "Удалить выбранный псевдоним", self.delete_selected_alias, variant="secondary").pack(fill="x", padx=12, pady=(0, 12))

        profile_wrap = tk.Frame(lists, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        profile_wrap.pack(fill="x", pady=(0, 10))
        tk.Label(profile_wrap, text="Профиль и резервная копия", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=12, pady=(10, 0))
        profile_btns = tk.Frame(profile_wrap, bg=PANEL_2)
        profile_btns.pack(fill="x", padx=12, pady=(8, 0))
        self.make_button(profile_btns, "Импорт профиля", self.import_jarvis_profile, variant="secondary").pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.make_button(profile_btns, "Экспорт профиля", self.export_jarvis_profile, variant="secondary").pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.make_button(profile_btns, "Бэкап", self.quick_backup_profile, variant="ghost").pack(side="left", fill="x", expand=True)
        backup_btns = tk.Frame(profile_wrap, bg=PANEL_2)
        backup_btns.pack(fill="x", padx=12, pady=(8, 12))
        tk.Checkbutton(backup_btns, text="Автосохранение профиля", variable=self.profile_autosave_var, bg=PANEL_2, fg=TEXT, activebackground=PANEL_2, activeforeground=TEXT, selectcolor=PANEL_2, font=("Segoe UI", 9)).pack(side="left")
        self.make_button(backup_btns, "Восстановить автосохранение", self.restore_autosave_profile, variant="secondary", font=("Segoe UI", 9, "bold"), padx=10, pady=6).pack(side="right")

        items_wrap = tk.Frame(lists, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        items_wrap.pack(fill="both", expand=True)
        tk.Label(items_wrap, text="Сохранённые приложения / сайты", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=12, pady=(10, 0))
        self.launcher_items_listbox = tk.Listbox(items_wrap, height=8)
        self.style_listbox_widget(self.launcher_items_listbox, font=("Segoe UI", 10))
        self.launcher_items_listbox.pack(fill="both", expand=True, padx=12, pady=(6, 6))
        item_btns = tk.Frame(items_wrap, bg=PANEL_2)
        item_btns.pack(fill="x", padx=12, pady=(0, 12))
        for label, cmd in [
            ("↑ Приложение", lambda: self.launcher_move_item("apps", -1)),
            ("↓ Приложение", lambda: self.launcher_move_item("apps", 1)),
            ("↑ Сайт", lambda: self.launcher_move_item("sites", -1)),
            ("↓ Сайт", lambda: self.launcher_move_item("sites", 1)),
            ("Редактировать", self.load_selected_launcher_item_into_editor),
            ("Удалить", self.delete_selected_launcher_item),
            ("Обновить", self.refresh_launcher_ui),
        ]:
            self.make_button(item_btns, label, cmd, variant="secondary", font=("Segoe UI", 9, "bold"), padx=10, pady=7).pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.launcher_items_listbox.bind("<Double-Button-1>", lambda e: self.load_selected_launcher_item_into_editor())
        self.launcher_search_var.trace_add("write", lambda *args: self.refresh_launcher_ui())
        self.refresh_launcher_ui()

    def launcher_icon_for_app(self, name, path):
        custom = (self.cfg.get("launcher_app_icons", {}) or {}).get(normalize_text(name), "").strip()
        if custom:
            return custom
        name_l = normalize_text(name)
        path_l = str(path).lower()
        text = f"{name_l} {path_l}"
        if "telegram" in text:
            return "✈"
        if "discord" in text:
            return "🎧"
        if "steam" in text or "epic" in text:
            return "🎮"
        if "chrome" in text or "browser" in text or "firefox" in text or "opera" in text or "edge" in text:
            return "🌐"
        if "notepad" in text or "code" in text or "pycharm" in text or "studio" in text:
            return "💻"
        if "obs" in text:
            return "🎥"
        if "spotify" in text or "music" in text:
            return "🎵"
        if "explorer" in text or "folder" in text:
            return "📁"
        if "photoshop" in text or "paint" in text:
            return "🎨"
        return "⚙"


    def launcher_icon_for_site(self, name, url):
        custom = (self.cfg.get("launcher_site_icons", {}) or {}).get(normalize_text(name), "").strip()
        if custom:
            return custom
        text = f"{name} {url}".lower()
        if "youtube" in text or "ютуб" in text:
            return "▶"
        if "github" in text or "гитхаб" in text:
            return "✦"
        if "music" in text or "музык" in text or "spotify" in text:
            return "🎵"
        if "github" in text:
            return "⌘"
        if "google" in text or "гугл" in text or "yandex" in text or "яндекс" in text:
            return "🔎"
        if "telegram" in text or "t.me" in text:
            return "✈"
        if "discord" in text:
            return "🎧"
        if "vk" in text or "vkontakte" in text:
            return "VK"
        if "notion" in text:
            return "N"
        if "drive.google" in text:
            return "☁"
        return "🌍"


    def launcher_ordered_items(self, kind):
        if kind == "apps":
            data = dict(self.cfg.get("favorite_apps", {}) or {})
            order_key = "launcher_order_apps"
        else:
            data = dict(self.cfg.get("favorite_sites", {}) or {})
            order_key = "launcher_order_sites"
        order = [normalize_text(x) for x in (self.cfg.get(order_key, []) or [])]
        items = []
        seen = set()
        for key in order:
            if key in data and key not in seen:
                items.append((key, data[key]))
                seen.add(key)
        for key, value in data.items():
            nk = normalize_text(key)
            if nk not in seen:
                items.append((nk, value))
                seen.add(nk)
        self.cfg[order_key] = [key for key, _ in items]
        return items


    def launcher_move_item(self, kind, direction):
        if not hasattr(self, "launcher_items_listbox"):
            return
        sel = self.launcher_items_listbox.curselection()
        if not sel:
            self.post_response("Выбери приложение или сайт для перемещения.")
            return
        line = self.launcher_items_listbox.get(sel[0])
        item_kind, name, _value = [part.strip() for part in line.split("|", 2)]
        if kind == "apps" and item_kind != "APP":
            self.post_response("Для этого действия выбери приложение.")
            return
        if kind == "sites" and item_kind != "SITE":
            self.post_response("Для этого действия выбери сайт.")
            return
        order_key = "launcher_order_apps" if kind == "apps" else "launcher_order_sites"
        ordered = [k for k, _ in self.launcher_ordered_items(kind)]
        target = normalize_text(name)
        if target not in ordered:
            self.post_response("Не нашёл элемент в списке быстрого запуска.")
            return
        idx = ordered.index(target)
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(ordered):
            self.post_response("Дальше двигать уже некуда.")
            return
        ordered[idx], ordered[new_idx] = ordered[new_idx], ordered[idx]
        self.cfg[order_key] = ordered
        save_config(self.cfg)
        self.refresh_launcher_ui(select_key=target, select_kind=kind)
        self.post_response(f"Сдвинул {name} {'выше' if direction < 0 else 'ниже'}.")


    def launcher_chip(self, parent, title, subtitle, command, accent_color=None, icon="⚡", edit_command=None):
        accent_color = accent_color or ACCENT
        normal_bg = PANEL_2
        hover_bg = CARD_ALT
        card = tk.Frame(parent, bg=normal_bg, highlightbackground=BORDER, highlightthickness=1)
        top_line = tk.Frame(card, bg=accent_color, height=4)
        top_line.pack(fill="x")
        inner = tk.Frame(card, bg=normal_bg)
        inner.pack(fill="both", expand=True, padx=10, pady=10)
        icon_row = tk.Frame(inner, bg=normal_bg)
        icon_row.pack(fill="x")
        icon_shell = tk.Frame(icon_row, bg=BG, highlightbackground=BORDER, highlightthickness=1)
        icon_shell.pack(side="left")
        icon_label = tk.Label(icon_shell, text=icon, bg=BG, fg=accent_color, font=("Segoe UI Symbol", 16, "bold"), padx=10, pady=7)
        icon_label.pack()
        type_pill = tk.Label(icon_row, text="запуск", bg=BG, fg=accent_color, font=("Segoe UI", 8, "bold"), padx=8, pady=3)
        type_pill.pack(side="left", padx=(8, 0), anchor="n")
        edit_btn = None
        if edit_command is not None:
            edit_btn = tk.Button(icon_row, text="✎", command=edit_command, bg=normal_bg, fg=MUTED, activebackground=hover_bg, activeforeground=accent_color, relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"))
            edit_btn.pack(side="right")
        action_btn = tk.Button(inner, text=title, command=command, bg=normal_bg, fg=TEXT, activebackground=hover_bg, activeforeground=accent_color, relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"), wraplength=180, justify="left", anchor="w", padx=0, pady=10)
        action_btn.pack(fill="x")
        sub = tk.Label(inner, text=subtitle, bg=normal_bg, fg=MUTED, font=("Segoe UI", 8), wraplength=180, justify="left", anchor="w")
        sub.pack(fill="x")
        footer = tk.Label(inner, text="ENTER → запустить", bg=normal_bg, fg=accent_color, font=("Segoe UI", 8, "bold"))
        footer.pack(anchor="w", pady=(10, 0))
        targets = [inner, icon_row, icon_shell, icon_label, action_btn, sub, footer]
        if edit_btn is not None:
            targets.append(edit_btn)
        self.bind_hover_lift(card, normal_bg, hover_bg, targets=targets)
        return card

    def refresh_launcher_ui(self, select_key=None, select_kind=None):
        query = normalize_text(self.launcher_search_var.get()) if hasattr(self, "launcher_search_var") else ""
        app_items = self.launcher_ordered_items("apps")
        site_items = self.launcher_ordered_items("sites")
        alias_items = sorted((self.cfg.get("aliases", {}) or {}).items())
        if query:
            app_items = [(name, path) for name, path in app_items if query in normalize_text(name) or query in normalize_text(str(path))]
            site_items = [(name, url) for name, url in site_items if query in normalize_text(name) or query in normalize_text(str(url))]
            alias_items = [(key, value) for key, value in alias_items if query in normalize_text(key) or query in normalize_text(str(value))]
        if hasattr(self, "launcher_apps_grid"):
            for child in self.launcher_apps_grid.winfo_children():
                child.destroy()
            visible_apps = app_items[:8]
            if not visible_apps:
                box = self.render_empty_state(self.launcher_apps_grid, "Нет приложений", "Добавь exe справа или сбрось поиск, если ничего не найдено.", icon="💻", accent=ACCENT, bg=CARD)
                box.pack(fill="x", pady=6)
            else:
                for idx, (name, path) in enumerate(visible_apps):
                    chip = self.launcher_chip(self.launcher_apps_grid, name, Path(str(path)).name or str(path), lambda n=name: self.launch_named_app(n), icon=self.launcher_icon_for_app(name, path), edit_command=lambda n=name: self.load_launcher_item_into_editor("apps", n))
                    r, c = divmod(idx, 4)
                    chip.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
                    self.launcher_apps_grid.columnconfigure(c, weight=1)
        if hasattr(self, "launcher_sites_grid"):
            for child in self.launcher_sites_grid.winfo_children():
                child.destroy()
            visible_sites = site_items[:8]
            if not visible_sites:
                box = self.render_empty_state(self.launcher_sites_grid, "Нет сайтов", "Добавь ссылку справа или сбрось фильтр, чтобы снова показать сохранённые сайты.", icon="🌐", accent=ACCENT_2, bg=CARD)
                box.pack(fill="x", pady=6)
            else:
                for idx, (name, url) in enumerate(visible_sites):
                    chip = self.launcher_chip(self.launcher_sites_grid, name, str(url).replace("https://", "").replace("http://", "")[:28], lambda n=name: self.launch_named_site(n), accent_color=ACCENT_2, icon=self.launcher_icon_for_site(name, url), edit_command=lambda n=name: self.load_launcher_item_into_editor("sites", n))
                    r, c = divmod(idx, 4)
                    chip.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
                    self.launcher_sites_grid.columnconfigure(c, weight=1)
        if hasattr(self, "alias_listbox"):
            self.alias_listbox.delete(0, "end")
            for key, value in alias_items:
                self.alias_listbox.insert("end", f"{key} → {value}")
            if not alias_items:
                self.alias_listbox.insert("end", "— alias пока пусты")
        if hasattr(self, "launcher_items_listbox"):
            self.launcher_items_listbox.delete(0, "end")
            for key, value in app_items:
                self.launcher_items_listbox.insert("end", f"APP | {key} | {value}")
            for key, value in site_items:
                self.launcher_items_listbox.insert("end", f"SITE | {key} | {value}")
            if self.launcher_items_listbox.size() == 0:
                self.launcher_items_listbox.insert("end", "— ничего не найдено")
        if hasattr(self, "launcher_summary_var"):
            self.launcher_summary_var.set(f"Быстрый запуск: приложений {len(app_items)} • сайтов {len(site_items)} • псевдонимов {len(alias_items)}")
        if hasattr(self, "launcher_stat_apps_var"):
            self.launcher_stat_apps_var.set(str(len(app_items)))
        if hasattr(self, "launcher_stat_sites_var"):
            self.launcher_stat_sites_var.set(str(len(site_items)))
        if hasattr(self, "launcher_stat_alias_var"):
            self.launcher_stat_alias_var.set(str(len(alias_items)))
        if hasattr(self, "launcher_stat_search_var"):
            self.launcher_stat_search_var.set(f"Фильтр: {query if query else 'нет'}")
        if hasattr(self, "quickbar_hint_var") and self.quickbar_hint_var is not None:
            suggestions = self.get_quickbar_suggestions()
            if suggestions:
                self.quickbar_hint_var.set("  •  ".join(suggestions[:3]))

    def pick_launcher_app_path(self):
        path = filedialog.askopenfilename(title="Выберите EXE для быстрого запуска", filetypes=[("EXE", "*.exe"), ("Все файлы", "*.*")])
        if path:
            self.launcher_app_path_var.set(path)


    def save_launcher_app(self):
        name = normalize_text(self.launcher_app_name_var.get())
        path = self.launcher_app_path_var.get().strip()
        if not name or not path:
            self.post_response("Для приложения нужно имя и путь к exe.")
            return
        fav = dict(self.cfg.get("favorite_apps", {}) or {})
        icons = dict(self.cfg.get("launcher_app_icons", {}) or {})
        original = normalize_text(self.launcher_edit_original_var.get()) if self.launcher_edit_kind_var.get() == "apps" else ""
        if original and original != name:
            old_val = fav.pop(original, None)
            old_icon = icons.pop(original, "")
            if old_val is not None and not path:
                path = old_val
            if self.launcher_icon_var.get().strip() == "" and old_icon:
                icons[name] = old_icon
        fav[name] = path
        icon_value = self.launcher_icon_var.get().strip()
        if icon_value:
            icons[name] = icon_value
        else:
            icons.pop(name, None)
        self.cfg["favorite_apps"] = fav
        self.cfg["launcher_app_icons"] = icons
        order = [k for k in (self.cfg.get("launcher_order_apps", []) or []) if k in fav]
        if original and original in order and original != name:
            order = [name if k == original else k for k in order]
        if name not in order:
            order.append(name)
        self.cfg["launcher_order_apps"] = order
        save_config(self.cfg)
        self.launcher_app_name_var.set("")
        self.launcher_app_path_var.set("")
        self.launcher_icon_var.set("")
        self.launcher_edit_kind_var.set("")
        self.launcher_edit_original_var.set("")
        self.refresh_launcher_ui()
        self.last_action_var.set(f"Сохранено приложение: {name}")
        self.post_response(f"Сохранил приложение «{name}» в быстром запуске.")


    def save_launcher_site(self):
        name = normalize_text(self.launcher_site_name_var.get())
        url = self.launcher_site_url_var.get().strip()
        if not name or not url:
            self.post_response("Для сайта нужно имя и ссылка.")
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        fav = dict(self.cfg.get("favorite_sites", {}) or {})
        icons = dict(self.cfg.get("launcher_site_icons", {}) or {})
        original = normalize_text(self.launcher_edit_original_var.get()) if self.launcher_edit_kind_var.get() == "sites" else ""
        if original and original != name:
            old_val = fav.pop(original, None)
            old_icon = icons.pop(original, "")
            if old_val is not None and not url:
                url = old_val
            if self.launcher_icon_var.get().strip() == "" and old_icon:
                icons[name] = old_icon
        fav[name] = url
        icon_value = self.launcher_icon_var.get().strip()
        if icon_value:
            icons[name] = icon_value
        else:
            icons.pop(name, None)
        self.cfg["favorite_sites"] = fav
        self.cfg["launcher_site_icons"] = icons
        order = [k for k in (self.cfg.get("launcher_order_sites", []) or []) if k in fav]
        if original and original in order and original != name:
            order = [name if k == original else k for k in order]
        if name not in order:
            order.append(name)
        self.cfg["launcher_order_sites"] = order
        save_config(self.cfg)
        self.launcher_site_name_var.set("")
        self.launcher_site_url_var.set("")
        self.launcher_icon_var.set("")
        self.launcher_edit_kind_var.set("")
        self.launcher_edit_original_var.set("")
        self.refresh_launcher_ui()
        self.last_action_var.set(f"Сохранён сайт: {name}")
        self.post_response(f"Сохранил сайт «{name}» в быстром запуске.")


    def save_alias_mapping(self):
        alias = normalize_text(self.alias_name_var.get())
        target = self.alias_target_var.get().strip()
        if not alias or not target:
            self.post_response("Для alias нужны короткое слово и целевая команда.")
            return
        data = dict(self.cfg.get("aliases", {}) or {})
        data[alias] = target
        self.cfg["aliases"] = data
        save_config(self.cfg)
        self.alias_name_var.set("")
        self.alias_target_var.set("")
        self.refresh_launcher_ui()
        self.last_action_var.set(f"Сохранён alias: {alias}")
        self.post_response(f"Alias {alias} теперь ведёт на: {target}")


    def load_launcher_item_into_editor(self, kind, name):
        key = normalize_text(name)
        if kind == "apps":
            data = dict(self.cfg.get("favorite_apps", {}) or {})
            icons = dict(self.cfg.get("launcher_app_icons", {}) or {})
            value = data.get(key, "")
            self.launcher_app_name_var.set(key)
            self.launcher_app_path_var.set(value)
            self.launcher_site_name_var.set("")
            self.launcher_site_url_var.set("")
            self.launcher_icon_var.set(icons.get(key, ""))
        else:
            data = dict(self.cfg.get("favorite_sites", {}) or {})
            icons = dict(self.cfg.get("launcher_site_icons", {}) or {})
            value = data.get(key, "")
            self.launcher_site_name_var.set(key)
            self.launcher_site_url_var.set(value)
            self.launcher_app_name_var.set("")
            self.launcher_app_path_var.set("")
            self.launcher_icon_var.set(icons.get(key, ""))
        self.launcher_edit_kind_var.set(kind)
        self.launcher_edit_original_var.set(key)
        self.last_action_var.set(f"Редактирование быстрого запуска: {key}")
        self.post_response(f"Загрузил {key} в редактор. Меняй поля справа и жми сохранить.")


    def load_selected_launcher_item_into_editor(self):
        if not hasattr(self, "launcher_items_listbox"):
            return
        sel = self.launcher_items_listbox.curselection()
        if not sel:
            self.post_response("Выбери приложение или сайт для редактирования.")
            return
        line = self.launcher_items_listbox.get(sel[0])
        kind, name, _value = [part.strip() for part in line.split("|", 2)]
        self.load_launcher_item_into_editor("apps" if kind == "APP" else "sites", name)


    def export_jarvis_profile(self):
        profile = {
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
        path = filedialog.asksaveasfilename(title="Экспорт профиля JARVIS", defaultextension=".json", filetypes=[("JARVIS Profile", "*.json"), ("JSON", "*.json")], initialfile="jarvis_profile_export.json")
        if not path:
            return
        try:
            Path(path).write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
            self.last_action_var.set("Профиль экспортирован")
            self.post_response(f"Профиль JARVIS экспортирован: {Path(path).name}")
        except Exception as exc:
            self.post_log(f"[profile-export] ошибка: {exc}")
            self.post_response("Не смог экспортировать профиль JARVIS.")


    def import_jarvis_profile(self):
        path = filedialog.askopenfilename(title="Импорт профиля JARVIS", filetypes=[("JSON", "*.json"), ("Все файлы", "*.*")])
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
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
            self.last_action_var.set("Профиль импортирован")
            self.post_response(f"Профиль JARVIS импортирован из {Path(path).name}")
        except Exception as exc:
            self.post_log(f"[profile-import] ошибка: {exc}")
            self.post_response("Не смог импортировать профиль. Проверь JSON-файл.")


    def delete_selected_alias(self):
        if not hasattr(self, "alias_listbox"):
            return
        sel = self.alias_listbox.curselection()
        if not sel:
            self.post_response("Выбери alias для удаления.")
            return
        line = self.alias_listbox.get(sel[0])
        alias = line.split("→", 1)[0].strip()
        data = dict(self.cfg.get("aliases", {}) or {})
        if alias in data:
            data.pop(alias, None)
            self.cfg["aliases"] = data
            save_config(self.cfg)
            self.refresh_launcher_ui()
            self.post_response(f"Удалил alias {alias}.")


    def delete_selected_launcher_item(self):
        if not hasattr(self, "launcher_items_listbox"):
            return
        sel = self.launcher_items_listbox.curselection()
        if not sel:
            self.post_response("Выбери приложение или сайт для удаления.")
            return
        line = self.launcher_items_listbox.get(sel[0])
        kind, name, _value = [part.strip() for part in line.split("|", 2)]
        if kind == "APP":
            data = dict(self.cfg.get("favorite_apps", {}) or {})
            data.pop(name, None)
            key = normalize_text(name)
            self.cfg["favorite_apps"] = data
            self.cfg["launcher_order_apps"] = [k for k in (self.cfg.get("launcher_order_apps", []) or []) if k != key]
            icons = dict(self.cfg.get("launcher_app_icons", {}) or {})
            icons.pop(key, None)
            self.cfg["launcher_app_icons"] = icons
        else:
            data = dict(self.cfg.get("favorite_sites", {}) or {})
            data.pop(name, None)
            key = normalize_text(name)
            self.cfg["favorite_sites"] = data
            self.cfg["launcher_order_sites"] = [k for k in (self.cfg.get("launcher_order_sites", []) or []) if k != key]
            icons = dict(self.cfg.get("launcher_site_icons", {}) or {})
            icons.pop(key, None)
            self.cfg["launcher_site_icons"] = icons
        save_config(self.cfg)
        self.refresh_launcher_ui()
        self.post_response(f"Удалил «{name}» из быстрого запуска.")


    def launch_named_app(self, name):
        data = self.cfg.get("favorite_apps", {}) or {}
        path = data.get(normalize_text(name)) or data.get(name)
        if not path:
            self.post_response(f"Не нашёл приложение {name}.")
            return False
        try:
            subprocess.Popen([path])
            self.last_action_var.set(f"Открыто приложение: {name}")
            self.post_response(f"Запускаю {name}.")
            return True
        except Exception as exc:
            self.post_log(f"[launcher-app] ошибка: {exc}")
            self.post_response(f"Не смог запустить {name}. Проверь путь к exe.")
            return False


    def launch_named_site(self, name):
        data = self.cfg.get("favorite_sites", {}) or {}
        url = data.get(normalize_text(name)) or data.get(name)
        if not url:
            self.post_response(f"Не нашёл сайт {name}.")
            return False
        webbrowser.open(url)
        self.last_action_var.set(f"Открыт сайт: {name}")
        self.post_response(f"Открываю {name}.")
        return True


    def apply_alias_command(self, text):
        aliases = self.cfg.get("aliases", {}) or {}
        key = normalize_text(text)
        target = aliases.get(key)
        if not target:
            return False
        self.post_log(f"[alias] {key} -> {target}")
        self.handle_command(target, source="alias")
        return True


    def open_launcher_site_or_app(self, text):
        t = normalize_text(text)
        if t.startswith(("найди ", "поиск ", "поищи ", "найди в интернете ")):
            query = re.sub(r"^(найди в интернете|найди|поиск|поищи)\s+", "", t).strip()
            if query:
                webbrowser.open("https://www.google.com/search?q=" + query.replace(" ", "+"))
                self.last_action_var.set(f"Поиск: {query}")
                self.post_response(f"Ищу в интернете: {query}.")
                return True
        if t.startswith("запусти "):
            name = t.split("запусти ", 1)[1].strip()
            if name and self.launch_named_app(name):
                return True
            if name and self.open_common_target(name):
                return True
        if t.startswith("открой "):
            name = t.split("открой ", 1)[1].strip()
            apps = self.cfg.get("favorite_apps", {}) or {}
            sites = self.cfg.get("favorite_sites", {}) or {}
            if name in apps and self.launch_named_app(name):
                return True
            if name in sites and self.launch_named_site(name):
                return True
            if name and self.open_common_target(name):
                return True
        return False


    def open_common_target(self, name: str) -> bool:
        target = normalize_text(name)
        if not target:
            return False
        folder_map = {
            "загрузки": "downloads",
            "скачанные": "downloads",
            "документы": "documents",
            "рабочий стол": "desktop",
        }
        if target in folder_map:
            if self.open_folder(folder_map[target]):
                self.last_action_var.set(f"Открыто: {target}")
                self.post_response(f"Открываю {target}.")
                return True
        safe_apps = {
            "калькулятор": ["calc"],
            "calculator": ["calc"],
            "блокнот": ["notepad"],
            "notepad": ["notepad"],
            "проводник": ["explorer"],
            "explorer": ["explorer"],
            "пейнт": ["mspaint"],
            "paint": ["mspaint"],
            "командную строку": ["cmd"],
            "cmd": ["cmd"],
            "powershell": ["powershell"],
            "настройки": ["cmd", "/c", "start", "ms-settings:"],
        }
        if target in safe_apps:
            try:
                subprocess.Popen(safe_apps[target], shell=False)
                self.last_action_var.set(f"Открыто: {target}")
                self.post_response(f"Открываю {target}.")
                return True
            except Exception as exc:
                self.post_log(f"[open-common] {target}: {exc}")
                self.post_response(f"Не смог открыть {target}.")
                return True
        if "." in target and " " not in target:
            url = target if target.startswith("http") else f"https://{target}"
            webbrowser.open(url)
            self.last_action_var.set(f"Открыт сайт: {target}")
            self.post_response(f"Открываю сайт {target}.")
            return True
        return False


    def open_folder(self, folder_name: str):
        base = Path.home()
        mapping = {
            "downloads": base / "Downloads",
            "documents": base / "Documents",
            "desktop": base / "Desktop",
        }
        path = mapping.get(folder_name)
        try:
            os.startfile(str(path))
            return True
        except Exception:
            return False


    def open_control_panel(self):
        try:
            subprocess.Popen(["control"])
            return True
        except Exception:
            return False


    def open_taskmgr(self):
        try:
            subprocess.Popen(["taskmgr"])
            return True
        except Exception:
            return False


    def show_desktop_windows(self):
        try:
            script = '(New-Object -ComObject Shell.Application).MinimizeAll()'
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creationflags)
            return True
        except Exception:
            return False


    def open_site_from_text(self, text: str):
        t = normalize_text(text)
        site = t.split("открой сайт",1)[1].strip() if "открой сайт" in t else ""
        if not site:
            return False
        fav = self.cfg.get("favorite_sites", {}) or {}
        url = fav.get(site)
        if not url:
            if site.startswith("http"):
                url = site
            elif "." in site:
                url = f"https://{site}"
            else:
                url = f"https://www.google.com/search?q={site.replace(' ', '+')}"
        webbrowser.open(url)
        self.last_action_var.set(f"Открыт сайт: {site}")
        self.post_response(f"Открываю сайт {site}.")
        return True


