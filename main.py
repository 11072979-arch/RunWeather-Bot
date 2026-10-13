"""RunWeather Bot: sends a daily running-weather report to Telegram."""
import logging
import os
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from weather_logic import make_recommendation

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
LATITUDE = float(os.getenv("LATITUDE", "48.5079"))
LONGITUDE = float(os.getenv("LONGITUDE", "32.2623"))
LOCATION_NAME = os.getenv("LOCATION_NAME", "Кропивницький").strip()
TIMEZONE = os.getenv("TIMEZONE", "Europe/Kyiv").strip()
CHAT_IDS = [x.strip() for x in os.getenv("TELEGRAM_CHAT_IDS", "").split(",") if x.strip()]

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}" if TOKEN else ""
HTTP = requests.Session()


def get_weather():
    """Fetch current conditions from Open-Meteo."""
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": (
            "temperature_2m,apparent_temperature,precipitation,rain,showers,"
            "snowfall,wind_speed_10m,wind_gusts_10m,weather_code"
        ),
        "timezone": TIMEZONE,
        "forecast_days": 1,
    }
    response = HTTP.get(OPEN_METEO_URL, params=params, timeout=20)
    response.raise_for_status()
    payload = response.json()
    current = payload.get("current")
    if not isinstance(current, dict):
        raise ValueError("Open-Meteo не повернув погодні дані у полі current.")
    required = ("temperature_2m", "wind_speed_10m", "precipitation")
    missing = [key for key in required if key not in current]
    if missing:
        raise ValueError(f"У відповіді Open-Meteo відсутні поля: {', '.join(missing)}")
    return {
        "temperature": float(current["temperature_2m"]),
        "feels_like": float(current.get("apparent_temperature", current["temperature_2m"])),
        "wind": float(current["wind_speed_10m"]),
        "gusts": float(current.get("wind_gusts_10m", current["wind_speed_10m"])),
        "precipitation": float(current.get("precipitation", 0) or 0),
        "rain": float(current.get("rain", 0) or 0),
        "showers": float(current.get("showers", 0) or 0),
        "snowfall": float(current.get("snowfall", 0) or 0),
        "code": int(current.get("weather_code", 0) or 0),
        "time": str(current.get("time", "невідомо")),
    }


def build_message():
    weather = get_weather()
    verdict, clothing = make_recommendation(weather)
    return (
        f"🏃 RunWeather Bot — {LOCATION_NAME}\n"
        f"🕖 Час даних: {weather['time']}\n\n"
        f"🌡 Температура: {weather['temperature']:.1f}°C "
        f"(відчувається як {weather['feels_like']:.1f}°C)\n"
        f"💨 Вітер: {weather['wind']:.1f} км/год "
        f"(пориви до {weather['gusts']:.1f} км/год)\n"
        f"🌧 Опади: {weather['precipitation']:.1f} мм\n\n"
        f"Вердикт: {verdict}\n"
        f"Рекомендація щодо одягу: {clothing}\n\n"
        "Порада орієнтовна. Перевіряйте офіційні погодні попередження та власне самопочуття."
    )


def send_telegram(chat_id, message):
    if not TELEGRAM_API:
        raise RuntimeError("Не задано TELEGRAM_BOT_TOKEN у файлі .env.")
    response = HTTP.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": message},
        timeout=20,
    )
    response.raise_for_status()
    result = response.json()
    if not result.get("ok"):
        raise RuntimeError(f"Telegram API повернув помилку: {result.get('description', 'невідома помилка')}")


def daily_job():
    try:
        message = build_message()
    except Exception:
        logging.exception("Не вдалося отримати погоду або сформувати повідомлення.")
        return

    if not CHAT_IDS:
        logging.warning("TELEGRAM_CHAT_IDS не налаштовано: прогноз сформовано, але не надіслано.")
        logging.info("Текст прогнозу:\n%s", message)
        return

    for chat_id in CHAT_IDS:
        try:
            send_telegram(chat_id, message)
            logging.info("Повідомлення надіслано для chat_id=%s.", chat_id)
        except Exception:
            # Avoid logging request URLs containing the bot token.
            logging.exception("Не вдалося надіслати повідомлення для chat_id=%s.", chat_id)


def main():
    if not TOKEN:
        raise SystemExit("Не задано TELEGRAM_BOT_TOKEN. Скопіюйте .env.example у .env і заповніть токен.")
    try:
        timezone = ZoneInfo(TIMEZONE)
    except ZoneInfoNotFoundError as exc:
        raise SystemExit(f"Невідомий часовий пояс {TIMEZONE!r}. Перевірте TIMEZONE у .env.") from exc

    scheduler = BlockingScheduler(timezone=timezone)
    scheduler.add_job(daily_job, "cron", hour=7, minute=0, id="daily_weather",
                      max_instances=1, coalesce=True)
    logging.info("RunWeather Bot запущено. Щоденний запуск о 07:00 (%s).", TIMEZONE)
    # Send a test report immediately after startup. Remove this line for scheduled-only operation.
    daily_job()
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("RunWeather Bot зупинено.")


if __name__ == "__main__":
    main()
