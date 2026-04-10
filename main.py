import os
import asyncio
import random
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from openai import OpenAI

# Налаштування (беруться з оточення)
API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')
STRING_SESSION = os.getenv('TG_STRING_SESSION')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

# Ініціалізація клієнтів
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
    # Працюємо тільки в приватних повідомленнях
    if not event.is_private: 
        return

    try:
        # Отримуємо сутність чату (input entity), щоб уникнути ValueError
        chat_entity = await event.get_input_chat()

        # Показуємо статус "друкує"
        async with tg_client.action(chat_entity, 'typing'):
            # Затримка для ефекту присутності
            await asyncio.sleep(random.randint(2, 5)) 

            # Запит до OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": event.text}
                ],
                temperature=1.0,
                max_tokens=60
            )
            
            reply = response.choices[0].message.content
            
            # Відповідаємо на повідомлення
            await event.reply(reply)

    except Exception as e:
        print(f"Error in handler: {e}")

async def main():
    # Авторизація
    await tg_client.start()
    
    # Важливо: завантажуємо діалоги, щоб Telethon закешував "entities"
    # Це допомагає уникнути помилок "Could not find input entity"
    await tg_client.get_dialogs()
    
    print("Гілфойл (Петро Мамут) у режимі 'Повний неадекват' запущений.")
    
    # Тримаємо клієнт запущеним
    await tg_client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Вимкнення...")
