import os
import time
import threading
import requests
import yt_dlp
from flask import Flask

# Web Server Mini untuk syarat Free Plan Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Telegram YT to MP3 Aktif!"

TOKEN = "9267531622:AAF35D5bGMGg-p5k8xgPPArPBjtg-B98nMo"
API_URL = f"https://api.telegram.org/bot{TOKEN}/"

def get_updates(offset=None):
    url = API_URL + "getUpdates?timeout=30"
    if offset:
        url += f"&offset={offset}"
    try:
        res = requests.get(url, timeout=35)
        return res.json()
    except Exception:
        return None

def send_message(chat_id, text):
    url = API_URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, data=payload)

def send_audio(chat_id, file_path, title):
    url = API_URL + "sendAudio"
    with open(file_path, "rb") as audio:
        payload = {"chat_id": chat_id, "title": title}
        files = {"audio": audio}
        requests.post(url, data=payload, files=files)

def process_youtube(url, chat_id):
    send_message(chat_id, "⚡ Mengunduh MP3 di Cloud...")
    
    output_filename = f"audio_{int(time.time())}"
    mp3_file = f"{output_filename}.mp3"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_filename}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'YouTube Audio')
            
        if os.path.exists(mp3_file):
            send_message(chat_id, "📤 Mengirim MP3...")
            send_audio(chat_id, mp3_file, title)
            os.remove(mp3_file)
        else:
            send_message(chat_id, "❌ Gagal mengonversi file audio.")
    except Exception as e:
        send_message(chat_id, f"❌ Terjadi kesalahan: {str(e)}")

def bot_loop():
    last_update_id = None
    print("Bot YT to MP3 berjalan...")
    while True:
        updates = get_updates(last_update_id)
        if updates and "result" in updates:
            for update in updates["result"]:
                last_update_id = update["update_id"] + 1
                message = update.get("message")
                if not message or "text" not in message:
                    continue
                
                chat_id = message["chat"]["id"]
                text = message["text"]
                
                if text == "/start":
                    send_message(chat_id, "Halo mas Arie! Kirimkan link YouTube untuk diubah jadi MP3.")
                elif "youtube.com" in text or "youtu.be" in text:
                    process_youtube(text, chat_id)
        time.sleep(1)

# Jalankan Bot Telegram di Thread terpisah
threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
