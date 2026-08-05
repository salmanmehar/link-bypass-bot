import os
import re
import asyncio
import aiohttp
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events

# Web server for Render keep-alive
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Shortener Bypass Bot Active!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

bot = TelegramClient(None, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Free Bypass API Function
async def bypass_url(url):
    api_url = f"https://api.bypass.vip/bypass?url={url}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=20) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("status") == "success" or "destination" in data:
                        return data.get("destination") or data.get("result")
    except Exception:
        pass
    return None

@bot.on(events.NewMessage(incoming=True))
async def handle_message(event):
    if not event.is_private:
        return

    text = event.message.text or ""
    
    if text.startswith('/start'):
        await event.reply("👋 Hello! Mujhe koi bhi shortener link (DevUploads, Droplink, etc.) bhejien, main uske ads bypass karke direct link de dunga.")
        return

    # Extract URL from text
    urls = re.findall(r'https?://[^\s]+', text)
    if not urls:
        await event.reply("⚠️ Kripya ek valid Link bhejein.")
        return

    status_msg = await event.reply("⏳ Ads bypass ho rahe hain, wait karein...")
    target_url = urls[0]

    direct_link = await bypass_url(target_url)

    if direct_link:
        await status_msg.edit(
            f"✅ **Link Bypassed Successfully!**\n\n"
            f"🔗 **Direct Link:**\n{direct_link}"
        )
    else:
        await status_msg.edit(
            "❌ Ye link bypass nahi ho paya. "
            "Ho sakta hai site ne captcha lagaya ho ya link unsupported ho."
        )

print("Bypass Bot Online...")
bot.run_until_disconnected()
