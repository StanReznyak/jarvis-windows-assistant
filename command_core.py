from __future__ import annotations

import difflib
import re

SUPPORTED_INTENTS = [
    ("voice_off", "Без голоса"),
    ("voice_on", "Включить голос"),
    ("interrupt_speech", "Прервать речь"),
    ("test_voice", "Тест голоса"),
    ("overlay_on", "Показать overlay"),
    ("overlay_off", "Скрыть overlay"),
    ("notes_show", "Показать заметки"),
    ("notes_export", "Экспорт заметок"),
    ("time_now", "Сколько времени"),
    ("date_today", "Какая дата"),
    ("open_twitch", "Открыть Twitch"),
    ("open_youtube", "Открыть YouTube"),
    ("open_telegram", "Открыть Telegram"),
    ("open_discord", "Открыть Discord"),
    ("open_steam", "Открыть Steam"),
    ("scenario_work", "Сценарий: рабочий режим"),
    ("scenario_game", "Сценарий: игровой режим"),
    ("scenario_silent", "Сценарий: тихий режим"),
    ("reminders_show", "Показать напоминания"),
    ("open_downloads", "Открыть загрузки"),
    ("open_documents", "Открыть документы"),
    ("open_desktop", "Открыть рабочий стол"),
    ("open_taskmgr", "Открыть диспетчер задач"),
    ("open_control_panel", "Открыть панель управления"),
    ("show_desktop", "Свернуть все окна"),
]

INTENT_DEFAULTS = {
    "voice_off": ["без голоса", "выключи голос", "молча", "тихий режим", "режим без звука"],
    "voice_on": ["включи голос", "верни голос", "говори", "озвучка включена"],
    "interrupt_speech": ["замолчи", "стоп речь", "перестань говорить", "стоп", "тихо"],
    "test_voice": ["тест голоса", "проверь голос", "проверка голоса", "проверить голос"],
    "overlay_on": ["включи оверлей", "покажи оверлей", "overlay", "покажи overlay"],
    "overlay_off": ["скрой оверлей", "убери оверлей", "спрячь overlay"],
    "notes_show": ["покажи заметки", "покажи память", "заметки", "память"],
    "notes_export": ["экспорт заметок", "сохрани заметки"],
    "time_now": ["сколько времени", "который час", "время"],
    "date_today": ["какая дата", "какое сегодня число", "сегодняшняя дата", "дата"],
    "open_twitch": ["открой твич", "открою твич", "запусти твич", "твич", "твитч", "твичь", "твиттер", "twitch", "twitch tv"],
    "open_youtube": ["открой ютуб", "открою ютуб", "зайди на ютуб", "ютуб", "ютюб", "ю туб", "youtube", "you tube"],
    "open_telegram": ["открой телеграм", "открою телеграм", "запусти телеграм", "телеграм", "телеграмм", "телегу", "телега", "telegram"],
    "open_discord": ["открой дискорд", "открою дискорд", "запусти дискорд", "дискорд", "дискор", "дис корд", "дисс корд", "дис корт", "дисс корт", "де скотт", "де скот", "discord"],
    "open_steam": ["открой стим", "открою стим", "открой steam", "запусти стим", "стим", "steam", "с тим", "в тим", "тим", "стиб", "стип", "стив"],
    "scenario_work": ["рабочий режим", "режим работа", "режим работы", "подготовь работу", "запусти рабочий режим"],
    "scenario_game": ["игровой режим", "режим игра", "режим игры", "запусти игровой режим", "подготовь игру"],
    "scenario_silent": ["тихий режим", "режим тишина", "ночной режим", "режим молчания", "запусти тихий режим"],
    "reminders_show": ["покажи напоминания", "покажи напоминалки", "напоминания", "мои напоминания"],
    "open_downloads": ["открой загрузки", "покажи загрузки", "загрузки"],
    "open_documents": ["открой документы", "покажи документы", "документы"],
    "open_desktop": ["открой рабочий стол", "покажи рабочий стол", "рабочий стол"],
    "open_taskmgr": ["открой диспетчер задач", "диспетчер задач", "task manager"],
    "open_control_panel": ["открой панель управления", "панель управления", "control panel"],
    "show_desktop": ["сверни все окна", "покажи рабочий стол", "свернуть все окна"],
}

BRAND_ALIASES = {
    "telegram": ["телеграм", "телеграмм", "телега", "телегу", "telegram", "телеграма"],
    "discord": ["дискорд", "дис корд", "дисс корд", "дис корт", "дисс корт", "дискор", "дескорд", "де скот", "де скотт", "discord"],
    "steam": ["стим", "steam", "с тим", "в тим", "стеам", "стеим", "стиб", "стип", "стив"],
    "twitch": ["твич", "твитч", "твичь", "твиттер", "twitch", "twitch tv"],
    "youtube": ["ютуб", "ютюб", "ю туб", "юту", "youtube", "you tube"],
}

ACTION_ALIASES = {
    "open": ["открой", "открою", "запусти", "включи", "зайди", "открыть", "запустить", "откро"],
    "show": ["покажи", "открой", "выведи"],
}

MEMORY_STOPWORDS = {
    "голос", "озвучка", "озвучку", "звук", "дата", "время", "ютуб", "телеграм", "дискорд",
    "стим", "память", "профиль", "ник", "имя", "город", "запомни", "меня", "зовут",
    "мой", "мое", "моё", "обо", "мне", "у", "голоса"
}

COMMAND_HELP_LINES = [
    "Вот что я умею:",
    "• открывать программы, сайты и папки: Telegram, Discord, Steam, YouTube, загрузки, документы",
    "• говорить время и дату",
    "• включать и выключать голос, оверлей и HUD",
    "• запускать рабочий, игровой и тихий режим",
    "• работать с заметками и напоминаниями",
    "• отвечать через локальную модель, если настроена Ollama",
    "• отвечать через облачный провайдер, если добавлен API-ключ",
    "• искать в интернете и открывать сайт по названию",
    "• показать этот список команд",
    "Это только примеры возможностей, а не сохранённые напоминания.",
]

def build_command_help_text() -> str:
    return "\n".join(COMMAND_HELP_LINES)


def normalize_text(text: str) -> str:
    text = text.lower().replace("ё", "е")
    text = re.sub(r"[^a-zа-я0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compact_text(text: str) -> str:
    return normalize_text(text).replace(" ", "")


def cleanup_memory_value(value: str) -> str:
    value = normalize_text(value)
    value = re.sub(r"^(это|что|будет)\s+", "", value).strip()
    value = re.sub(r"\b(пожалуйста|плиз)\b", "", value).strip()
    value = re.sub(r"\s+", " ", value).strip(" .,!?:;")
    return value


def looks_like_bad_memory_value(value: str) -> bool:
    v = cleanup_memory_value(value)
    if not v:
        return True
    if v in MEMORY_STOPWORDS:
        return True
    words = v.split()
    if len(words) <= 2 and all(w in MEMORY_STOPWORDS for w in words):
        return True
    bad_pairs = {"у голоса", "мой голос", "ник голос", "голос голос"}
    if v in bad_pairs:
        return True
    return False


def extract_after_prefix(text: str, prefixes):
    norm = normalize_text(text)
    for prefix in prefixes:
        p = normalize_text(prefix)
        if norm.startswith(p + " "):
            return cleanup_memory_value(norm[len(p):].strip())
        if norm == p:
            return ""
    return None


def fuzzy_normalize(text: str) -> str:
    text = compact_text(text)
    replacements = [
        ("дисскорт", "дискорд"), ("дискорт", "дискорд"), ("дисскорд", "дискорд"), ("дисскор", "дискорд"),
        ("дискорд", "дискорд"), ("дискор", "дискорд"), ("дисскорд", "дискорд"),
        ("дескорд", "дискорд"), ("дескорт", "дискорд"), ("дескотт", "дискорд"), ("дескот", "дискорд"),
        ("дескотд", "дискорд"), ("дескортд", "дискорд"), ("дискод", "дискорд"),
        ("телеграмм", "телеграм"), ("телеграм", "телеграм"), ("телега", "телеграм"), ("телегу", "телеграм"),
        ("твичь", "твич"), ("твитч", "твич"), ("твиттер", "твич"), ("twitchtv", "twitch"),
        ("ютюб", "ютуб"), ("ютюбе", "ютуб"), ("юту", "ютуб"), ("ютубчик", "ютуб"), ("youtub", "youtube"),
        ("стимм", "стим"), ("стеам", "steam"), ("стеамм", "steam"), ("стеим", "steam"), ("стим", "steam"), ("стиб", "steam"), ("стип", "steam"), ("стив", "steam"), ("открою", "открой"), ("откро", "открой"),
    ]
    for src, dst in replacements:
        text = text.replace(src, dst)
    return text


def wake_variants_from_value(value: str | None):
    value = normalize_text(value or "джарвис")
    variants = [value] if value else ["джарвис"]
    base_map = {
        "джарвис": ["джарвис", "джавис", "жарвис", "jarvis"],
        "жарвис": ["джарвис", "джавис", "жарвис", "jarvis"],
        "джавис": ["джарвис", "джавис", "жарвис", "jarvis"],
        "jarvis": ["jarvis", "джарвис", "джавис", "жарвис"],
    }
    aliases = base_map.get(value, [value])
    return list(dict.fromkeys([normalize_text(v) for v in (variants + aliases) if normalize_text(v)]))


def strip_wake_words(text: str, wake_variants):
    result = normalize_text(text)
    for wake in wake_variants:
        if wake:
            result = re.sub(rf"\b{re.escape(wake)}\b", " ", result).strip()
    return normalize_text(result)


def has_wake_word(text: str, wake_variants):
    norm = normalize_text(text)
    if not norm:
        return False
    padded = f" {norm} "
    for wake in wake_variants:
        w = normalize_text(wake)
        if not w:
            continue
        if norm == w or norm.startswith(w + " ") or f" {w} " in padded:
            return True
    return False


def extract_wake_tail(text: str, wake_variants):
    norm = normalize_text(text)
    if not norm:
        return False, "", ""
    for wake in wake_variants:
        w = normalize_text(wake)
        if not w:
            continue
        if norm == w:
            return True, "", w
        if norm.startswith(w + " "):
            return True, normalize_text(norm[len(w):].strip()), w
        token = f" {w} "
        padded = f" {norm} "
        idx = padded.find(token)
        if idx != -1:
            after = padded[idx + len(token):].strip()
            if after:
                return True, normalize_text(after), w
            before = padded[:idx].strip()
            return True, normalize_text(before), w
    return False, "", ""


def is_free_text_command(text: str) -> bool:
    norm = normalize_text(text)
    compact = compact_text(norm)
    triggers = [
        "запомни", "менязовут", "моеимя", "моёимя", "мойник", "ник", "мойгород", "город",
        "обомне", "напомни", "напоминай", "заметка", "добавьзадачу", "факт", "профиль",
        "спроси", "объясни", "обьясни", "расскажи", "установиоламу", "подготовьлокальныйрежим"
    ]
    return any(t in compact for t in triggers) or any(norm.startswith(p) for p in [
        "запомни ", "мой ник ", "ник ", "мой город ", "город ", "напомни ", "напоминай ", "запиши заметку ", "добавь задачу ",
        "спроси ", "объясни ", "обьясни ", "расскажи ",
        "ответь ", "объясни ", "обьясни ", "расскажи ", "что такое ", "почему ", "как сделать ", "можно ли ", "подготовь локальный режим", "установи оламу"
    ])


def phrase_similarity(a: str, b: str) -> float:
    aa = fuzzy_normalize(a)
    bb = fuzzy_normalize(b)
    if not aa or not bb:
        return 0.0
    if aa == bb:
        return 1.0
    score = difflib.SequenceMatcher(None, aa, bb).ratio()
    if aa in bb or bb in aa:
        score = max(score, min(len(aa), len(bb)) / max(len(aa), len(bb)) + 0.12)
    return min(score, 1.0)
