import os
import asyncio
from flask import Flask, request as flask_request, render_template_string
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
import yt_dlp

app = Flask(__name__)

# TOKEN OFICIAL, ID MESTRE E LINK PIX ATUALIZADO
TELEGRAM_BOT_TOKEN = "8905719627:AAEkdRBkweO-62u_td0jyKfTZYaxGQNZNI0"
MEU_TOKEN_MESTRE = "8964511789"
LINK_PAGAMENTO_PIX = "https://mpago.li/2GsYcDg"

testes_usuarios = {}

bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id == MEU_TOKEN_MESTRE:
        await update.message.reply_text("Salve, chefe! Servidor 100% blindado e operacional. Manda o som!")
    else:
        await update.message.reply_text(
            "🎵 **Baixador de Músicas VIP**\n\n"
            "Mande o nome da música ou o link para baixar o áudio direto no seu celular.\n\n"
            "(Você tem direito a 1 teste gratuito)."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_id = str(update.effective_user.id)
    termo_busca = update.message.text.strip()

    if user_id == MEU_TOKEN_MESTRE:
        pass 
    else:
        usos_atuais = testes_usuarios.get(user_id, 0)
        if usos_atuais < 1:
            testes_usuarios[user_id] = usos_atuais + 1
            await update.message.reply_text("Teste grátis liberado! Baixando o arquivo...")
        else:
            await update.message.reply_text(
                f"Seu teste gratuito acabou. Para continuar baixando músicas sem limite por apenas **R$ 25**, assine o acesso VIP:\n\n{LINK_PAGAMENTO_PIX}"
            )
            return

    status_msg = await update.message.reply_text("🎧 Buscando o som na base, aguenta um segundo...")

    audio_path = None
    try:
        query = termo_busca if "http" in termo_busca else f"ytsearch1:{termo_busca}"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True
        }

        os.makedirs("downloads", exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            filename = ydl.prepare_filename(info)
            
            base, ext = os.path.splitext(filename)
            audio_path = base + ".mp3"
            
            if os.path.exists(filename):
                if ext != ".mp3":
                    os.rename(filename, audio_path)
                else:
                    audio_path = filename
            
            titulo_musica = info.get('title', 'Áudio Baixado')

        with open(audio_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                caption=f"🎵 **{titulo_musica}**\n🔥 Baixado com sucesso!",
                title=titulo_musica
            )
        
        await status_msg.delete()
            
    except Exception as e:
        await status_msg.edit_text(
            f"❌ Deu pau ao processar essa faixa, mano. Tenta mandar o nome limpo da música ou outro link!"
        )
    finally:
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass

bot_app.add_handler(CommandHandler("start", start_command))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Baixador de Músicas VIP</title>
    <style>
        body { background-color: #0b0b0b; color: #fff; font-family: sans-serif; text-align: center; padding: 50px; }
        .container { background: #161616; padding: 40px; border-radius: 16px; display: inline-block; border: 1px solid #222; }
        h1 { color: #1db954; }
        a { color: #00ff66; font-weight: bold; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>SPOTIFY & MP3 DOWNLOADER</h1>
        <p>O bot automático de músicas do Telegram está ativo. Para liberar acesso completo por apenas R$ 25, assine:</p>
        <a href="{{ link_pagamento }}" target="_blank">Assinar Acesso VIP por R$ 25</a>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, link_pagamento=LINK_PAGAMENTO_PIX)

# Inicializa o bot para o Render não perder os pacotes
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(bot_app.initialize())

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    json_data = flask_request.get_json(force=True)
    update = Update.de_json(json_data, bot_app.bot)
    
    async def processar():
        await bot_app.process_update(update)

    try:
        loop.run_until_complete(processar())
    except Exception:
        asyncio.run(processar())
        
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
