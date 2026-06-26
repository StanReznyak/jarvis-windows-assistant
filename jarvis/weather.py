from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
import urllib.error
from typing import Any

WEATHER_CODE_RU = {
    0: "ясно",
    1: "в основном ясно",
    2: "переменная облачность",
    3: "пасмурно",
    45: "туман",
    48: "изморозь и туман",
    51: "слабая морось",
    53: "морось",
    55: "сильная морось",
    56: "ледяная морось",
    57: "сильная ледяная морось",
    61: "слабый дождь",
    63: "дождь",
    65: "сильный дождь",
    66: "ледяной дождь",
    67: "сильный ледяной дождь",
    71: "слабый снег",
    73: "снег",
    75: "сильный снег",
    77: "снежные зёрна",
    80: "слабый ливень",
    81: "ливень",
    82: "сильный ливень",
    85: "слабый снегопад",
    86: "сильный снегопад",
    95: "гроза",
    96: "гроза с градом",
    99: "сильная гроза с градом",
}

CITY_ALIASES = {
    "рыбинске": "рыбинск",
    "рыбинск": "рыбинск",
    "ярославле": "ярославль",
    "ярославль": "ярославль",
    "москве": "москва",
    "москва": "москва",
    "питере": "санкт-петербург",
    "санкт петербурге": "санкт-петербург",
    "санкт-петербурге": "санкт-петербург",
    "спб": "санкт-петербург",
}

WEATHER_WORDS = ("погода", "погоду", "погоде", "погодой", "градусов", "температура", "дождь", "снег", "ветер")


def _norm(value: Any) -> str:
    return str(value or "").strip()


def _clean_city(value: str) -> str:
    city = _norm(value).lower().replace("ё", "е")
    city = re.sub(r"[^a-zа-я0-9\-\s]", " ", city, flags=re.I)
    city = re.sub(r"\s+", " ", city).strip(" -")
    stop_tail = (
        "сейчас", "сегодня", "завтра", "на сегодня", "на завтра", "пожалуйста", "джарвис",
        "какая", "какой", "скажи", "покажи", "узнай", "что", "там", "с", "погодой",
    )
    words = [w for w in city.split() if w not in stop_tail]
    city = " ".join(words).strip(" -")
    city = CITY_ALIASES.get(city, city)
    if city.endswith("ске") and len(city) > 5:
        city = city[:-1]  # рыбинске -> рыбинск
    return city


def looks_like_weather_request(text: str) -> bool:
    low = _norm(text).lower().replace("ё", "е")
    return any(word in low for word in WEATHER_WORDS)


def extract_weather_city(text: str, config: dict[str, Any] | None = None, memory: dict[str, Any] | None = None) -> str:
    low = _norm(text).lower().replace("ё", "е")
    low = re.sub(r"\s+", " ", low).strip()

    patterns = [
        r"(?:какая\s+)?погода\s+в\s+(.+)$",
        r"погоду\s+в\s+(.+)$",
        r"температура\s+в\s+(.+)$",
        r"сколько\s+градусов\s+в\s+(.+)$",
        r"что\s+с\s+погодой\s+в\s+(.+)$",
        r"дождь\s+в\s+(.+)$",
        r"снег\s+в\s+(.+)$",
        r"ветер\s+в\s+(.+)$",
    ]
    for pat in patterns:
        match = re.search(pat, low)
        if match:
            city = _clean_city(match.group(1))
            if city:
                return city

    # Example: "погода рыбинск"
    after = re.sub(r"^(скажи|покажи|узнай|джарвис)\s+", "", low).strip()
    after = re.sub(r"^(какая\s+)?погода\s*", "", after).strip()
    if after and after != low:
        city = _clean_city(after)
        if city:
            return city

    # Try saved profile city.
    for source in (config or {}, (memory or {}).get("profile", {}) or {}, memory or {}):
        for key in ("city", "home_city"):
            city = _clean_city(source.get(key, "") if isinstance(source, dict) else "")
            if city:
                return city
    return ""


def _http_json(url: str, timeout: float = 12.0) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "JARVIS/8 Weather"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)


def _geocode_city(city: str) -> dict[str, Any] | None:
    candidates = [city]
    alias = CITY_ALIASES.get(city)
    if alias and alias not in candidates:
        candidates.append(alias)
    if city.endswith("ске") and len(city) > 5:
        candidates.append(city[:-1])
    if city.endswith("е") and len(city) > 5:
        candidates.append(city[:-1])

    seen: set[str] = set()
    for candidate in candidates:
        candidate = candidate.strip()
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode({
            "name": candidate,
            "count": 1,
            "language": "ru",
            "format": "json",
        })
        data = _http_json(url, timeout=12)
        results = data.get("results") or []
        if results:
            return results[0]
    return None


def get_weather_answer(text: str, config: dict[str, Any] | None = None, memory: dict[str, Any] | None = None) -> str:
    city = extract_weather_city(text, config=config, memory=memory)
    if not city:
        return "Скажи город. Например: Джарвис, какая погода в Рыбинске."

    try:
        place = _geocode_city(city)
        if not place:
            return f"Не нашёл город {city}. Скажи город точнее."
        lat = place.get("latitude")
        lon = place.get("longitude")
        name = place.get("name") or city.title()
        admin = place.get("admin1") or ""
        country = place.get("country") or ""
        location = ", ".join([x for x in [name, admin, country] if x])
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,precipitation,rain,snowfall,weather_code,wind_speed_10m",
            "timezone": "auto",
        }
        url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
        data = _http_json(url, timeout=14)
        current = data.get("current") or {}
        units = data.get("current_units") or {}
        temp = current.get("temperature_2m")
        feels = current.get("apparent_temperature")
        wind = current.get("wind_speed_10m")
        code = current.get("weather_code")
        precipitation = current.get("precipitation")
        weather_text = WEATHER_CODE_RU.get(int(code), "погода обновлена") if code is not None else "погода обновлена"
        temp_unit = units.get("temperature_2m", "°C")
        wind_unit = units.get("wind_speed_10m", "км/ч")
        parts = [f"В {location} сейчас {temp}{temp_unit}, ощущается как {feels}{temp_unit}, {weather_text}."]
        if precipitation is not None:
            parts.append(f"Осадки: {precipitation} мм.")
        if wind is not None:
            parts.append(f"Ветер: {wind} {wind_unit}.")
        return " ".join(parts)
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        return "Не смог получить погоду: нет интернета или погодный сервис недоступен. Локальная модель не знает текущую погоду."
    except Exception as exc:
        return f"Не смог получить погоду: {str(exc)[:160]}"
