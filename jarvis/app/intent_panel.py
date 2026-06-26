from .main_window_shared import *


class IntentPanelMixin:
    def combined_variants(self, label, base_variants):
        base = list(dict.fromkeys([normalize_text(v) for v in (base_variants or []) if normalize_text(v)]))
        custom = [normalize_text(v) for v in (self.cfg.get("custom_intents", {}).get(label, []) or []) if normalize_text(v)]
        merged = list(dict.fromkeys(base + custom))
        brand_map = {
            "open_telegram": "telegram",
            "open_discord": "discord",
            "open_steam": "steam",
            "open_twitch": "twitch",
            "open_youtube": "youtube",
        }
        brand_key = brand_map.get(label)
        if brand_key:
            for action in ACTION_ALIASES.get("open", []):
                for brand in BRAND_ALIASES.get(brand_key, []):
                    phrase = normalize_text(f"{action} {brand}")
                    if phrase:
                        merged.append(phrase)
        return list(dict.fromkeys(merged))


    def custom_intents_to_text(self):
        data = self.cfg.get("custom_intents", {}) or {}
        lines = []
        for key, _title in SUPPORTED_INTENTS:
            vals = data.get(key, [])
            if isinstance(vals, str):
                vals = [x.strip() for x in vals.split(",") if x.strip()]
            vals = [str(x).strip() for x in vals if str(x).strip()]
            if vals:
                lines.append(f"{key}: {', '.join(vals)}")
        if not lines:
            lines.append("# Пример: open_discord: открой дисс корт, запусти дескорд")
            lines.append("# Каждая строка: intent: фраза1, фраза2, фраза3")
        return "\n".join(lines)


    def parse_custom_intents_text(self, raw_text):
        result = {}
        for raw_line in raw_text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                raise ValueError(f"Нет двоеточия в строке: {line}")
            label, values = line.split(":", 1)
            label = label.strip()
            if label not in {k for k, _ in SUPPORTED_INTENTS}:
                raise ValueError(f"Неизвестный intent: {label}")
            phrases = [x.strip() for x in values.split(",") if x.strip()]
            result[label] = phrases
        return result


    def supported_intent_keys(self):
        return [k for k, _ in SUPPORTED_INTENTS]


    def current_editor_intent_key(self):
        raw = self.intent_editor_var.get().strip()
        if " — " in raw:
            raw = raw.split(" — ", 1)[0].strip()
        return raw or (SUPPORTED_INTENTS[0][0] if SUPPORTED_INTENTS else "")


    def refresh_custom_intents_editor(self, *_args):
        listbox = getattr(self, "intent_phrase_list", None)
        if listbox is None:
            return
        key = self.current_editor_intent_key()
        listbox.delete(0, "end")
        phrases = self.get_custom_variants(key)
        if not phrases:
            listbox.insert("end", "— пользовательских фраз пока нет —")
        else:
            for phrase in phrases:
                listbox.insert("end", phrase)


    def on_intent_editor_change(self, _event=None):
        self.intent_phrase_var.set("")
        self.refresh_custom_intents_editor()


    def add_phrase_to_selected_intent(self):
        key = self.current_editor_intent_key()
        phrase = normalize_text(self.intent_phrase_var.get())
        if not phrase:
            messagebox.showwarning("Пустая фраза", "Сначала впиши фразу для команды.")
            return
        data = self.cfg.get("custom_intents", {}) or {}
        values = data.get(key, [])
        if isinstance(values, str):
            values = [x.strip() for x in values.split(",") if x.strip()]
        values = [str(x).strip() for x in values if str(x).strip()]
        if phrase not in values:
            values.append(phrase)
        data[key] = values
        self.cfg["custom_intents"] = data
        self.custom_intents_text.delete("1.0", "end")
        self.custom_intents_text.insert("1.0", self.custom_intents_to_text())
        self.refresh_custom_intents_editor()
        self.intent_phrase_var.set("")
        self.post_log(f"[intent] Добавлена фраза для {key}: {phrase}")
        self.footer_var.set(f"Фраза добавлена: {phrase}")


    def load_selected_phrase_to_entry(self, _event=None):
        listbox = getattr(self, "intent_phrase_list", None)
        if listbox is None:
            return
        sel = listbox.curselection()
        if not sel:
            return
        value = listbox.get(sel[0])
        if value.startswith("— "):
            return
        self.intent_phrase_var.set(value)


    def remove_selected_phrase(self):
        key = self.current_editor_intent_key()
        listbox = getattr(self, "intent_phrase_list", None)
        if listbox is None:
            return
        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("Ничего не выбрано", "Сначала выбери фразу в списке.")
            return
        value = listbox.get(sel[0])
        if value.startswith("— "):
            return
        data = self.cfg.get("custom_intents", {}) or {}
        values = data.get(key, [])
        if isinstance(values, str):
            values = [x.strip() for x in values.split(",") if x.strip()]
        values = [str(x).strip() for x in values if str(x).strip() and str(x).strip() != value]
        if values:
            data[key] = values
        elif key in data:
            del data[key]
        self.cfg["custom_intents"] = data
        self.custom_intents_text.delete("1.0", "end")
        self.custom_intents_text.insert("1.0", self.custom_intents_to_text())
        self.refresh_custom_intents_editor()
        self.intent_phrase_var.set("")
        self.post_log(f"[intent] Удалена фраза для {key}: {value}")
        self.footer_var.set(f"Фраза удалена: {value}")



    def save_custom_intents(self):
        try:
            parsed = self.parse_custom_intents_text(self.custom_intents_text.get("1.0", "end"))
        except Exception as exc:
            messagebox.showerror("Ошибка словаря команд", str(exc))
            self.post_log(f"[intent] Ошибка словаря команд: {exc}")
            return
        self.cfg["custom_intents"] = parsed
        save_config(self.cfg)
        self.refresh_custom_intents_editor()
        self.post_log("[intent] Пользовательский словарь команд сохранён")
        self.footer_var.set("Словарь команд сохранён")
        self.response_var.set("Словарь команд обновлён.")


    def reset_custom_intents(self):
        self.cfg["custom_intents"] = {}
        save_config(self.cfg)
        self.custom_intents_text.delete("1.0", "end")
        self.custom_intents_text.insert("1.0", self.custom_intents_to_text())
        self.refresh_custom_intents_editor()
        self.post_log("[intent] Пользовательский словарь сброшен")
        self.footer_var.set("Словарь команд сброшен")


