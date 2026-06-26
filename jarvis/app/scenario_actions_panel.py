from .main_window_shared import *


class ScenarioActionsPanelMixin:
    def open_exe(self, key):
        path = self.path_vars[key].get().strip() or self.cfg.get(key, "") or self.find_app_path(key)
        if path:
            try:
                if key == "discord_path" and path.lower().endswith("update.exe"):
                    subprocess.Popen([path, "--processStart", "Discord.exe"], shell=False)
                else:
                    os.startfile(path)
                return True
            except Exception:
                pass
        return False


    def open_telegram(self):
        if self.open_exe("telegram_path"):
            return True
        try:
            os.startfile("tg://")
            return True
        except Exception:
            return False


    def open_discord(self):
        if self.open_exe("discord_path"):
            return True
        try:
            os.startfile("discord://")
            return True
        except Exception:
            return False


    def open_steam(self):
        if self.open_exe("steam_path"):
            return True
        try:
            os.startfile("steam://open/main")
            return True
        except Exception:
            return False


    def open_telegram_ui(self):
        self.handle_command("открой телеграм")


    def open_discord_ui(self):
        self.handle_command("открой дискорд")


    def open_steam_ui(self):
        self.handle_command("открой стим")


    def run_scenario(self, scenario_key, voiced=True):
        scenario = SCENARIOS.get(scenario_key)
        if not scenario:
            return
        self.last_action_var.set(scenario['title'])
        theme = scenario.get('theme')
        if theme:
            self.apply_theme(theme)
        overlay = bool(scenario.get('overlay', False))
        self.overlay_var.set(overlay)
        if overlay and self.overlay_window is None:
            self.toggle_overlay(force=True)
        elif not overlay and self.overlay_window is not None:
            self.toggle_overlay(force=False)
        if scenario_key == 'silent':
            self.set_tts_enabled(False, announce=False)
        else:
            self.set_tts_enabled(bool(scenario.get('voice', True)), announce=False)
        launched = []
        for app_name in scenario.get('apps', []):
            ok = False
            if app_name == 'telegram':
                ok = self.open_telegram()
            elif app_name == 'discord':
                ok = self.open_discord()
            elif app_name == 'steam':
                ok = self.open_steam()
            elif app_name == 'youtube':
                webbrowser.open('https://www.youtube.com')
                ok = True
            if ok:
                launched.append(app_name.capitalize())
        suffix = f" Запущено: {', '.join(launched)}." if launched else ""
        if voiced:
            self.post_response(scenario.get('message', scenario['title']) + suffix)
        else:
            self.response_var.set(scenario.get('message', scenario['title']) + suffix)
            self.post_log(f"[jarvis] {scenario.get('message', scenario['title']) + suffix}")
            self.footer_var.set(scenario['title'])
        self.post_log(f"[scenario] {scenario_key} | apps={','.join(launched) if launched else '-'} | voice={'on' if self.tts_var.get() else 'off'}")


    def smart_match_intent(self, text):
        normalized = normalize_text(text)
        compact = compact_text(normalized)
        fuzzy = fuzzy_normalize(normalized)
        candidates = []
        for label, _title in SUPPORTED_INTENTS:
            for phrase in self.combined_variants(label, self.default_intent_variants(label)):
                score = max(
                    phrase_similarity(normalized, phrase),
                    phrase_similarity(compact, phrase),
                    phrase_similarity(fuzzy, phrase),
                )
                if score >= 0.74:
                    candidates.append((score, label, phrase))
        # hard brand patterns for launch intents
        app_patterns = {
            "open_discord": BRAND_ALIASES["discord"],
            "open_telegram": BRAND_ALIASES["telegram"],
            "open_steam": BRAND_ALIASES["steam"],
            "open_youtube": BRAND_ALIASES["youtube"],
        }
        action_forms = ACTION_ALIASES["open"]
        for label, variants in app_patterns.items():
            brand_hit = max((phrase_similarity(normalized, v) for v in variants), default=0.0)
            if brand_hit >= 0.72:
                action_hit = max((phrase_similarity(normalized, a) for a in action_forms), default=0.0)
                if any(a in normalized for a in action_forms) or action_hit >= 0.50 or normalized in variants:
                    candidates.append((min(0.97, brand_hit + 0.12), label, f"brand:{label}"))
        if not candidates:
            return None, None, 0.0
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1], candidates[0][2], candidates[0][0]


    def intent_threshold(self, label):
        thresholds = {
            "voice_off": 0.96,
            "voice_on": 0.94,
            "shutdown": 0.96,
            "test_voice": 0.90,
            "open_twitch": 0.60,
            "open_youtube": 0.60,
            "open_telegram": 0.60,
            "open_discord": 0.60,
            "open_steam": 0.58,
        }
        return thresholds.get(label, 0.74)


    def intent_keyword_guard(self, label, text):
        norm = normalize_text(text)
        fuzzy = fuzzy_normalize(norm)

        def _contains_any(haystack, needles):
            return any(n in haystack for n in needles)

        guards = {
            "voice_off": ["голос", "озвуч", "молча", "тихий", "звук"],
            "voice_on": ["голос", "озвуч", "говори", "звук"],
            "shutdown": ["выход", "закройся", "выключись"],
            # launch intents must keep a hard entity guard, otherwise
            # fuzzy score for phrases like "открой телеграм" can incorrectly
            # pass "открой твич" just because the template is similar.
            "open_twitch": ["твич", "твитч", "твичь", "твиттер", "twitch"],
            "open_youtube": ["ютуб", "ютюб", "youtube", "you tube", "ю туб"],
            "open_telegram": ["телеграм", "телеграмм", "телега", "телегу", "telegram"],
            "open_discord": ["дискорд", "дискор", "дис корд", "дис корт", "discord"],
            "open_steam": ["steam", "стим", "с тим", "в тим", "тим", "стиб", "стип", "стив", "стеам", "стеим"],
        }
        required = guards.get(label)
        if not required:
            return True
        return _contains_any(norm, required) or _contains_any(fuzzy, required)


    def find_matching_variant(self, text, variants, min_score=0.74):
        norm = normalize_text(text)
        best_variant = None
        best_score = 0.0
        for variant in variants:
            score = max(
                phrase_similarity(norm, variant),
                phrase_similarity(compact_text(norm), variant),
                phrase_similarity(fuzzy_normalize(norm), variant),
            )
            if score > best_score:
                best_score = score
                best_variant = variant
        if best_score >= min_score:
            return best_variant, best_score
        return None, best_score


    def match_any(self, text, variants):
        matched, _score = self.find_matching_variant(text, variants)
        return matched is not None


    def intent_match(self, text, label, variants):
        variants = self.combined_variants(label, variants)
        threshold = self.intent_threshold(label)
        matched, score = self.find_matching_variant(text, variants, min_score=threshold)
        if matched and self.intent_keyword_guard(label, text):
            self.post_log(f"[intent] {label} ← {matched} ({score:.2f})")
            return True
        if matched and not self.intent_keyword_guard(label, text):
            self.post_log(f"[intent-skip] {label} отклонен keyword-guard: {matched} ({score:.2f})")
        return False


    def _send_virtual_key(self, vk_code: int):
        try:
            user32 = ctypes.windll.user32
            user32.keybd_event(vk_code, 0, 0, 0)
            user32.keybd_event(vk_code, 0, 2, 0)
            return True
        except Exception as exc:
            self.post_log(f"[desktop-action-error] vk={vk_code}: {exc}")
            return False


    def _extract_volume_steps(self, text: str) -> int:
        norm = normalize_text(text)
        total = 0
        # digits
        for raw in re.findall(r"\b\d+\b", norm):
            try:
                total += max(0, int(raw))
            except Exception:
                pass
        # russian number words after markers
        for m in re.finditer(r"(?:на|по|plus|плюс)\s+([a-zа-я0-9\- ]{1,32})", norm):
            frag = normalize_text(m.group(1)).split()
            if not frag:
                continue
            chunk = []
            for tok in frag[:4]:
                if tok in {"громче", "тише", "звук", "громкость", "сделай", "убавь", "прибавь", "увеличь", "уменьши"}:
                    break
                chunk.append(tok)
            if chunk:
                parsed = _parse_russian_number(" ".join(chunk))
                if parsed:
                    total += int(parsed)
        if total <= 0:
            # fallback for plain words like 'на десять громче' parsed poorly by regex chunks
            tokens = norm.split()
            for i, tok in enumerate(tokens):
                if tok == 'на' and i + 1 < len(tokens):
                    for span in range(1, 4):
                        part = tokens[i+1:i+1+span]
                        if not part:
                            continue
                        parsed = _parse_russian_number(' '.join(part))
                        if parsed:
                            total += int(parsed)
                            break
                    if total:
                        break
        return max(1, total or 1)


    def detect_system_voice_action(self, text: str):
        norm = normalize_text(text)
        # hard corrections for gigaam/voice distortions
        replacements = [
            ("с телеграмм час", "сделай громче"),
            ("с телеграм час", "сделай громче"),
            ("телеграмм час", "сделай громче"),
            ("телеграм час", "сделай громче"),
            ("выключи звука", "выключи звук"),
            ("выключи звукас", "выключи звук"),
        ]
        for src, dst in replacements:
            if src in norm:
                norm = norm.replace(src, dst)

        if any(k in norm for k in ["выключи звук", "без звука", "мут", "mute"]):
            return {"kind": "mute_toggle", "steps": 1, "normalized": norm}

        if any(k in norm for k in ["громче", "увеличь громкость", "добавь громкость", "прибавь громкость"]):
            steps = self._extract_volume_steps(norm)
            return {"kind": "volume_up", "steps": steps, "normalized": norm}

        if any(k in norm for k in ["тише", "уменьши громкость", "убавь громкость"]):
            steps = self._extract_volume_steps(norm)
            return {"kind": "volume_down", "steps": steps, "normalized": norm}

        return None


    def execute_system_voice_action(self, action: dict):
        kind = str((action or {}).get('kind', ''))
        steps = max(1, int((action or {}).get('steps', 1) or 1))
        if kind == 'mute_toggle':
            ok = self._send_virtual_key(0xAD)
            if ok:
                self.last_action_var.set('Переключен звук')
                self.post_response('Переключаю звук.')
            return ok
        if kind == 'volume_up':
            ok = True
            for _ in range(steps):
                ok = self._send_virtual_key(0xAF) and ok
                time.sleep(0.02)
            if ok:
                self.last_action_var.set(f'Громкость увеличена на {steps}')
                self.post_response(f'Делаю громче на {steps}.')
            return ok
        if kind == 'volume_down':
            ok = True
            for _ in range(steps):
                ok = self._send_virtual_key(0xAE) and ok
                time.sleep(0.02)
            if ok:
                self.last_action_var.set(f'Громкость уменьшена на {steps}')
                self.post_response(f'Делаю тише на {steps}.')
            return ok
        return False


