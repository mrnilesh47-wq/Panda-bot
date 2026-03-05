import sqlite3
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = '8184975668:AAHCNDZl2qAHK68FtwBx5vXx-2_ScnEAzFo'

# Render ko "Live" signal dene ke liye chota server
class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running!")

def run_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), SimpleServer)
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
    # Server ko alag thread mein chalayein
    threading.Thread(target=run_server, daemon=True).start()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL & filters.VIDEO, handle_channel_post))
    print("Bot chalu ho gaya hai...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
