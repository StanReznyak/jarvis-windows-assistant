from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

MODEL_SYSTEM_PROMPT = """
Ты голосовой помощник JARVIS на Windows-компьютере пользователя.
Отвечай по-русски, коротко, по делу и живо, потому что ответ будет озвучиваться голосом.
Не используй длинные списки без необходимости. Не выдумывай, если не уверен.
Ты не управляешь компьютером напрямую: открытие программ, сайтов и системные действия выполняет локальный код JARVIS.
Если пользователь просит опасное действие, вредоносный код, взлом, скрытое наблюдение или обход защиты — откажи коротко и предложи безопасный вариант.
""".strip()

MODEL_TRIGGER_PREFIXES = (
    "спроси ",
    "спроси модель ",
    "ответь ",
    "объясни ",
    "обьясни ",
    "расскажи ",
    "подумай ",
)

MODEL_QUESTION_STARTS = (
    "что такое ",
    "кто такой ",
    "кто такая ",
    "кто это ",
    "почему ",
    "зачем ",
    "как сделать ",
    "как мне ",
    "как лучше ",
    "можно ли ",
    "что будет если ",
    "в чем разница ",
    "в чём разница ",
)


def _norm(value: Any) -> str:
    return str(value or "").strip()


def get_cloud_api_key(config: dict[str, Any]) -> str:
    return _norm(os.environ.get("JARVIS_CLOUD_API_KEY")) or _norm(config.get("cloud_api_key"))


def get_model_provider(config: dict[str, Any]) -> str:
    provider = _norm(os.environ.get("JARVIS_MODEL_PROVIDER") or config.get("model_provider") or "auto").lower()
    if provider not in {"local", "cloud", "auto"}:
        provider = "auto"
    return provider


def strip_model_prefix(text: str) -> str:
    raw = _norm(text)
    low = raw.lower().replace("ё", "е")
    for prefix in sorted(MODEL_TRIGGER_PREFIXES, key=len, reverse=True):
        p = prefix.lower().replace("ё", "е")
        if low.startswith(p):
            return raw[len(prefix):].strip()
    return raw


def looks_like_model_request(text: str, allow_questions: bool = True) -> bool:
    raw = _norm(text)
    if not raw:
        return False
    low = raw.lower().replace("ё", "е")
    if any(low.startswith(prefix.lower().replace("ё", "е")) for prefix in sorted(MODEL_TRIGGER_PREFIXES, key=len, reverse=True)):
        return True
    if allow_questions and any(low.startswith(prefix.lower().replace("ё", "е")) for prefix in MODEL_QUESTION_STARTS):
        return True
    return False


def _extract_text_from_response(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return str(text).strip()
    chunks: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            ctext = getattr(content, "text", None)
            if ctext:
                chunks.append(str(ctext))
    return "\n".join(chunks).strip()


def _build_messages(text: str, history: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
    user_text = strip_model_prefix(text) or text
    messages: list[dict[str, str]] = [
        {"role": "system", "content": MODEL_SYSTEM_PROMPT},
    ]
    for msg in (history or [])[-8:]:
        role = msg.get("role", "user")
        content = _norm(msg.get("content"))
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_text})
    return messages


def _ask_cloud_provider(text: str, config: dict[str, Any], history: list[dict[str, str]] | None = None) -> str:
    api_key = get_cloud_api_key(config)
    if not api_key:
        return "MODEL_OFF: ключ облачного режима не указан. Локальные команды работают. Для облачного режима добавьте API-ключ, для локального режима запустите SETUP_LOCAL_MODEL_WINDOWS.bat."

    try:
        from openai import OpenAI
    except Exception as exc:
        return f"MODEL_OFF: пакет для облачного провайдера не установлен. Для локального режима он не нужен. Деталь: {exc}"

    model = _norm(config.get("cloud_model")) or "gpt-5-mini"
    max_tokens = int(config.get("cloud_max_output_tokens", 500) or 500)
    max_tokens = max(120, min(max_tokens, 1800))

    try:
        client = OpenAI(api_key=api_key, timeout=35.0)
        response = client.responses.create(
            model=model,
            input=_build_messages(text, history),
            max_output_tokens=max_tokens,
        )
        answer = _extract_text_from_response(response)
        if not answer:
            return "MODEL_ERROR: облачный провайдер вернул пустой ответ. Попробуйте ещё раз."
        return answer.strip()
    except Exception as exc:
        message = str(exc).replace(api_key, "***")
        return f"MODEL_ERROR: не смог получить ответ облачного провайдера: {message[:260]}"


def ask_ollama(text: str, config: dict[str, Any], history: list[dict[str, str]] | None = None) -> str:
    """Local Ollama mode running on 127.0.0.1:11434."""
    base_url = _norm(config.get("ollama_base_url")) or "http://127.0.0.1:11434"
    model = _norm(config.get("ollama_model")) or "llama3.2:1b"
    max_tokens = int(config.get("ollama_max_output_tokens", config.get("cloud_max_output_tokens", 500)) or 500)
    max_tokens = max(120, min(max_tokens, 1800))
    timeout = float(config.get("ollama_timeout_sec", 60) or 60)

    payload = {
        "model": model,
        "messages": _build_messages(text, history),
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.4,
        },
    }
    endpoint = base_url.rstrip("/") + "/api/chat"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        result = json.loads(raw)
        message = result.get("message") or {}
        answer = _norm(message.get("content"))
        if not answer:
            return "MODEL_ERROR: Ollama вернула пустой ответ. Проверьте модель и попробуйте ещё раз."
        return answer
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:260]
        if "not found" in detail.lower() or exc.code == 404:
            return f"MODEL_OFF: модель Ollama '{model}' не найдена. Локальные команды работают. Запустите SETUP_LOCAL_MODEL_WINDOWS.bat или в PowerShell: ollama pull {model}"
        return f"MODEL_ERROR: ошибка Ollama HTTP {exc.code}: {detail}"
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        return "MODEL_OFF: локальный режим ещё не подготовлен. Локальные команды работают. Запустите SETUP_LOCAL_MODEL_WINDOWS.bat — он проверит Ollama и загрузит llama3.2:1b."
    except Exception as exc:
        return f"MODEL_ERROR: ошибка локального режима Ollama: {str(exc)[:260]}"


def ask_model(text: str, config: dict[str, Any], history: list[dict[str, str]] | None = None) -> str:
    """Route a free-form request to the selected local or cloud model provider."""
    provider = get_model_provider(config)
    if provider == "cloud":
        return _ask_cloud_provider(text, config, history)
    if provider == "auto":
        if get_cloud_api_key(config):
            cloud = _ask_cloud_provider(text, config, history)
            if not cloud.startswith("MODEL_OFF:"):
                return cloud
        return ask_ollama(text, config, history)
    return ask_ollama(text, config, history)
