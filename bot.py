import os, tempfile, asyncio, glob
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a link from Facebook / Instagram / TikTok / YouTube / X and I will remove the music and send you clean voice 🎧")

def download(url):
    tmp = tempfile.mkdtemp()
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{tmp}/%(title)s.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        base = ydl.prepare_filename(info)
        files = glob.glob(f"{tmp}/*.mp3")
        return (files[0] if files else base), info.get('title','audio')

def clean(inp):
    out = inp.replace(".mp3","_voice.mp3")
    os.system(f'ffmpeg -y -i "{inp}" -af "highpass=f=200,lowpass=f=3000" "{out}" -loglevel quiet')
    return out if os.path.exists(out) else inp

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"): 
        return
    msg = await update.message.reply_text("Downloading and removing music... please wait ⏳")
    try:
        loop = asyncio.get_event_loop()
        ap, title = await loop.run_in_executor(None, download, url)
        cp = await loop.run_in_executor(None, clean, ap)
        with open(cp, 'rb') as f:
            await update.message.reply_voice(voice=f, caption=f"Done: {title} ✅")
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"Error: {str(e)[:200]}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("Bot running 12h/day")
    app.run_polling()
