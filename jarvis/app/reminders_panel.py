from .main_window_shared import *


class RemindersPanelMixin:
    def refresh_reminders_ui(self):
        latest = load_reminders_any()
        if isinstance(latest, list):
            self.reminders = latest
        active = [r for r in sorted(self.reminders, key=lambda x: x.get("when", "")) if not r.get("done")]
        self.reminder_count_var.set(str(len(active)))
        self.reminder_status_var.set(f"Напоминаний: {len(active)}")

        if hasattr(self, "reminders_listbox"):
            try:
                self.reminders_listbox.delete(0, "end")
                if active:
                    for item in active:
                        self.reminders_listbox.insert("end", format_reminder_item(item))
                else:
                    self.reminders_listbox.insert("end", "Активных напоминаний пока нет.")
            except Exception:
                pass

        lines = []
        if active:
            for idx, item in enumerate(active[:8], 1):
                try:
                    when_text = datetime.fromisoformat(item.get("when", "")).strftime("%d.%m %H:%M")
                except Exception:
                    when_text = item.get("when", "")
                lines.append(f"{idx}. {when_text} — {item.get('text','')}")
        else:
            lines = ["Активных напоминаний пока нет."]

        full_text = "\n".join(lines)
        short_text = "\n".join(lines[:4])
        self.reminder_feed_var.set(full_text)
        self.reminder_feed_short_var.set(short_text)

        if hasattr(self, "reminders_notes_feed_listbox"):
            try:
                self.reminders_notes_feed_listbox.delete(0, "end")
                for line in lines[:4]:
                    self.reminders_notes_feed_listbox.insert("end", line)
            except Exception:
                pass

        for widget_name in ("reminders_preview", "reminders_live_text", "reminders_hero_text", "reminders_memory_feed_text", "reminders_notes_feed_text"):
            widget = getattr(self, widget_name, None)
            if widget is None:
                continue
            try:
                widget.configure(state="normal")
                widget.delete("1.0", "end")
                widget.insert("1.0", full_text)
                widget.configure(state="disabled")
            except Exception:
                try:
                    widget.configure(text=full_text)
                except Exception:
                    pass

        try:
            self.root.update_idletasks()
        except Exception:
            pass
        self.update_stats()


    def add_reminder(self, when_dt: datetime, text: str, repeat: str | None = None):
        item = {
            "id": f"r{int(time.time()*1000)}",
            "when": when_dt.replace(microsecond=0).isoformat(),
            "text": text.strip(),
            "done": False,
            "created_at": now_iso(),
        }
        if repeat:
            item["repeat"] = repeat
        self.reminders.append(item)
        self.reminders = sorted(self.reminders, key=lambda x: x.get("when", ""))
        save_reminders(self.reminders)
        self.refresh_reminders_ui()
        return item


    def get_active_reminders(self):
        return [r for r in sorted(self.reminders, key=lambda x: x.get("when", "")) if not r.get("done")]


    def get_latest_active_reminder(self):
        active = [r for r in self.reminders if not r.get("done")]
        if not active:
            return None
        def _created_key(item):
            return item.get("created_at") or item.get("when") or item.get("id") or ""
        return sorted(active, key=_created_key)[-1]


    def delete_reminder_by_id(self, reminder_id: str):
        before = len(self.reminders)
        self.reminders = [r for r in self.reminders if r.get("id") != reminder_id]
        if len(self.reminders) == before:
            return False
        save_reminders(self.reminders)
        self.refresh_reminders_ui()
        return True


    def handle_delete_reminder_command(self, text: str):
        cmd = parse_reminder_delete_command(text)
        if not cmd:
            return False
        active = self.get_active_reminders()
        if not active:
            self.post_response("Активных напоминаний нет.")
            return True

        def delete_last_with_message():
            target = self.get_latest_active_reminder()
            if not target:
                self.post_response("Активных напоминаний нет.")
                return True
            self.delete_reminder_by_id(target.get("id"))
            target_when = target.get("when", "")
            try:
                from datetime import datetime as _dt
                target_when = _dt.fromisoformat(target_when).strftime('%d.%m %H:%M')
            except Exception:
                pass
            self.last_action_var.set(f"Удалено последнее напоминание: {target.get('text','')}")
            self.post_response(f"Удалил последнее напоминание: {target_when} — {target.get('text','')}")
            return True

        mode = cmd.get("mode")
        if mode == "all":
            self.reminders = [r for r in self.reminders if r.get("done")]
            save_reminders(self.reminders)
            self.refresh_reminders_ui()
            self.last_action_var.set("Удалены все напоминания")
            self.post_response("Удалил все активные напоминания.")
            return True
        if mode == "last":
            return delete_last_with_message()
        if mode == "index":
            index = max(1, int(cmd.get("index", 0))) - 1
            if index >= len(active):
                self.post_response("Нет напоминания с таким номером. Скажи: покажи напоминания.")
                return True
            target = active[index]
            self.delete_reminder_by_id(target.get("id"))
            self.last_action_var.set(f"Удалено напоминание #{index + 1}")
            self.post_response(f"Удалил напоминание номер {index + 1}: {target.get('text','')}")
            return True
        if mode == "text":
            raw_query = normalize_text(cmd.get("text", ""))
            query = re.sub(r"\b(?:телегу|телега|телеграм|телеги|тг|де|это|эти|эту|их|его|её|ее|мне|напоминание|напоминания)\b", " ", raw_query)
            query = re.sub(r"\s+", " ", query).strip()
            for target in active:
                target_text = normalize_text(target.get("text", ""))
                if query and (query in target_text or target_text in query):
                    self.delete_reminder_by_id(target.get("id"))
                    self.last_action_var.set(f"Удалено напоминание: {target.get('text','')}")
                    self.post_response(f"Удалил напоминание: {target.get('text','')}")
                    return True
            compact = compact_text(text)
            weak_delete = compact.startswith(("удали", "убери", "удалить", "убрать")) or ("удали" in compact or "убери" in compact)
            reminderish = ("напомин" in raw_query) or ("напомин" in compact) or any(token in compact for token in ["телегу", "телега", "телеграм", "телеги"])
            if not query or len(query.split()) <= 2 or reminderish or weak_delete:
                return delete_last_with_message()
            self.post_response("Не нашёл такое напоминание. Скажи точнее или открой список.")
            return True
        return False


    def delete_last_reminder(self):
        target = self.get_latest_active_reminder()
        if not target:
            self.post_response("Активных напоминаний нет.")
            return
        self.delete_reminder_by_id(target.get("id"))
        target_when = target.get("when", "")
        try:
            from datetime import datetime as _dt
            target_when = _dt.fromisoformat(target_when).strftime('%d.%m %H:%M')
        except Exception:
            pass
        self.last_action_var.set("Удалено последнее напоминание")
        self.post_response(f"Удалил последнее напоминание: {target_when} — {target.get('text','')}")


    def delete_selected_reminder(self):
        if not hasattr(self, "reminders_listbox"):
            return
        sel = self.reminders_listbox.curselection()
        if not sel:
            return
        visible = [r for r in sorted(self.reminders, key=lambda x: x.get("when", "")) if not r.get("done")]
        idx = sel[0]
        if idx >= len(visible):
            return
        target_id = visible[idx].get("id")
        self.reminders = [r for r in self.reminders if r.get("id") != target_id]
        save_reminders(self.reminders)
        self.refresh_reminders_ui()
        self.post_response("Удалил напоминание.")


    def _play_reminder_melody(self, mode: str | None = None):
        melody_mode = str(mode or self.cfg.get("reminder_melody_mode", "loud") or "loud").lower()

        def worker():
            try:
                if winsound is not None and os.name == "nt":
                    patterns = {
                        "soft": [(880, 120), (988, 140), (1047, 160)],
                        "normal": [(988, 160), (1319, 180), (1568, 220)],
                        "loud": [(784, 160), (988, 180), (1319, 220), (1568, 260)],
                    }
                    selected = patterns.get(melody_mode, patterns["loud"])
                    loops = 1 if melody_mode != "loud" else 2
                    for _ in range(loops):
                        for freq, duration in selected:
                            winsound.Beep(freq, duration)
                            time.sleep(0.04)
                        time.sleep(0.08)
                else:
                    loops = 3 if melody_mode == "loud" else 2
                    for _ in range(loops):
                        try:
                            self.root.after(0, self.root.bell)
                        except Exception:
                            pass
                        time.sleep(0.18)
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()


    def test_reminder_melody(self):
        self.save_ui_config()
        mode = str(self.reminder_melody_mode_var.get() or "loud")
        self.post_log(f"[reminder] тест мелодии | mode={mode}")
        self._play_reminder_melody(mode=mode)
        self.post_response("Тест мелодии напоминания запущен.")


    def _fire_reminder_alert_once(self, item, pass_index: int, total_passes: int):
        text = str(item.get("text", "")).strip()
        if not text:
            text = "без текста"
        self._play_reminder_melody()
        if pass_index == 0:
            self.show_page("memory")
        self.post_response(f"Напоминание {pass_index + 1} из {total_passes}: {text}")
        self.post_log(f"[reminder] сигнал {pass_index + 1}/{total_passes}: {text}")


    def _dispatch_triggered_reminder(self, item):
        total_passes = max(1, int(self.cfg.get("reminder_alert_repeats", 3)))
        delay_ms = int(max(1.0, float(self.cfg.get("reminder_alert_interval_sec", 4.5))) * 1000)
        for pass_index in range(total_passes):
            self.root.after(delay_ms * pass_index, lambda idx=pass_index, payload=dict(item): self._fire_reminder_alert_once(payload, idx, total_passes))
        self.post_log(f"[reminder] поставлено повторов: {total_passes} | interval_ms={delay_ms} | text={item.get('text','')}")


    def check_reminders(self):
        now = datetime.now()
        triggered = []
        changed = False
        for item in self.reminders:
            if item.get("done"):
                continue
            try:
                when = datetime.fromisoformat(item.get("when", ""))
            except Exception:
                continue
            if when <= now:
                repeat = item.get("repeat")
                if repeat:
                    nxt = next_recurring_time(when, repeat)
                    if nxt:
                        original_when = item.get("when", "")
                        item["when"] = nxt.replace(microsecond=0).isoformat()
                        item["last_triggered_at"] = now_iso()
                        triggered.append({**item, "trigger_when": original_when})
                        changed = True
                        continue
                item["done"] = True
                triggered.append(item)
                changed = True
        if changed:
            save_reminders(self.reminders)
            self.refresh_reminders_ui()
        for item in triggered:
            self._dispatch_triggered_reminder(item)
            self.post_log(f"[reminder] сработало: {item.get('text','')} @ {item.get('trigger_when', item.get('when',''))}")
        self.root.after(1000, self.check_reminders)


