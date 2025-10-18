import json
import os
from datetime import datetime, timedelta
import asyncio
import pytz
from telethon.sync import TelegramClient
from telethon.tl.types import Message

# НАСТРОЙКИ
API_ID = "API_ID"  # реальный API ID
API_HASH = 'API_HASH'  # реальный API Hash
SESSION_NAME = 'telegram_analyzer'

# Юзернейм или ID чата, который нужно анализировать
CHAT_USERNAME = '@public_chat'  # Например: '@public_chat' или ID номер для приватной супергруппы

# Часовой пояс для отчета
TIMEZONE = 'Asia/Tashkent'

# Количество дней для анализа
DAYS_TO_ANALYZE = 7

async def main():
  print("🚀 Запускаем анализ...")

  # Подключаемся к Telegram
  async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
      try:
          target_chat = await client.get_entity(CHAT_USERNAME)
          print(f"✅ Успешно подключились к чату: '{target_chat.title}'")
      except Exception as e:
          print(f"❌ Не удалось найти чат '{CHAT_USERNAME}'. Проверь юзернейм или ID. Ошибка: {e}")
          return

      # Словарь для хранения информации о тредах
      threads = {}
      root_message_ids = set()

      # Определяем дату, с которой начинаем анализ
      utc_tz = pytz.utc
      start_date = datetime.now(utc_tz) - timedelta(days=DAYS_TO_ANALYZE)
      print(f"⏳ Анализирую сообщения за последние {DAYS_TO_ANALYZE} дней. Это может занять некоторое время...")

      # Итерируемся по сообщениям в чате
      async for message in client.iter_messages(target_chat, offset_date=datetime.now(utc_tz), reverse=True):
          # Останавливаемся, если сообщение слишком старое
          if message.date < start_date:
              break

          # Нас интересуют только ответы на другие сообщения (или сообщения в топиках)
          if not message.is_reply and not message.is_topic_message:
              continue

          # Определяем ID треда
          thread_id = None
          if message.is_topic_message:
              thread_id = message.reply_to.topic_id
          elif message.is_reply:
              thread_id = message.reply_to_msg_id

          if not thread_id:
              continue

          # Инициализируем тред, если видим его впервые
          if thread_id not in threads:
              threads[thread_id] = {
                  "message_count": 0,
                  "users": set(),
                  "root_message_id": thread_id
              }
          root_message_ids.add(thread_id)

          # Обновляем счетчики
          threads[thread_id]["message_count"] += 1
          if message.sender_id:
              threads[thread_id]["users"].add(message.sender_id)

      print(f"📊 Найдено {len(threads)} уникальных обсуждений. Получаю детали...")

      # Получаем тексты и даты корневых сообщений
      root_messages = await client.get_messages(target_chat, ids=list(root_message_ids))
      root_messages_map = {msg.id: msg for msg in root_messages if msg}
      processed_threads = []

      for thread_id, data in threads.items():
          root_message = root_messages_map.get(thread_id)
          if not root_message:
              continue

          # Определяем "тему" обсуждения
          topic_title = "Без темы"
          if root_message.is_topic_message:
              topic_action = root_message.action
              if topic_action and hasattr(topic_action, 'title'):
                  topic_title = topic_action.title
          elif root_message.text:
              topic_title = (root_message.text[:70] + '...') if len(root_message.text) > 70 else root_message.text

          processed_threads.append({
              "date": root_message.date,
              "topic": topic_title.replace('\n', ' '),
              "messages": data["message_count"],
              "users": len(data["users"])
          })

      # Сортируем обсуждения по количеству сообщений
      processed_threads.sort(key=lambda x: x["messages"], reverse=True)
      print("📑 Формирую JSON-отчет...")

      # Группировка по дням
      days_report = {}
      target_tz = pytz.timezone(TIMEZONE)
      for thread in processed_threads:
          local_date_str = thread["date"].astimezone(target_tz).strftime('%Y-%m-%d')
          if local_date_str not in days_report:
              days_report[local_date_str] = []
          days_report[local_date_str].append({
              "topic": thread["topic"],
              "messages": thread["messages"],
              "users": thread["users"]
          })

      # Собираем финальный JSON
      final_report = {
          "timezone": TIMEZONE,
          "days": []
      }
      for date_str in sorted(days_report.keys()):
          final_report["days"].append({
              "date": date_str,
              "threads": days_report[date_str]
          })

      # Сохраняем в файл
      output_filename = 'report.json'
      with open(output_filename, 'w', encoding='utf-8') as f:
          json.dump(final_report, f, ensure_ascii=False, indent=2)
      print(f"✅ Готово! Отчет сохранен в файл '{output_filename}'")

if __name__ == "__main__":
  # В Windows может потребоваться эта строка для корректной работы asyncio
  if os.name == 'nt':
      asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
  asyncio.run(main())