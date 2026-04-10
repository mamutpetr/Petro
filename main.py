import os
import asyncio
import random
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from openai import OpenAI

# Дані з Render Environment Variables
API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')
STRING_SESSION = os.getenv('TG_STRING_SESSION')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_KEY)
tg_client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

SYSTEM_PROMPT = (
    "Ти — Бертрам Гілфойл. Ти системний архітектор, сатаніст і геній. "
    "Ти відповідаєш замість Петра. Спілкуйся токсично, з сарказмом і матюками. "
    "Ти зневажаєш тупість і низькі бюджети. Відповідай коротко."
)

@tg_client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return

    async with tg_client.action(event.chat_id, 'typing'):
        await asyncio.sleep(random.randint(5, 12))
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": event.text}
                ],
                temperature=0.9
            )
            reply = response.choices[0].message.content
            if random.random() > 0.7:
                reply = random.choice(["Блять, ", "Сука, ", "Слухай сюди... "]) + reply
            await event.reply(reply)
        except Exception as e:
            print(f"Error: {e}")

# Виправлений блок запуску для Python 3.12+
async def main():
    await tg_client.start()
    print("Гілфойл підключений і готовий принижувати людей...")
    await tg_client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
