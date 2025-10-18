# Telegram Thread Analyzer

## Описание
Скрипт для анализа активности тредов в Telegram-чате за указанный период. Позволяет:
- Собирать статистику по обсуждениям
- Группировать треды по дням
- Формировать JSON-отчет с детальной информацией

## Зависимости
- Python 3.8+
- telethon
- pytz

## Установка
1. Клонируйте репозиторий
2. Установите зависимости:
```bash
pip install telethon pytz
```

## Настройка
1. Получите `API_ID` и `API_HASH` в [Telegram Developer Portal](https://my.telegram.org/apps)
2. Отредактируйте настройки в скрипте:
 - `API_ID`: Ваш Telegram API ID
 - `API_HASH`: Ваш Telegram API Hash
 - `CHAT_USERNAME`: Юзернейм или ID чата
 - `TIMEZONE`: Часовой пояс для отчета
 - `DAYS_TO_ANALYZE`: Количество дней для анализа

## Запуск
```bash
python telegram_analyzer.py
```

## Выходные данные
- `report.json`: Отчет с группировкой по дням
- Структура: 
- `timezone`: Часовой пояс
- `days`: Массив дней с тредами

## Примечания
- При первом запуске потребуется авторизация в Telegram
- Скрипт работает асинхронно для эффективности

## Лицензия
MIT by Denis Kulakov