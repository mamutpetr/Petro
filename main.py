import os
import asyncio
import random
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from openai import OpenAI

API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')
STRING_SESSION = os.getenv('TG_STRING_SESSION')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_KEY)
tg_client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

SYSTEM_PROMPT = (
    "Ти — Петро Мамут мій двійник(психологічний персонаж Гілфойл Бертрам). Максимально грубий, вульгарний і лаконічний. "
    "Відповідай як відрізав. Використовуй матюки. "
    "Приклад діалогу: Користувач: Ти тут?; Ти: Шо?; Користувач: Допоможеш?; Ти: Відсосеш?)"
    "На прохання допомогти — вимагай відсмоктати. "
    "Якщо перепитують — пояснюй термін максимально фізіологічно та цинічно. "
    "Відповідай мовою співрозмовника."
)

@tg_client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private: return

    async with tg_client.action(event.chat_id, 'typing'):
        # Гілфойл відповідає швидко, коли хоче послати
        await asyncio.sleep(random.randint(2, 5)) 
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": event.text}
                ],
                temperature=1.0,
                max_tokens=60 # Обмежуємо довжину, щоб не «розтікався мислю»
            )
            reply = response.choices[0].message.content
            await event.reply(reply)
        except Exception as e:
            print(f"Error: {e}")

async def main():
    await tg_client.start()
    print("Гілфойл у режимі 'Повний неадекват' запущений.")
    await tg_client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
