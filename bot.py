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
        self.wfile.write(b"Live Auto-Refresh Bypass Bot Active!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

bot = TelegramClient(None, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Real-time bypass function without caching
async def bypass_url_live(url):
    # Headers to bypass server-side caching & force fresh fetch
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache'
    }

    # Public Real-Time Bypass Endpoints
    api_list = [
        f"https://api.sckey.workers.dev/bypass?url={url}&nocache=true",
        f"https://bypass.id/api/v1/bypass?url={url}&refresh=true"
    ]
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for api_endpoint in api_list:
            try:
                async with session.get(api_endpoint, timeout=12) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        res = data.get("destination") or data.get("result") or data.get("bypassed_url") or data.get("url")
                        if res and "discord" not in res.lower() and "shut down" not in res.lower():
                            return res
            except Exception:
                continue

    # Direct Unwrapper / Redirect Fetch (Bypasses old cached headers)
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, allow_redirects=True, timeout=10) as resp:
                final_url = str(resp.url)
                if final_url != url and "discord" not in final_url:
                    return final_url
    except Exception:
        pass

    return None

@bot.on(events.NewMessage(incoming=True))
async def handle_message(event):
    if not event.is_private:
        return

    text = event.message.text or ""
    
    if text.startswith('/start'):
        await event.reply("👋 Hello! Mujhe koi bhi shortener link bhejien. Main Real-Time live bypassing karunga taaki agar file replace hui ho toh aapko hamesha LATEST file hi mile.")
        return

    urls = re.findall(r'https?://[^\s]+', text)
    if not urls:
        await event.reply("⚠️ Kripya ek valid Link bhejein.")
        return

    status_msg = await event.reply("🔄 Live link fetch ho raha hai (Fetching latest file)...")
    target_url = urls[0]

    # Dynamic Live Fetch
    direct_link = await bypass_url_live(target_url)

    if direct_link:
        await status_msg.edit(
            f"✅ **Latest Link Bypassed!**\n\n"
            f"🔗 **Direct Download Link:**\n{direct_link}\n\n"
            f"⚡ *Note: Ye live fetch kiya gaya hai, isme purani corrupted file ka cache nahi hai.*"
        )
    else:
        await status_msg.edit(
            "❌ Ye link bypass nahi ho paya ya server response nahi de raha."
        )

print("Live Bypass Bot Online...")
bot.run_until_disconnected()
