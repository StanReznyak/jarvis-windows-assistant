from .main_window_shared import *


class SettingsRuntimeMixin:
    def save_ui_config(self):
        self.cfg["auto_tts"] = bool(self.tts_var.get())
        self.cfg["auto_start_voice"] = bool(self.auto_start_voice_var.get()) if hasattr(self, "auto_start_voice_var") else bool(self.cfg.get("auto_start_voice", True))
        self.cfg["auto_start_voice_user_disabled"] = not bool(self.cfg.get("auto_start_voice", True))
        self.cfg["tts_preferred_engine"] = self.tts_engine_var.get()
        self.cfg["voice_input_engine"] = self.voice_input_engine_var.get()
        self.cfg["speechkit_api_key"] = self.speechkit_api_key_var.get().strip() if hasattr(self, "speechkit_api_key_var") else self.cfg.get("speechkit_api_key", "")
        self.cfg["speechkit_folder_id"] = self.speechkit_folder_id_var.get().strip() if hasattr(self, "speechkit_folder_id_var") else self.cfg.get("speechkit_folder_id", "")
        self.cfg["speechkit_lang"] = self.speechkit_lang_var.get() if hasattr(self, "speechkit_lang_var") else self.cfg.get("speechkit_lang", "ru-RU")
        self.cfg["speechkit_topic"] = self.speechkit_topic_var.get() if hasattr(self, "speechkit_topic_var") else self.cfg.get("speechkit_topic", "general")
        self.cfg["whisper_model_size"] = self.whisper_model_var.get() if hasattr(self, "whisper_model_var") else self.cfg.get("whisper_model_size", "small")
        self.cfg["whisper_compute_type"] = self.whisper_compute_var.get() if hasattr(self, "whisper_compute_var") else self.cfg.get("whisper_compute_type", "int8")
        self.cfg["whisper_device"] = self.whisper_device_var.get() if hasattr(self, "whisper_device_var") else self.cfg.get("whisper_device", "auto")
        self.cfg["whisper_cpp_cli_path"] = self.whisper_cpp_cli_var.get().strip() if hasattr(self, "whisper_cpp_cli_var") else self.cfg.get("whisper_cpp_cli_path", "")
        self.cfg["whisper_cpp_model_path"] = self.whisper_cpp_model_var.get().strip() if hasattr(self, "whisper_cpp_model_var") else self.cfg.get("whisper_cpp_model_path", "")
        self.cfg["whisper_cpp_language"] = self.whisper_cpp_lang_var.get().strip() if hasattr(self, "whisper_cpp_lang_var") else self.cfg.get("whisper_cpp_language", "ru")
        self.cfg["whisper_cpp_threads"] = max(1, int(self.whisper_cpp_threads_var.get())) if hasattr(self, "whisper_cpp_threads_var") else int(self.cfg.get("whisper_cpp_threads", 4) or 4)
        self.cfg["model_answers_enabled"] = bool(self.model_answers_enabled_var.get()) if hasattr(self, "model_answers_enabled_var") else bool(self.cfg.get("model_answers_enabled", True))
        self.cfg["model_fallback_unknown"] = bool(self.model_fallback_unknown_var.get()) if hasattr(self, "model_fallback_unknown_var") else bool(self.cfg.get("model_fallback_unknown", True))
        self.cfg["model_provider"] = self.model_provider_var.get().strip() if hasattr(self, "model_provider_var") else self.cfg.get("model_provider", "auto")
        self.cfg["ollama_base_url"] = self.ollama_base_url_var.get().strip() if hasattr(self, "ollama_base_url_var") else self.cfg.get("ollama_base_url", "http://127.0.0.1:11434")
        self.cfg["ollama_model"] = self.ollama_model_var.get().strip() if hasattr(self, "ollama_model_var") else self.cfg.get("ollama_model", "llama3.2:1b")
        self.cfg["ollama_max_output_tokens"] = max(120, int(self.ollama_max_tokens_var.get())) if hasattr(self, "ollama_max_tokens_var") else int(self.cfg.get("ollama_max_output_tokens", 500) or 500)
        self.cfg["cloud_api_key"] = self.cloud_api_key_var.get().strip() if hasattr(self, "cloud_api_key_var") else self.cfg.get("cloud_api_key", "")
        self.cfg["cloud_model"] = self.cloud_model_var.get().strip() if hasattr(self, "cloud_model_var") else self.cfg.get("cloud_model", "gpt-5-mini")
        self.cfg["cloud_max_output_tokens"] = max(120, int(self.cloud_max_tokens_var.get())) if hasattr(self, "cloud_max_tokens_var") else int(self.cfg.get("cloud_max_output_tokens", 500) or 500)
        self.cfg["overlay_enabled"] = bool(self.overlay_var.get())
        self.cfg["visualizer_enabled"] = bool(self.visualizer_var.get())
        self.cfg["always_on_top"] = bool(self.always_on_top_var.get())
        self.cfg["overlay_topmost"] = bool(self.overlay_topmost_var.get())
        self.cfg["overlay_scale"] = float(self.overlay_scale_var.get())
        self.cfg["quick_bar_topmost"] = bool(self.quick_bar_topmost_var.get())
        self.cfg["minimize_to_tray"] = bool(self.minimize_to_tray_var.get())
        self.cfg["close_to_tray"] = bool(self.close_to_tray_var.get())
        self.cfg["start_minimized"] = bool(self.start_minimized_var.get())
        self.cfg["autostart_enabled"] = bool(self.autostart_enabled_var.get())
        self.cfg["restore_last_session"] = bool(self.restore_last_session_var.get())
        self.cfg["startup_recovery_prompt"] = bool(self.startup_recovery_prompt_var.get())
        self.cfg["toast_notifications"] = bool(self.toast_notifications_var.get())
        self.cfg["system_event_toasts"] = bool(self.system_event_toasts_var.get())
        self.cfg["wake_word_enabled"] = bool(self.wake_word_enabled_var.get())
        self.cfg["wake_word"] = normalize_text(self.wake_word_var.get()) or "джарвис"
        self.cfg["reminder_alert_repeats"] = max(1, int(self.reminder_alert_repeats_var.get()))
        self.cfg["reminder_alert_interval_sec"] = max(1.0, float(self.reminder_alert_interval_var.get()))
        self.cfg["reminder_melody_mode"] = str(self.reminder_melody_mode_var.get() or "loud")
        save_config(self.cfg)
        self.footer_var.set("Настройки интерфейса сохранены")
        if self.overlay_var.get() and self.overlay_window is None:
            self.toggle_overlay(force=True)
        elif not self.overlay_var.get() and self.overlay_window is not None:
            self.toggle_overlay(force=False)

    def save_paths(self):
        for k, var in self.path_vars.items():
            self.cfg[k] = var.get().strip()
        self.cfg["auto_tts"] = bool(self.tts_var.get())
        self.cfg["auto_start_voice"] = bool(self.auto_start_voice_var.get()) if hasattr(self, "auto_start_voice_var") else bool(self.cfg.get("auto_start_voice", True))
        self.cfg["auto_start_voice_user_disabled"] = not bool(self.cfg.get("auto_start_voice", True))
        self.cfg["model_answers_enabled"] = bool(self.model_answers_enabled_var.get()) if hasattr(self, "model_answers_enabled_var") else bool(self.cfg.get("model_answers_enabled", True))
        self.cfg["model_fallback_unknown"] = bool(self.model_fallback_unknown_var.get()) if hasattr(self, "model_fallback_unknown_var") else bool(self.cfg.get("model_fallback_unknown", True))
        self.cfg["model_provider"] = self.model_provider_var.get().strip() if hasattr(self, "model_provider_var") else self.cfg.get("model_provider", "auto")
        self.cfg["ollama_base_url"] = self.ollama_base_url_var.get().strip() if hasattr(self, "ollama_base_url_var") else self.cfg.get("ollama_base_url", "http://127.0.0.1:11434")
        self.cfg["ollama_model"] = self.ollama_model_var.get().strip() if hasattr(self, "ollama_model_var") else self.cfg.get("ollama_model", "llama3.2:1b")
        self.cfg["ollama_max_output_tokens"] = max(120, int(self.ollama_max_tokens_var.get())) if hasattr(self, "ollama_max_tokens_var") else int(self.cfg.get("ollama_max_output_tokens", 500) or 500)
        self.cfg["cloud_api_key"] = self.cloud_api_key_var.get().strip() if hasattr(self, "cloud_api_key_var") else self.cfg.get("cloud_api_key", "")
        self.cfg["cloud_model"] = self.cloud_model_var.get().strip() if hasattr(self, "cloud_model_var") else self.cfg.get("cloud_model", "gpt-5-mini")
        self.cfg["cloud_max_output_tokens"] = max(120, int(self.cloud_max_tokens_var.get())) if hasattr(self, "cloud_max_tokens_var") else int(self.cfg.get("cloud_max_output_tokens", 500) or 500)
        self.cfg["overlay_enabled"] = bool(self.overlay_var.get())
        self.cfg["visualizer_enabled"] = bool(self.visualizer_var.get())
        self.cfg["always_on_top"] = bool(self.always_on_top_var.get())
        self.cfg["overlay_topmost"] = bool(self.overlay_topmost_var.get())
        self.cfg["overlay_scale"] = float(self.overlay_scale_var.get())
        self.cfg["quick_bar_topmost"] = bool(self.quick_bar_topmost_var.get())
        self.cfg["minimize_to_tray"] = bool(self.minimize_to_tray_var.get())
        self.cfg["close_to_tray"] = bool(self.close_to_tray_var.get())
        self.cfg["start_minimized"] = bool(self.start_minimized_var.get())
        self.cfg["autostart_enabled"] = bool(self.autostart_enabled_var.get())
        self.cfg["restore_last_session"] = bool(self.restore_last_session_var.get())
        self.cfg["startup_recovery_prompt"] = bool(self.startup_recovery_prompt_var.get())
        self.cfg["user_name"] = self.user_name_var.get().strip() or "Пользователь"
        self.cfg["window_opacity"] = self.clamp_opacity(self.window_opacity_var.get())
        self.cfg["overlay_opacity"] = self.clamp_opacity(self.overlay_opacity_var.get())
        self.cfg["splash_opacity"] = self.clamp_opacity(self.splash_opacity_var.get())
        self.cfg["hud_opacity"] = self.clamp_opacity(self.hud_opacity_var.get())
        self.cfg["always_on_top"] = bool(self.always_on_top_var.get())
        self.cfg["overlay_topmost"] = bool(self.overlay_topmost_var.get())
        self.cfg["overlay_scale"] = max(0.8, min(1.5, float(self.overlay_scale_var.get())))
        self.cfg["wake_word_enabled"] = bool(self.wake_word_enabled_var.get())
        self.cfg["wake_word"] = normalize_text(self.wake_word_var.get()) or "джарвис"
        self.cfg["voice_input_engine"] = self.voice_input_engine_var.get()
        self.cfg["speechkit_api_key"] = self.speechkit_api_key_var.get().strip() if hasattr(self, "speechkit_api_key_var") else self.cfg.get("speechkit_api_key", "")
        self.cfg["speechkit_folder_id"] = self.speechkit_folder_id_var.get().strip() if hasattr(self, "speechkit_folder_id_var") else self.cfg.get("speechkit_folder_id", "")
        self.cfg["speechkit_lang"] = self.speechkit_lang_var.get() if hasattr(self, "speechkit_lang_var") else self.cfg.get("speechkit_lang", "ru-RU")
        self.cfg["speechkit_topic"] = self.speechkit_topic_var.get() if hasattr(self, "speechkit_topic_var") else self.cfg.get("speechkit_topic", "general")
        self.cfg["whisper_model_size"] = self.whisper_model_var.get() if hasattr(self, "whisper_model_var") else self.cfg.get("whisper_model_size", "small")
        self.cfg["whisper_compute_type"] = self.whisper_compute_var.get() if hasattr(self, "whisper_compute_var") else self.cfg.get("whisper_compute_type", "int8")
        self.cfg["whisper_device"] = self.whisper_device_var.get() if hasattr(self, "whisper_device_var") else self.cfg.get("whisper_device", "auto")
        self.cfg["reminder_alert_repeats"] = max(1, int(self.reminder_alert_repeats_var.get()))
        self.cfg["reminder_alert_interval_sec"] = max(1.0, float(self.reminder_alert_interval_var.get()))
        self.cfg["reminder_melody_mode"] = str(self.reminder_melody_mode_var.get() or "loud")
        self.apply_all_opacity(initial=True)
        self.apply_topmost_flags()
        self.ensure_tray_state()
        self.ensure_autostart_state()
        save_config(self.cfg)
        self.footer_var.set("Настройки сохранены")
        self.post_log("[jarvis] Настройки сохранены.")
        self.post_response(f"Сохранил настройки, {self.cfg['user_name']}.")

    def pick_path(self, key):
        path = filedialog.askopenfilename(title="Выбери EXE", filetypes=[("EXE", "*.exe"), ("Все файлы", "*.*")])
        if path:
            self.path_vars[key].set(path)
            self.save_paths()

    def auto_find_all(self, silent=False):
        found = []
        for key in ["telegram_path", "discord_path", "steam_path"]:
            p = self.find_app_path(key)
            if p:
                self.cfg[key] = p
                if key in getattr(self, 'path_vars', {}):
                    self.path_vars[key].set(p)
                found.append(key)
        save_config(self.cfg)
        if found:
            self.footer_var.set(f"Автопоиск нашёл: {', '.join(k.replace('_path', '') for k in found)}")
        if found and not silent:
            self.post_log("[jarvis] Автопоиск обновил пути программ.")

    def auto_find_single(self, key):
        p = self.find_app_path(key)
        if p:
            self.path_vars[key].set(p)
            self.save_paths()
            self.post_response(f"Нашёл путь для {key.replace('_path', '')}.")
        else:
            self.post_response(f"Не нашёл путь для {key.replace('_path', '')}. Выбери EXE вручную.")

    def find_app_path(self, key):
        home = Path.home()
        appdata = Path(os.environ.get("APPDATA", home / "AppData/Roaming"))
        local = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local"))
        candidates = []
        if key == "telegram_path":
            candidates += [
                appdata / "Telegram Desktop/Telegram.exe",
                Path("C:/Program Files/Telegram Desktop/Telegram.exe"),
                Path("C:/Program Files (x86)/Telegram Desktop/Telegram.exe"),
            ]
        elif key == "discord_path":
            candidates += [
                local / "Discord/Update.exe",
                local / "Discord/app-1.0.9181/Discord.exe",
                local / "Discord/app-1.0.9179/Discord.exe",
            ]
            discord_dir = local / "Discord"
            if discord_dir.exists():
                for child in sorted(discord_dir.glob("app-*"), reverse=True):
                    candidates.append(child / "Discord.exe")
                candidates.append(discord_dir / "Update.exe")
        elif key == "steam_path":
            candidates += [
                Path("C:/Program Files (x86)/Steam/Steam.exe"),
                Path("C:/Program Files/Steam/Steam.exe"),
            ]
        for c in candidates:
            if c.exists():
                return str(c)
        return ""

    def set_status(self, text):
        self.status_var.set(f"● {text}")
        self.footer_var.set(f"Статус: {text}")
        self.listening = text in {"слушаю", "запуск голоса"}
        self.update_overlay_view()

    def get_wake_variants(self):
        return wake_variants_from_value(self.wake_word_var.get() if hasattr(self, "wake_word_var") else self.cfg.get("wake_word", "джарвис"))

    def save_wake_word_settings(self):
        value = normalize_text(self.wake_word_var.get()) or "джарвис"
        self.wake_word_var.set(value)
        self.cfg["wake_word_enabled"] = bool(self.wake_word_enabled_var.get())
        self.cfg["wake_word"] = value
        save_config(self.cfg)
        self.footer_var.set(f"Ключевая фраза: {'вкл' if self.cfg['wake_word_enabled'] else 'выкл'} • {value}")
        self.post_log(f"[voice] Ключевая фраза {'включен' if self.cfg['wake_word_enabled'] else 'выключен'}: {value}")

    def get_custom_variants(self, label):
        raw = self.cfg.get("custom_intents", {}).get(label, [])
        if isinstance(raw, str):
            raw = [x.strip() for x in raw.split(",") if x.strip()]
        if not isinstance(raw, list):
            return []
        return [str(x).strip() for x in raw if str(x).strip()]
