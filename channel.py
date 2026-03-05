import sqlite3
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = '8184975668:AAHCNDZl2qAHK68FtwBx5vXx-2_ScnEAzFo'

# Render ko signal dene ke liye chota server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Active")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def init_db():
    conn = sqlite3.connect('video_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS videos (file_id TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.video:
        v_id = update.channel_post.video.file_unique_id
        conn = sqlite3.connect('video_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM videos WHERE file_id=?", (v_id,))
        if cursor.fetchone():
            try: await update.channel_post.delete()
            except: pass
        else:
            cursor.execute("INSERT INTO videos (file_id) VALUES (?)", (v_id,))
            conn.commit()
        conn.close()

def main():
    init_db()
    # Health check server chalu karein
    threading.Thread(target=run_health_check, daemon=True).start()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL & filters.VIDEO, handle_channel_post))
    print("Bot chalu ho gaya hai...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
