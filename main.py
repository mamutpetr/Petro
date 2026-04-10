import os
import asyncio
import random
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from openai import OpenAI

# Налаштування
API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')
STRING_SESSION = os.getenv('TG_STRING_SESSION')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_KEY)
tg_client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# Оновлений промпт: акцент на ультра-стислості (1-5 слів)
SYSTEM_PROMPT = (
    "Ти — цифровий двійник юзера. Стиль: ультра-цинічний, максимально грубий, прямий. "
    "Пиши максимально коротко (1-5 слів), без розділових знаків, використовуй різкий сленг. "
    "На будь-які прохання про допомогу відповідай зневагою: це марна трата твоїх ресурсів. "
    "Якщо перепитують — посилай максимально коротко. Навколо одні дегенерати, твій час — це мільярди. Жодної етики."
)

@tg_client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private: return

    try:
        chat_entity = await event.get_input_chat()

        async with tg_client.action(chat_entity, 'typing'):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": event.text if event.text else ""}
                ],
                temperature=1.3,
                max_tokens=15,  # Жорстке обмеження для довжини 1-5 слів
                presence_penalty=0.8
            )
            
            reply = response.choices[0].message.content.strip().replace('.', '').replace(',', '')
            
            if reply:
                await event.reply(reply)

    except Exception as e:
        print(f"Error: {e}")

async def main():
    await tg_client.start()
    await tg_client.get_dialogs()
    print("Двійник-мізантроп запущений. Режим максимальної стислості.")
    await tg_client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOff.")
