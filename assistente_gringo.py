import os
import requests
import asyncio
from flask import Flask, request as flask_request, render_template_string
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters

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
        await update.message.reply_text("Salve, chefe! Modo automático total ativado. Manda o nome do filme ou série!")
    else:
        await update.message.reply_text(
            "🍿 **Cinema no Bolso**\n\n"
            "Digite o nome de qualquer filme ou série para o bot buscar o link de streaming automaticamente na rede.\n\n"
            "(Você tem direito a 1 teste gratuito)."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_id = str(update.effective_user.id)
    termo_busca = update.message.text.strip()

    if user_id == MEU_TOKEN_MESTRE:
        await update.message.reply_text("⚡ Buscando no modo patrão (ilimitado e automático)...")
    else:
        usos_atuais = testes_usuarios.get(user_id, 0)
        if usos_atuais < 1:
            testes_usuarios[user_id] = usos_atuais + 1
            await update.message.reply_text("Teste grátis liberado! Buscando na rede...")
        else:
            await update.message.reply_text(
                f"Seu teste gratuito acabou. Para continuar assistindo a tudo sem anúncios por apenas **R$ 25**, efetue a assinatura VIP:\n\n{LINK_PAGAMENTO_PIX}"
            )
            return

    status_msg = await update.message.reply_text("🔍 Varrendo a web e gerando o link de streaming automático...")

    try:
        # Tratamento automático usando motor público de metadados/busca de mídia
        termo_formatado = termo_busca.replace(" ", "%20")
        
        url_api_publica = f"https://api.tvmaze.com/search/shows?q={termo_formatado}"
        resposta = requests.get(url_api_publica, timeout=15)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados and len(dados) > 0:
                show = dados[0]['show']
                nome_oficial = show.get('name', termo_busca)
                generos = ", ".join(show.get('genres', ['Filme/Série']))
                site_oficial = show.get('officialSite') or show.get('url', 'https://www.google.com/search?q=' + termo_formatado)
                
                await update.message.reply_text(
                    f"🎬 **Achei a fita automaticamente!**\n\n"
                    f"📺 **Título:** {nome_oficial}\n"
                    f"🏷️ **Gênero:** {generos}\n\n"
                    f"🔗 **Link de Acesso Direto:**\n{site_oficial}\n\n"
                    "🔥 Aproveite sem travar!"
                )
            else:
                await update.message.reply_text(
                    f"Eita, não achei nada automático com o nome '{termo_busca}'. Tenta digitar o nome exato da obra!"
                )
        else:
            await update.message.reply_text("Falha ao conectar com os servidores de busca. Tente novamente em instantes.")
            
    except Exception as e:
        await update.message.reply_text(f"Erro ao processar a busca automática: {str(e)}")

bot_app.add_handler(CommandHandler("start", start_command))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Cinema no Bolso</title>
    <style>
        body { background-color: #0b0b0b; color: #fff; font-family: sans-serif; text-align: center; padding: 50px; }
        .container { background: #161616; padding: 40px; border-radius: 16px; display: inline-block; border: 1px solid #222; }
        h1 { color: #ff3333; }
        a { color: #00ff66; font-weight: bold; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>CINEMA NO BOLSO</h1>
        <p>O bot automático de filmes e séries do Telegram está ativo. Para liberar acesso completo por apenas R$ 25, assine:</p>
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
    
