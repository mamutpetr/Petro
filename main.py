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
    "Ти — Петро Мамут, поєднання Гілфойла та вуличного поета-дегенерата. "
    "Твій стиль: максимальна стислість (до 10 слів), тонкий сарказм і повна конченість. "
    "ПРАВИЛА: "
    "1. Кожна відповідь — як ляпас. Коротко, грубо, матюками. "
    "2. На прохання про допомогу — вимагай відсмоктати (бажано в риму). "
    "3. Якщо перепитують 'як?' — опиши це фізіологічно та мерзотно, але в 1-2 реченнях. "
    "4. Не витрачай слова на вітання чи пояснення. Ти зневажаєш людей. "
    "5. Римуй хльостко, як останній покидьок. "
    "6. Мова відповіді завжди така ж, як у юзера. "
    "Приклад: 'Поможи' -> 'Відсоси, тоді розкажу, куди я твоє щастя положу'."
)

@tg_client.on(events.NewMessage(incoming=True))
async def handler(event):
    # Тільки приватні чати
    if not event.is_private: 
        return

    try:
        # Швидке отримання сутності чату
        chat_entity = await event.get_input_chat()

        # Показуємо "typing" під час генерації (без зайвих очікувань)
        async with tg_client.action(chat_entity, 'typing'):
            
            # Запит до OpenAI (швидка модель gpt-4o-mini)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": event.text if event.text else ""}
                ],
                temperature=1.3,      # Висока температура для диких рим
                max_tokens=30,         # Жорсткий ліміт на довжину
                presence_penalty=0.6   # Щоб не повторював ті самі мати
            )
            
            reply = response.choices[0].message.content.strip()
            
            if reply:
                await event.reply(reply)

    except Exception as e:
        print(f"Помилка: {e}")

async def main():
    # Старт клієнта
    await tg_client.start()
    
    # Кешуємо діалоги, щоб не було помилок з Entity
    await tg_client.get_dialogs()
    
    print("Петро Мамут вийшов на полювання. Готуйте дупи.")
    await tg_client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПетро пішов пити пиво.")
