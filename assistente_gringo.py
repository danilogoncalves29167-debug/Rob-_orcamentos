import os
import requests
import asyncio
from flask import Flask, request as flask_request, render_template_string
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters

app = Flask(__name__)

# NOVO TOKEN OFICIAL DO TELEGRAM, ID MESTRE E LINK PIX
TELEGRAM_BOT_TOKEN = "8905719627:AAEkdRBkweO-62u_td0jyKfTZYaxGQNZNI0"
MEU_TOKEN_MESTRE = "8964511789"
LINK_PAGAMENTO_PIX = "https://mpago.la/33m86YJ"

testes_usuarios = {}

bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Comando /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id == MEU_TOKEN_MESTRE:
        await update.message.reply_text("Salve, chefe! Acesso total e ilimitado liberado para o dono da porra toda. Manda o prompt aí!")
    else:
        await update.message.reply_text(
            "Olá! Seja bem-vindo ao gerador de imagens por Inteligência Artificial.\n\n"
            "Envie o texto descrevendo a imagem que você deseja criar (você tem direito a 2 testes gratuitos)."
        )

# Função para processar prompts de imagem
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_id = str(update.effective_user.id)
    prompt_usuario = update.message.text

    # Se for o dono (ID mestre), passa direto sem gastar nada
    if user_id == MEU_TOKEN_MESTRE:
        await update.message.reply_text("⚡ Gerando imagem no modo patrão (ilimitado)...")
    else:
        usos_atuais = testes_usuarios.get(user_id, 0)
        if usos_atuais < 2:
            testes_usuarios[user_id] = usos_atuais + 1
            restantes = 2 - testes_usuarios[user_id]
            await update.message.reply_text(f"Teste grátis liberado! (Restam {restantes} usos). Processando na nuvem...")
        else:
            await update.message.reply_text(
                f"Seus testes gratuitos acabaram. Para continuar gerando imagens, efetue a assinatura:\n\n{LINK_PAGAMENTO_PIX}"
            )
            return

    try:
        prompt_formatado = prompt_usuario.replace(" ", "%20")
        url_imagem_externa = f"https://image.pollinations.ai/prompt/{prompt_formatado}?width=1024&height=1024&nologo=true"
        
        resposta_img = requests.get(url_imagem_externa, timeout=30)
        if resposta_img.status_code == 200:
            os.makedirs("static", exist_ok=True)
            caminho_imagem = "static/gerado.png"
            with open(caminho_imagem, "wb") as f:
                f.write(resposta_img.content)
            
            await update.message.reply_photo(photo=open(caminho_imagem, "rb"), caption="🔥 Imagem gerada com sucesso!")
        else:
            await update.message.reply_text("Ocorreu uma falha na geração da imagem. Tente enviar o prompt novamente.")
    except Exception as e:
        await update.message.reply_text(f"Erro de conexão com o motor: {str(e)}")

bot_app.add_handler(CommandHandler("start", start_command))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Gerador VIP</title>
    <style>
        body { background-color: #0b0b0b; color: #fff; font-family: sans-serif; text-align: center; padding: 50px; }
        .container { background: #161616; padding: 40px; border-radius: 16px; display: inline-block; border: 1px solid #222; }
        h1 { color: #00ff66; }
        a { color: #ff4d4d; font-weight: bold; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>SISTEMA OPERANTE</h1>
        <p>O bot do Telegram está ativo. Para liberar o acesso completo, assine:</p>
        <a href="{{ link_pagamento }}" target="_blank">Assinar Acesso VIP por R$ 65</a>
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
    
