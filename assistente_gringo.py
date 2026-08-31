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
        await update.message.reply_text("Salve, chefe! Modo gravadora blindada ativado. Manda o nome ou link do som!")
    else:
        await update.message.reply_text(
            "🎵 **Baixador de Músicas VIP**\n\n"
            "Mande o nome de qualquer música ou link para receber o arquivo MP3 direto no seu celular.\n\n"
            "(Você tem direito a 1 teste gratuito)."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_id = str(update.effective_user.id)
    termo_busca = update.message.text.strip()

    if user_id == MEU_TOKEN_MESTRE:
        pass # Patrão passa direto
    else:
        usos_atuais = testes_usuarios.get(user_id, 0)
        if usos_atuais < 1:
            testes_usuarios[user_id] = usos_atuais + 1
            await update.message.reply_text("Teste grátis liberado! Baixando o arquivo MP3...")
        else:
            await update.message.reply_text(
                f"Seu teste gratuito acabou. Para continuar baixando músicas direto para o celular sem limite por apenas **R$ 25**, efetue a assinatura VIP:\n\n{LINK_PAGAMENTO_PIX}"
            )
            return

    status_msg = await update.message.reply_text("🎧 Convertendo a fita em MP3, aguenta um segundo...")

    audio_path = None
    try:
        # Força a busca otimizada direto no YouTube para extrair o áudio bruto
        query = termo_busca if "http" in termo_busca else f"ytsearch1:{termo_busca}"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
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
            audio_path = os.path.splitext(filename)[0] + ".mp3"
            titulo_musica = info.get('title', 'Áudio Baixado')

        # Envia o arquivo MP3 de verdade para rodar direto no celular do usuário
        with open(audio_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                caption=f"🎵 **{titulo_musica}**\n🔥 Pronto para escutar no talo!",
                title=titulo_musica
            )
        
        await status_msg.delete()
            
    except Exception as e:
        # Se der qualquer bosta, agora ele avisa direito em vez de mandar para o Google
        await status_msg.edit_text(
            f"❌ Deu ruim na conversão dessa música específica, mano. Tenta mandar o nome exato ou o link direto do YouTube/Spotify!"
        )
    finally:
        # Garante a limpeza do arquivo local no servidor
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

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    json_data = flask_request.get_json(force=True)
    update = Update.de_json(json_data, bot_app.bot)
    
    async def processar():
        await bot_app.initialize()
        await bot_app.process_update(update)
        
    asyncio.run(processar())
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
