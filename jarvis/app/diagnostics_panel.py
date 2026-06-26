from .main_window_shared import *


class DiagnosticsPanelMixin:
    def get_data_health_report(self):
        report = {
            "checked_at": now_iso(),
            "data_dir": str(DATA_DIR),
            "mode": STORAGE_MODE,
            "issues": [],
            "warnings": [],
            "files": [],
            "stats": {},
        }
        required = [
            ("config.json", CONFIG_PATH, "json"),
            ("notes.txt", NOTES_PATH, "text"),
            ("history.txt", HISTORY_PATH, "text"),
            ("reminders.json", REMINDERS_PATH, "json"),
            ("memory_profile.json", MEMORY_PATH, "json"),
            ("ui_session.json", SESSION_STATE_PATH, "json_optional"),
            ("system_events.log", SYSTEM_LOG_PATH, "text_optional"),
        ]
        for label, path, kind in required:
            item = {"name": label, "path": str(path), "exists": path.exists(), "size": 0, "status": "ok"}
            if path.exists():
                try:
                    item["size"] = path.stat().st_size
                except Exception:
                    item["size"] = 0
            if not path.exists():
                if kind.endswith("optional"):
                    item["status"] = "optional-missing"
                    report["warnings"].append(f"{label}: optional file отсутствует")
                else:
                    item["status"] = "missing"
                    report["issues"].append(f"{label}: обязательный файл отсутствует")
            elif kind.startswith("json"):
                try:
                    json.loads(path.read_text(encoding="utf-8"))
                except Exception as exc:
                    item["status"] = "broken-json"
                    report["issues"].append(f"{label}: JSON повреждён ({exc})")
            report["files"].append(item)

        backups = sorted(BACKUP_DIR.glob("*")) if BACKUP_DIR.exists() else []
        profile_backups = [p for p in backups if p.is_file() and p.name.startswith("jarvis_profile_backup_")]
        old_backups = []
        now_ts = time.time()
        for p in backups:
            try:
                age_days = (now_ts - p.stat().st_mtime) / 86400
            except Exception:
                age_days = 0
            if age_days > 14:
                old_backups.append(p.name)
        report["stats"] = {
            "backup_count": len(backups),
            "profile_backup_count": len(profile_backups),
            "old_backup_count": len(old_backups),
            "autosave_exists": AUTOSAVE_PROFILE_PATH.exists(),
            "session_exists": SESSION_STATE_PATH.exists(),
            "log_exists": SYSTEM_LOG_PATH.exists(),
            "data_size_bytes": self._dir_size(DATA_DIR),
        }
        if len(profile_backups) > 12:
            report["warnings"].append(f"Профильных backup слишком много: {len(profile_backups)}")
        if report["stats"]["data_size_bytes"] > 50 * 1024 * 1024:
            report["warnings"].append("Папка data стала тяжёлой — возможно, пора подчистить backup/log")
        if old_backups:
            report["warnings"].append(f"Старых backup старше 14 дней: {len(old_backups)}")
        return report


    def _dir_size(self, path: Path):
        total = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    try:
                        total += item.stat().st_size
                    except Exception:
                        pass
        except Exception:
            pass
        return total


    def _human_size(self, num):
        try:
            num = float(num)
        except Exception:
            return "0 B"
        for unit in ["B", "KB", "MB", "GB"]:
            if num < 1024 or unit == "GB":
                return f"{num:.1f} {unit}" if unit != "B" else f"{int(num)} {unit}"
            num /= 1024.0
        return f"{num:.1f} GB"


    def update_data_health_summary(self, report=None):
        report = report or self.get_data_health_report()
        issues = len(report.get("issues", []))
        warnings = len(report.get("warnings", []))
        size_text = self._human_size(report.get("stats", {}).get("data_size_bytes", 0))
        if issues:
            state = f"Найдены проблемы: {issues} • предупреждений: {warnings} • data: {size_text}"
        elif warnings:
            state = f"Health норм, но есть предупреждения: {warnings} • data: {size_text}"
        else:
            state = f"Health ок • backup: {report.get('stats', {}).get('backup_count', 0)} • data: {size_text}"
        if hasattr(self, "data_health_summary_var"):
            self.data_health_summary_var.set(state)
        return report


    def run_data_health_check(self):
        report = self.update_data_health_summary()
        try:
            DATA_HEALTH_REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
        self.append_system_event("health", f"Проверка data health • issues={len(report.get('issues', []))} warnings={len(report.get('warnings', []))}", toast=False)
        self.last_action_var.set("Проверка данных завершена")
        self.post_response("Проверка данных завершена. Состояние папки data обновлено.")
        return report


    def repair_data_files(self):
        repaired = []
        try:
            if not CONFIG_PATH.exists():
                save_config(self.cfg)
                repaired.append("config.json")
            if not NOTES_PATH.exists():
                NOTES_PATH.write_text("", encoding="utf-8")
                repaired.append("notes.txt")
            if not HISTORY_PATH.exists():
                HISTORY_PATH.write_text("", encoding="utf-8")
                repaired.append("history.txt")
            if not REMINDERS_PATH.exists():
                save_reminders([])
                repaired.append("reminders.json")
            else:
                try:
                    json.loads(REMINDERS_PATH.read_text(encoding="utf-8"))
                except Exception:
                    save_reminders([])
                    repaired.append("reminders.json(reset)")
            if not MEMORY_PATH.exists():
                save_memory_profile(self.memory)
                repaired.append("memory_profile.json")
            else:
                try:
                    json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
                except Exception:
                    save_memory_profile(self.memory)
                    repaired.append("memory_profile.json(reset)")
            if not SESSION_STATE_PATH.exists():
                SESSION_STATE_PATH.write_text("{}", encoding="utf-8")
                repaired.append("ui_session.json")
            if not SYSTEM_LOG_PATH.exists():
                SYSTEM_LOG_PATH.write_text("", encoding="utf-8")
                repaired.append("system_events.log")
            report = self.run_data_health_check()
            msg = ", ".join(repaired) if repaired else "Базовые файлы уже были в порядке"
            self.append_system_event("health", f"Repair data files: {msg}")
            messagebox.showinfo("Проверка данных", f"Восстановление завершено.\n\n{msg}\n\nПроблем осталось: {len(report.get('issues', []))}")
        except Exception as exc:
            self.append_system_event("health", f"Ошибка repair data: {exc}")
            messagebox.showerror("Проверка данных", f"Не удалось выполнить восстановление:\n{exc}")


    def cleanup_data_artifacts(self):
        removed = []
        errors = []
        try:
            backups = sorted([p for p in BACKUP_DIR.glob("jarvis_profile_backup_*.json") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)
            for stale in backups[8:]:
                try:
                    stale.unlink()
                    removed.append(stale.name)
                except Exception as exc:
                    errors.append(f"{stale.name}: {exc}")
            for stale in BACKUP_DIR.glob("pre_migration_*"):
                try:
                    age_days = (time.time() - stale.stat().st_mtime) / 86400
                except Exception:
                    age_days = 0
                if age_days > 14:
                    try:
                        if stale.is_dir():
                            shutil.rmtree(stale, ignore_errors=True)
                        else:
                            stale.unlink()
                        removed.append(stale.name)
                    except Exception as exc:
                        errors.append(f"{stale.name}: {exc}")
            if SYSTEM_LOG_PATH.exists():
                lines = SYSTEM_LOG_PATH.read_text(encoding="utf-8").splitlines()
                if len(lines) > 1200:
                    SYSTEM_LOG_PATH.write_text("\n".join(lines[-800:]) + "\n", encoding="utf-8")
                    removed.append("system_events.log(trimmed)")
            report = self.run_data_health_check()
            self.append_system_event("health", f"Cleanup data artifacts: removed={len(removed)} errors={len(errors)}")
            msg = "Удалено/подчищено:\n- " + "\n- ".join(removed) if removed else "Чистить почти нечего — временных файлов не нашёл."
            if errors:
                msg += "\n\nОшибки:\n- " + "\n- ".join(errors[:6])
            msg += f"\n\nПроблем после clean-up: {len(report.get('issues', []))}"
            messagebox.showinfo("Проверка данных", msg)
        except Exception as exc:
            self.append_system_event("health", f"Ошибка cleanup data: {exc}")
            messagebox.showerror("Проверка данных", f"Не удалось очистить данные:\n{exc}")


    def export_data_health_report(self):
        report = self.run_data_health_check()
        target = filedialog.asksaveasfilename(title="Сохранить health-отчёт", defaultextension=".json", filetypes=[("JSON", "*.json"), ("Text", "*.txt")], initialfile=f"jarvis_data_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        if not target:
            return
        try:
            if target.lower().endswith(".txt"):
                lines = [
                    f"JARVIS {APP_VERSION} Data Health Report",
                    f"Checked: {report['checked_at']}",
                    f"Data dir: {report['data_dir']}",
                    f"Mode: {report['mode']}",
                    "",
                    "Issues:",
                ]
                lines.extend([f"- {x}" for x in report.get("issues", [])] or ["- none"])
                lines.append("")
                lines.append("Warnings:")
                lines.extend([f"- {x}" for x in report.get("warnings", [])] or ["- none"])
                Path(target).write_text("\n".join(lines), encoding="utf-8")
            else:
                Path(target).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            self.append_system_event("health", f"Экспорт health-отчёта: {Path(target).name}", toast=False)
            self.post_response(f"Health-отчёт сохранён: {Path(target).name}")
        except Exception as exc:
            messagebox.showerror("Проверка данных", f"Не удалось сохранить отчёт:\n{exc}")


    def open_data_dir(self):
        try:
            os.startfile(str(DATA_DIR))
        except Exception:
            try:
                subprocess.Popen(["xdg-open", str(DATA_DIR)])
            except Exception:
                pass


    def open_logs_dir(self):
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            os.startfile(str(DATA_DIR))
        except Exception:
            try:
                subprocess.Popen(["xdg-open", str(DATA_DIR)])
            except Exception:
                pass


    def open_app_dir(self):
        try:
            os.startfile(str(APP_DIR))
        except Exception:
            try:
                subprocess.Popen(["xdg-open", str(APP_DIR)])
            except Exception:
                pass


    def show_data_health_center(self):
        report = self.run_data_health_check()
        win, body = self.create_modal_shell("Проверка данных", "Диагностика, восстановление и очистка пользовательских данных.", width=820, height=560)
        hero = tk.Frame(body, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        hero.pack(fill="x", pady=(0, 12))
        tk.Label(hero, text="Проверка данных", bg=CARD_ALT, fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(hero, text="Показывает состояние основных файлов, размер папки данных и количество резервных копий. Здесь же можно выполнить восстановление и очистку.", bg=CARD_ALT, fg=MUTED, wraplength=720, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 14))
        grid = tk.Frame(body, bg=BG)
        grid.pack(fill="both", expand=True)
        left = tk.Frame(grid, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right = tk.Frame(grid, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        stats = tk.Frame(left, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        stats.pack(fill="x", pady=(0, 10))
        tk.Label(stats, text="Сводка", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        for idx, (title, value, color) in enumerate([
            ("Проблемы", str(len(report.get("issues", []))), DANGER if report.get("issues") else ACCENT_2),
            ("Предупреждения", str(len(report.get("warnings", []))), WARN if report.get("warnings") else ACCENT),
            ("Размер data", self._human_size(report.get("stats", {}).get("data_size_bytes", 0)), ACCENT),
            ("Backup", str(report.get("stats", {}).get("backup_count", 0)), ACCENT_2),
        ]):
            badge = tk.Frame(stats, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
            badge.pack(fill="x", padx=16, pady=(0, 8))
            tk.Label(badge, text=title, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(10, 0))
            tk.Label(badge, text=value, bg=PANEL_2, fg=color, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=(4, 10))

        files_card = tk.Frame(left, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        files_card.pack(fill="both", expand=True)
        tk.Label(files_card, text="Основные файлы", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        files_text = tk.Text(files_card, height=16, wrap="word", font=("Consolas", 9))
        self.style_text_widget(files_text)
        files_text.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        lines = []
        for item in report.get("files", []):
            lines.append(f"[{item.get('status','ok')}] {item.get('name')} • {self._human_size(item.get('size', 0))}")
            lines.append(f"    {item.get('path','')}")
        files_text.insert("1.0", "\n".join(lines) if lines else "Пока нет данных")
        files_text.configure(state="disabled")

        issues_card = tk.Frame(right, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        issues_card.pack(fill="both", expand=True, pady=(0, 10))
        tk.Label(issues_card, text="Проблемы и предупреждения", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        issue_text = tk.Text(issues_card, height=16, wrap="word", font=("Consolas", 9))
        self.style_text_widget(issue_text)
        issue_text.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        out = []
        out.append("ISSUES:")
        out.extend([f"- {x}" for x in report.get("issues", [])] or ["- none"])
        out.append("")
        out.append("WARNINGS:")
        out.extend([f"- {x}" for x in report.get("warnings", [])] or ["- none"])
        issue_text.insert("1.0", "\n".join(out))
        issue_text.configure(state="disabled")

        action = tk.Frame(right, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        action.pack(fill="x")
        tk.Label(action, text="Действия", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        self.make_button(action, "Обновить проверку", lambda: [win.destroy(), self.show_data_health_center()], variant="secondary", font=("Segoe UI", 9, "bold"), padx=10, pady=7).pack(fill="x", padx=16, pady=(0, 6))
        self.make_button(action, "Repair missing/broken", lambda: [self.repair_data_files(), win.destroy()], variant="secondary", font=("Segoe UI", 9, "bold"), padx=10, pady=7).pack(fill="x", padx=16, pady=(0, 6))
        self.make_button(action, "Cleanup old artifacts", lambda: [self.cleanup_data_artifacts(), win.destroy()], variant="ghost", font=("Segoe UI", 9, "bold"), padx=10, pady=7).pack(fill="x", padx=16, pady=(0, 6))
        self.make_button(action, "Экспорт отчёта", self.export_data_health_report, variant="primary", font=("Segoe UI", 9, "bold"), padx=10, pady=7).pack(fill="x", padx=16, pady=(0, 6))
        self.make_button(action, "Открыть папку данных", self.open_data_dir, variant="ghost", font=("Segoe UI", 9, "bold"), padx=10, pady=7).pack(fill="x", padx=16, pady=(0, 16))



    def show_voice_diagnostics_center(self):
        report = diagnose_voice_environment()
        self.append_system_event("voice", f"Voice diagnostics • issues={len(report.get('issues', []))}", toast=False)
        win, body = self.create_modal_shell("Диагностика голоса", "Проверка Vosk model, пакетов vosk/sounddevice и микрофона.", width=820, height=560)
        hero = tk.Frame(body, bg=CARD_ALT, highlightbackground=BORDER, highlightthickness=1)
        hero.pack(fill="x", pady=(0, 12))
        title = "Диагностика голоса"
        subtitle = "Здесь видно, почему голос не стартует: нет model, нет vosk/sounddevice или Windows не отдаёт микрофон."
        tk.Label(hero, text=title, bg=CARD_ALT, fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(hero, text=subtitle, bg=CARD_ALT, fg=MUTED, wraplength=720, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 14))

        text_box = tk.Text(body, height=20, wrap="word", font=("Consolas", 10))
        self.style_text_widget(text_box)
        text_box.pack(fill="both", expand=True)
        text_box.insert("1.0", format_voice_diagnostics(report))
        text_box.configure(state="disabled")

        btns = tk.Frame(body, bg=BG)
        btns.pack(fill="x", pady=(12, 0))
        self.make_button(btns, "Повторить проверку", lambda: [win.destroy(), self.show_voice_diagnostics_center()], variant="secondary", font=("Segoe UI", 10, "bold"), padx=12, pady=8).pack(side="left")
        self.make_button(btns, "Тест голоса", self.test_voice, variant="secondary", font=("Segoe UI", 10, "bold"), padx=12, pady=8).pack(side="left", padx=(8, 0))
        self.make_button(btns, "Папка JARVIS", self.open_app_dir, variant="ghost", font=("Segoe UI", 10, "bold"), padx=12, pady=8).pack(side="left", padx=(8, 0))
        self.make_button(btns, "Папка данных", self.open_data_dir, variant="ghost", font=("Segoe UI", 10, "bold"), padx=12, pady=8).pack(side="left", padx=(8, 0))
        self.make_button(btns, "Лог", self.open_system_log_file, variant="ghost", font=("Segoe UI", 10, "bold"), padx=12, pady=8).pack(side="left", padx=(8, 0))
        self.make_button(btns, "Закрыть", win.destroy, variant="primary", font=("Segoe UI", 10, "bold"), padx=12, pady=8).pack(side="right")


    def build_system_page(self):
        page = tk.Frame(self.page_container, bg=BG)
        self.pages["system"] = page

        self.section_title(page, "Notification Center", "События запуска, восстановления, автосохранения и работы в трее собраны в одном журнале.")

        hero = self.card(page, bg=CARD_ALT)
        hero.pack(fill="x", pady=(12, 10))
        hero_inner = tk.Frame(hero, bg=CARD_ALT)
        hero_inner.pack(fill="both", expand=True, padx=18, pady=16)
        left_head = tk.Frame(hero_inner, bg=CARD_ALT)
        left_head.pack(side="left", fill="both", expand=True)
        tk.Label(left_head, text="Системный журнал", bg=CARD_ALT, fg=TEXT, font=("Segoe UI Semibold", 26)).pack(anchor="w")
        tk.Label(left_head, text="Показывает события запуска, восстановления, автосохранения, трея и уведомлений. Есть фильтры, поиск и экспорт.", bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 10), wraplength=760, justify="left").pack(anchor="w", pady=(4, 10))
        pills = tk.Frame(left_head, bg=CARD_ALT)
        pills.pack(anchor="w")
        self.pill(pills, "Восстановление", fg=WARN).pack(side="left", padx=(0, 8))
        self.pill(pills, "Автосохранение", fg=ACCENT_2).pack(side="left", padx=(0, 8))
        self.pill(pills, "Трей", fg=ACCENT).pack(side="left", padx=(0, 8))
        self.pill(pills, "Уведомления", fg="#ff9fb2").pack(side="left")

        stat_row = tk.Frame(left_head, bg=CARD_ALT)
        stat_row.pack(fill="x", pady=(14, 0))
        self.system_event_count_var = tk.StringVar(value="0")
        self.system_last_event_var = tk.StringVar(value="Пока пусто")
        self.system_unread_var = tk.StringVar(value="0")
        for idx, (title, var, color) in enumerate([
            ("Событий", self.system_event_count_var, ACCENT_2),
            ("Непрочитанных", self.system_unread_var, WARN),
            ("Последнее", self.system_last_event_var, TEXT),
        ]):
            stat = tk.Frame(stat_row, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
            stat.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 8, 0))
            tk.Label(stat, text=title, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(12, 0))
            tk.Label(stat, textvariable=var, bg=PANEL_2, fg=color, font=("Segoe UI", 11 if idx == 2 else 18, "bold"), wraplength=240, justify="left").pack(anchor="w", padx=14, pady=(6, 12))
            stat_row.grid_columnconfigure(idx, weight=1)

        right_head = tk.Frame(hero_inner, bg=CARD_ALT, width=300)
        right_head.pack(side="left", fill="y", padx=(16, 0))
        right_head.pack_propagate(False)
        action_box = tk.Frame(right_head, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        action_box.pack(fill="both", expand=True)
        tk.Label(action_box, text="Действия с журналом", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(12, 0))
        tk.Label(action_box, text="Быстрые действия", bg=PANEL_2, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16)
        tk.Label(action_box, text="Открой лог, выгрузи журнал или отметь всё прочитанным прямо отсюда без лишнего копания.", bg=PANEL_2, fg=MUTED, wraplength=250, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(4, 10))
        q1 = tk.Frame(action_box, bg=PANEL_2)
        q1.pack(fill="x", padx=16, pady=(0, 8))
        self.make_button(q1, "Экспорт", self.export_system_journal, variant="secondary", font=("Segoe UI", 9, "bold"), padx=10, pady=7).pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.make_button(q1, "Открыть лог", self.open_system_log_file, variant="ghost", font=("Segoe UI", 9, "bold"), padx=10, pady=7).pack(side="left", fill="x", expand=True)
        q2 = tk.Frame(action_box, bg=PANEL_2)
        q2.pack(fill="x", padx=16, pady=(0, 8))
        self.make_button(q2, "Прочитать всё", self.mark_system_events_read, variant="secondary", font=("Segoe UI", 9, "bold"), padx=10, pady=7).pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.make_button(q2, "Очистить", self.clear_system_journal, variant="danger", font=("Segoe UI", 9, "bold"), padx=10, pady=7).pack(side="left", fill="x", expand=True)
        self.make_button(action_box, "Voice diagnostics", self.show_voice_diagnostics_center, variant="secondary", font=("Segoe UI", 9, "bold"), padx=10, pady=8).pack(fill="x", padx=16, pady=(0, 8))
        self.make_button(action_box, "Открыть папку данных", self.open_data_dir, variant="ghost", font=("Segoe UI", 9, "bold"), padx=10, pady=8).pack(fill="x", padx=16, pady=(0, 8))
        self.make_button(action_box, "Тестовое уведомление", lambda: self.show_toast("System", "Тестовый toast из Notification Center."), variant="primary", font=("Segoe UI", 9, "bold"), padx=10, pady=8).pack(fill="x", padx=16, pady=(0, 12))

        tools_card = self.card(page, bg=CARD)
        tools_card.pack(fill="x", pady=(0, 10))
        row = tk.Frame(tools_card, bg=CARD)
        row.pack(fill="x", padx=16, pady=16)
        search_shell = tk.Frame(row, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        search_shell.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.system_search_var = tk.StringVar(value="")
        system_search = tk.Entry(search_shell, textvariable=self.system_search_var)
        self.style_entry_widget(system_search, font=("Segoe UI", 11))
        system_search.configure(bg=BG)
        system_search.pack(fill="x", expand=True, ipady=8, padx=10, pady=8)
        category_box = ttk.Combobox(row, style="Jarvis.TCombobox", textvariable=self.system_category_var, values=["все", "startup", "recovery", "session", "autosave", "backup", "tray", "journal", "toast", "exit"], state="readonly", width=12)
        category_box.pack(side="left", padx=(8, 8))
        category_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_system_journal_ui())
        tk.Checkbutton(row, text="Только непрочитанные", variable=self.system_unread_only_var, command=self.refresh_system_journal_ui, bg=CARD, fg=TEXT, activebackground=CARD, activeforeground=TEXT, selectcolor=CARD, font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        self.make_button(row, "Фильтр", self.refresh_system_journal_ui, variant="secondary", font=("Segoe UI", 9, "bold"), padx=10, pady=7).pack(side="left")

        body = tk.Frame(page, bg=BG)
        body.pack(fill="both", expand=True)
        left = self.card(body, bg=CARD_ALT)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = self.card(body, bg=CARD)
        right.pack(side="left", fill="y")
        right.configure(width=320)
        right.pack_propagate(False)

        log_head = tk.Frame(left, bg=CARD_ALT)
        log_head.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(log_head, text="Системный журнал", bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(side="left")
        self.pill(log_head, "Живая лента", fg=ACCENT_2, bg=PANEL_2).pack(side="right")
        self.system_log_text = tk.Text(left, wrap="word", font=("Consolas", 10))
        self.style_text_widget(self.system_log_text)
        self.system_log_text.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        tk.Label(right, text="Справка по журналу", bg=CARD, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        info_box = tk.Frame(right, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        info_box.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(info_box, text="Что здесь видно", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(10, 0))
        tk.Label(info_box, text="запуск • восстановление • автосохранение • резервные копии • трей • уведомления • выход", bg=PANEL_2, fg=TEXT, wraplength=250, justify="left", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(4, 10))
        filter_box = tk.Frame(right, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        filter_box.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(filter_box, text="Как читать ленту", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(10, 0))
        tk.Label(filter_box, text="Используй поиск, фильтр по категории и режим «Только непрочитанные», чтобы быстро найти нужное событие.", bg=PANEL_2, fg=TEXT, wraplength=250, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(4, 10))
        preview_box = tk.Frame(right, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        preview_box.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        tk.Label(preview_box, text="Последняя запись", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(10, 0))
        tk.Label(preview_box, textvariable=self.system_last_event_var, bg=PANEL_2, fg=TEXT, wraplength=250, justify="left", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(4, 10))
        tk.Label(preview_box, text="Подсказка", bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(4, 0))
        tk.Label(preview_box, text="Непрочитанные события можно отметить одной кнопкой. Журнал экспортируется в TXT или LOG.", bg=PANEL_2, fg=TEXT, wraplength=250, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(4, 10))
        self.refresh_system_journal_ui()


    def append_system_event(self, category: str, message: str, toast=None):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] [{category}] {message}"
        try:
            with SYSTEM_LOG_PATH.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass
        widget = getattr(self, "system_log_text", None)
        if widget is not None:
            widget.insert("end", line + "\n")
            widget.see("end")
        if hasattr(self, "system_last_event_var"):
            self.system_last_event_var.set(line)
        self.refresh_system_journal_stats()
        events_widget = getattr(self, "dashboard_events_text", None)
        if events_widget is not None:
            try:
                src = SYSTEM_LOG_PATH.read_text(encoding="utf-8").splitlines() if SYSTEM_LOG_PATH.exists() else []
            except Exception:
                src = []
            src = [ln for ln in src if ln.strip()][-5:]
            src.reverse()
            events_widget.delete("1.0", "end")
            if src:
                events_widget.insert("1.0", "\n".join(src) + "\n")
        if toast is None:
            toast = bool(self.system_event_toasts_var.get()) if hasattr(self, "system_event_toasts_var") else True
        if toast:
            self.show_toast(f"{category}", message)


    def refresh_system_journal_stats(self):
        lines = []
        try:
            if SYSTEM_LOG_PATH.exists():
                lines = [ln.rstrip() for ln in SYSTEM_LOG_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
        except Exception:
            lines = []
        if hasattr(self, "system_event_count_var"):
            self.system_event_count_var.set(str(len(lines)))
        if hasattr(self, "system_unread_var"):
            self.system_unread_var.set(str(self.system_unread_count))
        if hasattr(self, "system_nav_var"):
            label = "System Journal" if self.system_unread_count <= 0 else f"System Journal • {self.system_unread_count}"
            self.system_nav_var.set(label)
        if hasattr(self, "system_last_event_var") and lines:
            self.system_last_event_var.set(lines[-1])


    def refresh_system_journal_ui(self):
        widget = getattr(self, "system_log_text", None)
        if widget is None:
            return
        try:
            lines = SYSTEM_LOG_PATH.read_text(encoding="utf-8").splitlines() if SYSTEM_LOG_PATH.exists() else []
        except Exception:
            lines = []
        category = self.system_category_var.get().strip().lower() if hasattr(self, "system_category_var") else "все"
        needle = self.system_search_var.get().strip().lower() if hasattr(self, "system_search_var") else ""
        if category and category != "все":
            lines = [ln for ln in lines if f"[{category}]" in ln.lower()]
        if needle:
            lines = [ln for ln in lines if needle in ln.lower()]
        if getattr(self, "system_unread_only_var", None) is not None and bool(self.system_unread_only_var.get()):
            unread = max(0, int(getattr(self, "system_unread_count", 0)))
            if unread:
                lines = lines[-unread:]
            else:
                lines = []
        widget.delete("1.0", "end")
        if lines:
            widget.insert("1.0", "\n".join(lines) + "\n")
            widget.see("end")
        else:
            widget.insert("1.0", "System Journal пока пуст или текущий фильтр ничего не нашёл.\n")
        self.refresh_system_journal_stats()

    def clear_system_journal(self):
        try:
            if SYSTEM_LOG_PATH.exists():
                SYSTEM_LOG_PATH.unlink()
        except Exception:
            pass
        self.system_unread_count = 0
        self.refresh_system_journal_ui()
        self.append_system_event("journal", "System Journal очищен", toast=False)
        self.footer_var.set("Системный журнал очищен")


    def mark_system_events_read(self):
        self.system_unread_count = 0
        self.refresh_system_journal_stats()
        self.refresh_system_journal_ui()
        self.footer_var.set("Системный журнал отмечен как прочитанный")


    def export_system_journal(self):
        try:
            target = filedialog.asksaveasfilename(
                title="Экспорт System Journal",
                defaultextension=".txt",
                filetypes=[("Text file", "*.txt"), ("Log file", "*.log"), ("All files", "*.*")],
                initialfile=f"jarvis_system_journal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            )
            if not target:
                return
            content = SYSTEM_LOG_PATH.read_text(encoding="utf-8") if SYSTEM_LOG_PATH.exists() else ""
            Path(target).write_text(content, encoding="utf-8")
            self.footer_var.set(f"Журнал экспортирован: {Path(target).name}")
            self.append_system_event("journal", f"Экспорт журнала: {Path(target).name}", toast=False)
        except Exception as e:
            messagebox.showerror("Ошибка экспорта", str(e))


    def open_system_log_file(self):
        try:
            if not SYSTEM_LOG_PATH.exists():
                SYSTEM_LOG_PATH.write_text("", encoding="utf-8")
            os.startfile(str(SYSTEM_LOG_PATH))
        except Exception:
            try:
                self.open_folder(DATA_DIR)
            except Exception:
                pass


    def show_toast(self, title: str, message: str, duration=3200):
        if not bool(getattr(self, "toast_notifications_var", tk.BooleanVar(value=True)).get()):
            return
        try:
            if self.toast_window is not None and self.toast_window.winfo_exists():
                self.toast_window.destroy()
        except Exception:
            pass
        try:
            win = tk.Toplevel(self.root)
            self.toast_window = win
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            win.configure(bg=BORDER)
            win.wm_attributes("-alpha", 0.96)
            width, height = 360, 108
            rx = self.root.winfo_rootx() + self.root.winfo_width() - width - 24
            ry = self.root.winfo_rooty() + 72
            win.geometry(f"{width}x{height}+{rx}+{ry}")
            box = tk.Frame(win, bg=CARD_ALT, highlightbackground=ACCENT, highlightthickness=1)
            box.pack(fill="both", expand=True, padx=1, pady=1)
            tk.Label(box, text=title, bg=CARD_ALT, fg=ACCENT_2, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
            tk.Label(box, text=message, bg=CARD_ALT, fg=TEXT, justify="left", wraplength=328, font=("Segoe UI", 10)).pack(anchor="w", padx=14)
            tk.Label(box, text=datetime.now().strftime("%H:%M:%S"), bg=CARD_ALT, fg=MUTED, font=("Consolas", 9)).pack(anchor="e", padx=14, pady=(6, 10))
            try:
                if self.toast_after_id is not None:
                    self.root.after_cancel(self.toast_after_id)
            except Exception:
                pass
            self.toast_after_id = self.root.after(duration, self.hide_toast)
        except Exception:
            self.toast_window = None


    def hide_toast(self):
        try:
            if self.toast_window is not None and self.toast_window.winfo_exists():
                self.toast_window.destroy()
        except Exception:
            pass
        self.toast_window = None
        self.toast_after_id = None


