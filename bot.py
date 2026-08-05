import os
import re
import asyncio
import aiohttp
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Multi-Layer Bypass Bot Active!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

bot = TelegramClient(None, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Multi-layer recursive unwrapper
async def resolve_final_url(url, depth=0):
    if depth > 5:
        return url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'Cache-Control': 'no-cache'
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, allow_redirects=True, timeout=12) as resp:
                text = await resp.text()
                final_dest = str(resp.url)

                # Look for embedded target URLs inside ad scripts/HTML (DevUploads, Drive, APK, etc.)
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
                        if res and "discord" not in res.lower():
                            # Deep resolve intermediate ad links
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
        await event.reply("👋 Hello! Shortener links bhejien, main ads layers bypass karke final link nikalunga.")
        return

    urls = re.findall(r'https?://[^\s]+', text)
    if not urls:
        await event.reply("⚠️ Kripya valid Link bhejein.")
        return

    status_msg = await event.reply("🔍 Ads & Intermediate layers bypass ho rahi hain...")
    target_url = urls[0]

    direct_link = await bypass_url_deep(target_url)

    if direct_link:
        await status_msg.edit(
            f"✅ **Final File Link Extracted!**\n\n"
            f"🔗 **Direct Link:**\n{direct_link}\n\n"
            f"⚡ *Isme latest file ka live URL include hai.*"
        )
    else:
        await status_msg.edit("❌ Link bypass nahi ho paya.")

print("Deep Bypass Bot Online...")
bot.run_until_disconnected()
