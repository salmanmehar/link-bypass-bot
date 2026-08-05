import os
import re
import asyncio
import aiohttp
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events

# Minimal Flask App for Render Keep-Alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bypass Bot Server Running Live!"

# Environment Variables
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Initialize Telethon Client
bot = TelegramClient('bypass_session', API_ID, API_HASH)

async def resolve_final_url(url, depth=0):
    if depth > 5:
        return url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'Cache-Control': 'no-cache, no-store, must-revalidate'
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, allow_redirects=True, timeout=12) as resp:
                text = await resp.text()
                final_dest = str(resp.url)

                found_links = re.findall(r'https?://(?:devuploads\.com|download|drive\.google|mega|mediafire|apk)[^\s"\'<>]+', text, re.IGNORECASE)
                if found_links:
                    return found_links[0]

                if final_dest != url and not any(x in final_dest for x in ['sarkarijob', 'health', 'blog', 'news']):
                    return final_dest
    except Exception:
        pass

    return url

async def bypass_url_deep(url):
    api_list = [
        f"https://api.sckey.workers.dev/bypass?url={url}&nocache=true",
        f"https://bypass.id/api/v1/bypass?url={url}"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    async with aiohttp.ClientSession(headers=headers) as session:
        for api in api_list:
            try:
                async with session.get(api, timeout=12) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        res = data.get("destination") or data.get("result") or data.get("url")
                        if res and "discord" not in res.lower() and "shut down" not in res.lower():
                            return await resolve_final_url(res)
            except Exception:
                continue

    return await resolve_final_url(url)

@bot.on(events.NewMessage(incoming=True))
async def handle_message(event):
    if not event.is_private:
        return

    text = event.message.text or ""
    if text.startswith('/start'):
        await event.reply("👋 Hello! Shortener link bhejien, main real-time bypass karke direct link dunga.")
        return

    urls = re.findall(r'https?://[^\s]+', text)
    if not urls:
        await event.reply("⚠️ Kripya ek valid Link bhejein.")
        return

    status_msg = await event.reply("🔍 Link bypass ho raha hai, thoda wait karein...")
    target_url = urls[0]

    direct_link = await bypass_url_deep(target_url)

    if direct_link:
        await status_msg.edit(
            f"✅ **Final Link Bypassed!**\n\n"
            f"🔗 **Direct Link:**\n{direct_link}\n\n"
            f"⚡ *Real-time live fetch किया गया URL.*"
        )
    else:
        await status_msg.edit("❌ Link bypass nahi ho paya.")

def start_telegram_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.start(bot_token=BOT_TOKEN)
    print("Telegram Bot Connected Successfully!")
    bot.run_until_disconnected()

# Background Thread for Telegram Client
t = Thread(target=start_telegram_bot, daemon=True)
t.start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
