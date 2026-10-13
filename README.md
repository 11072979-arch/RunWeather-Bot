# RunWeather Bot 🏃

RunWeather Bot — асистент для бігунів і спортсменів. Щоранку о **07:00 за київським часом** застосунок отримує актуальні погодні дані для обраної локації, оцінює орієнтовний комфорт пробіжки та надсилає в Telegram рекомендацію щодо одягу.

## Архітектура

![Архітектурна схема RunWeather Bot](docs/architecture.svg)

### Потік даних
1. `APScheduler` запускає завдання щодня о 07:00 (`Europe/Kyiv`).
2. Python-бекенд надсилає HTTPS GET-запит до Open-Meteo.
3. Бекенд аналізує температуру, вітер, пориви та опади й формує рекомендацію.
4. Звіт надсилається користувачам через Telegram Bot API (`sendMessage`, HTTPS POST).
5. Налаштування зберігаються в локальному `.env`; погодні дані обробляються в пам’яті. База даних не потрібна для MVP.

## Технології та API
- Python 3.11+
- Requests — HTTP-запити
- python-dotenv — змінні оточення
- APScheduler — розклад запуску
- pytest — автоматичні тести
- [Open-Meteo Forecast API](https://open-meteo.com/en/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## Встановлення

### Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## Налаштування Telegram
1. Відкрийте [@BotFather](https://t.me/BotFather) у Telegram.
2. Надішліть `/newbot`, виконайте інструкції та скопіюйте токен.
3. Відкрийте створеного бота й натисніть **Start** або надішліть `/start`.
4. Дізнайтеся свій `chat_id`. Після повідомлення боту його можна отримати через Telegram Bot API `getUpdates`. Не публікуйте токен або URL із токеном.
5. Заповніть локальний `.env`:

```dotenv
TELEGRAM_BOT_TOKEN=ваш_справжній_токен
TELEGRAM_CHAT_IDS=ваш_chat_id
LATITUDE=48.5079
LONGITUDE=32.2623
LOCATION_NAME=Кропивницький
TIMEZONE=Europe/Kyiv
```

Для кількох користувачів укажіть ID через кому.

## Запуск
```bash
python src/main.py
```

Після старту бот один раз надсилає тестовий звіт, а потім планує повідомлення на 07:00 щодня. Комп’ютер або сервер має залишатися увімкненим, а процес — працювати. Щоб не надсилати звіт одразу після запуску, закоментуйте `daily_job()` перед `scheduler.start()` у `src/main.py`.

## Тести
```bash
pytest -q
```
Тести перевіряють правила рекомендацій, але не реальну доставку повідомлень чи доступність зовнішніх API.

## Безпека
- `.env` виключений із Git; публікуйте лише `.env.example` без секретів.
- Якщо токен опубліковано, відкличте його через BotFather і створіть новий.
- Не додавайте токен у README, issue чи публічні логи.

## Наступні етапи
- [ ] Додати команди `/start` і `/settings`, збереження підписників та вибір міста.
- [ ] Дозволити користувачам вибирати час повідомлення.
- [ ] Розширити тести та обробку помилок API.
- [ ] Розгорнути сервіс на VPS або хмарному сервері.

## Обмеження
Рекомендації орієнтовні й не замінюють офіційні попередження про небезпечну погоду. Враховуйте якість повітря, самопочуття та індивідуальну переносимість холоду й спеки.
