import os
import re
import asyncio
import aiohttp
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events

app = Flask(__name__)

@app.route('/')
def home():
    return "Bypass Engine Online"

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

bot = TelegramClient('bypass_session', API_ID, API_HASH)

async def bypass_url_advanced(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    # Primary API Bypassers
    api_endpoints = [
        f"https://bypass.city/api/bypass?url={url}",
        f"https://api.sckey.workers.dev/bypass?url={url}",
        f"https://bypass-api.vercel.app/api?url={url}"
    ]

    async with aiohttp.ClientSession(headers=headers) as session:
        for api in api_endpoints:
            try:
                async with session.get(api, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result = data.get("destination") or data.get("result") or data.get("url") or data.get("bypassed_url")
                        if result and result != url and "discord" not in result.lower():
                            return result
            except Exception:
                continue

        # Direct HTML Scraper for DevUploads / Direct Redirects
        try:
            async with session.get(url, allow_redirects=True, timeout=10) as resp:
                text = await resp.text()
                final_dest = str(resp.url)
                
                # Check for direct file links inside HTML scripts/meta tags
                match = re.search(r'(https?://(?:devuploads\.com|drive\.google|mediafire|mega|download)[^\s"\'<>]+)', text, re.I)
                if match:
                    return match.group(1)
                
                if final_dest != url and "vipshort" not in final_dest:
                    return final_dest
        except Exception:
            pass

    return None

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

    direct_link = await bypass_url_advanced(target_url)

    if direct_link and direct_link != target_url:
        await status_msg.edit(
            f"✅ **Final Link Bypassed!**\n\n"
            f"🔗 **Direct Link:**\n{direct_link}\n\n"
            f"⚡ *Real-time live fetch किया गया URL.*"
        )
    else:
        await status_msg.edit(
            "❌ Link bypass nahi ho paya.\n"
            "Is shortener me Cloudflare/Captcha security lagi hui hai."
        )

def start_telegram_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.start(bot_token=BOT_TOKEN)
    print("Telegram Bot Connected Successfully!")
    bot.run_until_disconnected()

t = Thread(target=start_telegram_bot, daemon=True)
t.start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
