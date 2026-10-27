import os, tempfile, asyncio, glob, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me any link from YouTube, TikTok, Instagram, Twitter, Facebook, SoundCloud... and I'll convert it to MP3 🎵")

def download_tiktok_api(url):
    try:
        r = requests.post("https://www.tikwm.com/api/", data={"url": url, "count": 12, "cursor": 0, "web": 1, "hd": 1}, timeout=15).json()
        if r.get('data') and r['data'].get('music'):
            music_url = r['data']['music']
            tmp = tempfile.mkdtemp()
            path = f"{tmp}/song.mp3"
            data = requests.get(music_url, timeout=15).content
            with open(path, 'wb') as f:
                f.write(data)
            return path
    except Exception as e:
        print(f"TikTok API Error: {e}")
    return None

def download(url):
    tmp = tempfile.mkdtemp()
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{tmp}/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    files = glob.glob(f"{tmp}/*.mp3")
    return files[0] if files else None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "http" not in url:
        return
    
    await update.message.reply_text("⏳ Downloading... please wait")

    try:
        file_path = None
        if "tiktok.com" in url or "vt.tiktok" in url:
            file_path = download_tiktok_api(url)
        
        if not file_path:
            file_path = await asyncio.to_thread(download, url)

        if file_path and os.path.exists(file_path):
            await update.message.reply_audio(audio=open(file_path, 'rb'), caption="Done! 🎵 @VocalPure_AI_bot")
            os.remove(file_path)
        else:
            await update.message.reply_text("Failed to download 😔 Try another link")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
print("Universal Bot Started - All Sites Supported!")
app.run_polling()
