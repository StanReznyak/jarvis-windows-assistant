from .main_window_shared import *


class VoicePanelMixin:
    def resolve_hybrid_voice_text(self, command_text: str, free_text: str) -> str:
        command_text = normalize_text(command_text or "")
        free_text = normalize_text(free_text or "")
        if command_text:
            self.post_log(f"[hybrid-cmd] {command_text}")
        if free_text and free_text != command_text:
            self.post_log(f"[hybrid-free] {free_text}")

        if not command_text:
            return free_text
        if not free_text:
            return command_text

        wake_variants = self.get_wake_variants()
        if bool(self.cfg.get("wake_word_enabled", False)):
            cmd_has_wake = has_wake_word(command_text, wake_variants)
            free_has_wake = has_wake_word(free_text, wake_variants)
            if not cmd_has_wake and not free_has_wake:
                self.post_log(f"[wake] пропуск без wake word: {free_text or command_text}")
                return ""
            if cmd_has_wake and not free_has_wake:
                free_text = ""
            elif free_has_wake and not cmd_has_wake:
                command_text = ""
        cmd_core = strip_wake_words(command_text, wake_variants)
        free_core = strip_wake_words(free_text, wake_variants)

        if is_free_text_command(cmd_core) or is_free_text_command(free_core):
            chosen = free_text if len(compact_text(free_core)) >= len(compact_text(cmd_core)) else command_text
            self.post_log(f"[hybrid] free-text mode → {chosen}")
            return chosen

        if has_wake_word(free_text, wake_variants) and len(compact_text(free_text)) > len(compact_text(command_text)) + 2:
            self.post_log(f"[hybrid] chose free recognizer → {free_text}")
            return free_text

        self.post_log(f"[hybrid] chose command recognizer → {command_text}")
        return command_text


    def on_voice_text(self, text: str):
        self.root.after(0, lambda: self._handle_voice_text(text))


    def _handle_voice_text(self, text: str):
        self.heard_var.set(text)
        self.overlay_heard_var.set(text)
        self.bump_visualizer(0.8)
        self.post_log(f"[voice] {text}")
        self.set_status("распознаю")
        self.set_voice_pipeline_status(f"heard → {text[:64]}")
        self.handle_command(text, source="voice")


    def send_entry(self, source="chat"):
        widget = self.entry if source == "chat" else self.dashboard_entry
        text = widget.get().strip()
        if not text:
            return
        widget.delete(0, "end")
        self.heard_var.set(text)
        self.overlay_heard_var.set(text)
        self.post_log(f"[text] {text}")
        self.handle_command(text, source="text")


    def start_voice(self):
        if self.voice_worker and self.voice_worker.is_alive():
            self.post_response("Голос уже запущен.")
            return
        self.voice_worker = VoiceWorker(self)
        self.voice_worker.start()
        current_stt = str(self.cfg.get("voice_input_engine", self.voice_input_engine_var.get() if hasattr(self, "voice_input_engine_var") else "auto")).upper()
        self.voice_mode_var.set(f"{current_stt} STT • АКТИВЕН")
        self.set_status("запуск голоса")
        self.last_action_var.set("Голосовой режим запущен")
        self.set_voice_pipeline_status(f"listening via {current_stt.lower()}")
        self.bump_visualizer(1.0)


    def stop_voice(self):
        if self.voice_worker:
            self.voice_worker.stop()
            self.voice_worker = None
        current_stt = str(self.cfg.get("voice_input_engine", self.voice_input_engine_var.get() if hasattr(self, "voice_input_engine_var") else "auto")).upper()
        self.voice_mode_var.set(f"{current_stt} STT • ОСТАНОВЛЕН")
        self.set_status("ожидание")
        self.last_action_var.set("Голосовой режим остановлен")
        self.set_voice_pipeline_status("stopped")
        self.post_response("Остановил голосовой режим.")


    def set_tts_enabled(self, enabled: bool, announce=True):
        self.tts_var.set(bool(enabled))
        self.tts_state_var.set("Голос включён" if self.tts_var.get() else "Без голоса")
        self.save_ui_config()
        self.post_log(f"[jarvis] Озвучка {'включена' if self.tts_var.get() else 'выключена'}.")
        self.footer_var.set(self.tts_state_var.get())
        if announce:
            if self.tts_var.get():
                self.post_response("Озвучка включена.")
            else:
                self.response_var.set("Озвучка выключена. Команды будут выполняться молча.")
                self.post_log("[jarvis] Озвучка выключена. Команды будут выполняться молча.")


    def toggle_tts_enabled(self):
        self.set_tts_enabled(not bool(self.tts_var.get()))


    def test_voice(self):
        if not self.tts_var.get():
            self.post_log("[tts] Тест пропущен: включён режим без голоса")
            self.response_var.set("Сейчас включён режим без голоса.")
            self.footer_var.set("Без голоса")
            return
        mode = self.tts_engine_var.get()
        self.post_log(f"[tts] Ручной тест голоса запущен | режим={mode}")
        self.post_log(f"[stt] input-engine={self.voice_input_engine_var.get() if hasattr(self, 'voice_input_engine_var') else self.cfg.get('voice_input_engine', 'auto')}")
        self.post_log(f"[stt] speechkit-lang={self.cfg.get('speechkit_lang', 'ru-RU')} topic={self.cfg.get('speechkit_topic', 'general')} configured={bool(self.cfg.get('speechkit_api_key')) and bool(self.cfg.get('speechkit_folder_id'))}")
        self.post_log(f"[stt] whisper-model={self.cfg.get('whisper_model_size', 'small')} compute={self.cfg.get('whisper_compute_type', 'int8')} device={self.cfg.get('whisper_device', 'auto')}")
        self.post_log(f"[stt] whisper.cpp cli={self.cfg.get('whisper_cpp_cli_path', '') or str(find_whisper_cpp_cli() or '')} model={self.cfg.get('whisper_cpp_model_path', '') or str(find_whisper_cpp_model() or '')} lang={self.cfg.get('whisper_cpp_language', 'ru')} threads={self.cfg.get('whisper_cpp_threads', 4)}")
        self.set_voice_pipeline_status(f"tts test • {mode}")
        self.post_response(f"Тест голоса. Режим {mode}.")


    def stop_speaking(self):
        self.tts.stop()
        self.footer_var.set("Речь прервана")
        self.post_log("[jarvis] Озвучка прервана вручную.")
        self.last_action_var.set("Озвучка прервана")


    def test_stt_setup(self):
        engine = str(self.voice_input_engine_var.get() if hasattr(self, "voice_input_engine_var") else self.cfg.get("voice_input_engine", "auto"))
        cli = str(self.whisper_cpp_cli_var.get() if hasattr(self, "whisper_cpp_cli_var") else self.cfg.get("whisper_cpp_cli_path", "")).strip()
        model = str(self.whisper_cpp_model_var.get() if hasattr(self, "whisper_cpp_model_var") else self.cfg.get("whisper_cpp_model_path", "")).strip()
        giga_model_name = str(self.gigaam_model_name_var.get() if hasattr(self, "gigaam_model_name_var") else self.cfg.get("gigaam_model_name", "istupakov/gigaam-v3-onnx")).strip()
        giga_model_path = str(self.gigaam_model_path_var.get() if hasattr(self, "gigaam_model_path_var") else self.cfg.get("gigaam_model_path", "")).strip()
        cli_exists = Path(cli).exists() if cli else False
        model_exists = Path(model).exists() if model else False
        giga_local_exists = Path(giga_model_path).exists() if giga_model_path else False
        giga_target = giga_model_path or giga_model_name or "-"
        giga_state = "ok" if giga_local_exists else ("hf" if not giga_model_path else "missing")
        summary = f"STT={engine} • gigaam={giga_target} • giga-local={giga_state} • wcpp-cli={'ok' if cli_exists else 'missing'} • wcpp-model={'ok' if model_exists else 'missing'}"
        self.set_voice_pipeline_status(summary)
        self.post_log(f"[stt-check] engine={engine} gigaam={giga_target} giga_local_exists={giga_local_exists} cli={cli or '-'} exists={cli_exists} model={model or '-'} exists={model_exists}")
        self.post_response(f"Проверка STT: {summary}.")


    def show_voice_command_cheatsheet(self):
        tips = (
            "Быстрые голосовые команды:\n\n"
            "• джарвис открой телеграм\n"
            "• джарвис открой дискорд\n"
            "• джарвис открой ютуб\n"
            "• джарвис какая дата\n"
            "• джарвис напомни через 10 минут выключить плиту\n"
            "• джарвис напомни завтра в 11 купить хлеб\n"
            "• джарвис покажи напоминания\n"
            "• джарвис удали последнее напоминание"
        )
        try:
            messagebox.showinfo("Подсказка по голосовым командам", tips)
        except Exception:
            self.post_log("[voice-help] Не удалось открыть окно cheatsheet")
        self.post_log("[voice-help] shown")


    def set_voice_pipeline_status(self, text: str):
        self.voice_pipeline_var.set(f"Голосовой модуль: {text}")
        self.post_log(f"[voice-state] {text}")


