import os
import requests
from flask import Flask, request as flask_request, render_template_string
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

app = Flask(__name__)

# CONFIGURAÇÕES OFICIAIS: API do Bot, ID Mestre e Link de Pagamento Integrados
TELEGRAM_BOT_TOKEN = "8940699833:AAFRxnt0Ew__V0g223oNHRaftvO246GPeyQ"
MEU_TOKEN_MESTRE = "8964511789"
LINK_PAGAMENTO_PIX = "https://mpago.la/33m86YJ"

# Dicionário simples para controlar quem já usou os testes grátis
testes_usuarios = {}

# Template HTML básico para a rota web do Render
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
    update = Update.de_json(flask_request.get_json(force=True), bot_app.bot)
    return "OK", 200

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    prompt_usuario = update.message.text

    # Se for o teu ID mestre, passa direto sem limite
    if user_id == MEU_TOKEN_MESTRE:
        pass
    else:
        usos_atuais = testes_usuarios.get(user_id, 0)
        if usos_atuais < 2:
            testes_usuarios[user_id] = usos_atuais + 1
            restantes = 2 - testes_usuarios[user_id]
            await update.message.reply_text(f"🎁 Teste grátis liberado! (Restam {restantes + 1} usos). Processando na nuvem...")
        else:
            await update.message.reply_text(
                f"⚠️ Seus testes grátis acabaram! Para continuar gerando imagens no talo, assine o acesso VIP:\n\n{LINK_PAGAMENTO_PIX}"
            )
            return

    await update.message.reply_text("⚡ Conectando ao motor externo de alta definição, chefe...")

    try:
        # Usando uma API pública gratuita e leve via Pollinations AI para gerar a imagem direto por link, sem pesar o servidor
        prompt_formatado = prompt_usuario.replace(" ", "%20")
        url_imagem_externa = f"https://image.pollinations.ai/prompt/{prompt_formatado}?width=1024&height=1024&nologo=true"
        
        # Baixa a imagem gerada pela nuvem de forma leve
        resposta_img = requests.get(url_imagem_externa, timeout=30)
        if resposta_img.status_code == 200:
            os.makedirs("static", exist_ok=True)
            caminho_imagem = "static/gerado.png"
            with open(caminho_imagem, "wb") as f:
                f.write(resposta_img.content)
            
            await update.message.reply_photo(photo=open(caminho_imagem, "rb"), caption="🔥 Imagem gerada com sucesso na nuvem, cachorro!")
        else:
            await update.message.reply_text("❌ Deu ruim na API externa, tenta mandar o prompt de novo, mano.")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro de conexão com o motor: {str(e)}")

bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
