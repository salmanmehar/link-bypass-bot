import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events

# Render free server keeping alive handler
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Link Bypass Bot Active!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# Environment Configurations
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0)) # Admin's Telegram User ID

bot = TelegramClient(None, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Dynamic File Storage (Memory / Real-time Map)
# Structure: { "file_key": { "channel_id": -100xxx, "message_id": 123 } }
file_database = {}

@bot.on(events.NewMessage(pattern=r'/start (.*)'))
async def handle_start_with_param(event):
    file_key = event.pattern_match.group(1).strip()
    
    if file_key in file_database:
        data = file_database[file_key]
        try:
            # Dynamic Fetching: Real-time latest message fetch karega target channel se
            latest_msg = await bot.get_messages(data["channel_id"], ids=data["message_id"])
            if latest_msg and latest_msg.media:
                await bot.send_file(
                    event.chat_id,
                    file=latest_msg.media,
                    caption=latest_msg.text or "✅ Ye rahi aapki updated file!"
                )
            else:
                await event.reply("⚠️ Target file delete ho chuki hai ya corrupt hai. Admin se contact karein.")
        except Exception as e:
            await event.reply(f"❌ Error fetching file: {str(e)}")
    else:
        await event.reply("❌ Ye link expire ho chuka hai ya invalid hai.")

@bot.on(events.NewMessage(pattern=r'/start$'))
async def handle_start_pure(event):
    await event.reply("👋 Namaste! Main Link Bypass & File Provider Bot hu.\nLink ke through access karein.")

# ADMIN COMMAND: File Update / Replace karne ke liye
# Usage: /updatefile <file_key> (Reply to the new file message from DB channel)
@bot.on(events.NewMessage(pattern=r'/updatefile (.*)'))
async def update_file_key(event):
    if event.sender_id != ADMIN_ID:
        await event.reply("⛔ Aapke paas is command ki permission nahi hai.")
        return

    file_key = event.pattern_match.group(1).strip()
    reply_msg = await event.get_reply_message()

    if not reply_msg:
        await event.reply("⚠️ Kripya kisi file / message par reply karke ye command dein.")
        return

    # Update database with new Message ID dynamically
    file_database[file_key] = {
        "channel_id": reply_msg.chat_id,
        "message_id": reply_msg.id
    }

    bot_user = await bot.get_me()
    bypass_link = f"https://t.me/{bot_user.username}?start={file_key}"
    
    await event.reply(
        f"✅ **File Link Updated Successfully!**\n\n"
        f"🔑 **Key:** `{file_key}`\n"
        f"🔗 **Bypass Link:** {bypass_link}\n\n"
        f"⚡ Purani corrupted file ab nayi file se replace ho gayi hai."
    )

print("Link Bypass Bot Online...")
bot.run_until_disconnected()
