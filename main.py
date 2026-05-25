import os
import time
import asyncio
import requests
from telethon import TelegramClient, events

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

client = TelegramClient("session", API_ID, API_HASH)


def get_ai_reply(user_message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Tu ek real insaan ki tarah reply karta hai. "
                    "Replies casual Hinglish mein hone chahiye — thoda Hindi, thoda English, "
                    "jaise dost baat karta hai. Chhoti aur natural replies de. "
                    "Kabhi mat batana ki tu AI hai. "
                    "Emojis occasionally use kar sakte ho but overdo mat karo."
                ),
            },
            {"role": "user", "content": user_message},
        ],
        "max_tokens": 150,
    }
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"AI error: {e}")
        return None


@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return

    if event.out:
        return

    sender = await event.get_sender()
    if sender is None or sender.bot:
        return

    message_text = event.raw_text.strip()
    if not message_text:
        return

    print(f"Message from {sender.first_name}: {message_text}")

    reply = await asyncio.to_thread(get_ai_reply, message_text)

    if reply:
        await asyncio.sleep(3)
        await event.reply(reply)
        print(f"Replied: {reply}")


async def main():
    print("Starting Telegram AI auto-reply...")
    await client.start()
    print("Logged in successfully. Listening for messages...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
