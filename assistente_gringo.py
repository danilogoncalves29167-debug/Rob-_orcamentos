import os
import torch
from flask import Flask, request, redirect, render_template_string
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from diffusers import StableDiffusionXLPipeline

app = Flask(__name__)

# CONFIGURAÇÕESOFICIAIS: API do Bot, ID Mestre e Link de Pagamento Integrados
TELEGRAM_BOT_TOKEN = "8940699833:AAFRxnt0Ew__V0g223oNHRaftvO246GPeyQ"
MEU_TOKEN_MESTRE = "8964511789"
LINK_PAGAMENTO_PIX = "https://mpago.la/33m86YJ"

# Carrega o modelo SDXL otimizado para máxima nitidez e realismo
print("Carregando o motor de imagens em alta definição...")
model_id = "stabilityai/stable-diffusion-xl-base-1.0"
pipe = StableDiffusionXLPipeline.from_pretrained(
    model_id, 
    torch_dtype=torch.float16, 
    use_safetensors=True
)
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

# Template HTML caso alguém acesse a rota web no Render
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Gerador 4K VIP</title>
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
        <p>O bot do Telegram está ativo. Para gerar imagens, acesse pelo Telegram ou assine:</p>
        <a href="{{ link_pagamento }}" target="_blank">Assinar Acesso VIP por R$ 65</a>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, link_pagamento=LINK_PAGAMENTO_PIX)

# Rota para o Webhook do Telegram receber as mensagens dos usuários
@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    # Aqui processaria a atualização do Telegram de forma assíncrona ou direta
    return "OK", 200

# Função que processa os prompts enviados no Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    prompt_usuario = update.message.text

    # Trava de segurança: Se for o teu ID mestre, libera geral. Senão, manda o link de pagamento.
    if user_id != MEU_TOKEN_MESTRE:
        await update.message.reply_text(
            f"⚠️ Acesso restrito! Para liberar o gerador 4K completo, efetue o pagamento da assinatura:\n\n{LINK_PAGAMENTO_PIX}"
        )
        return

    await update.message.reply_text("⚡ Processando tua obra-prima em alta definição, chefe...")

    # Parâmetros para garantir realismo bruto
    negative_prompt = "cartoon, illustration, painting, blurry, low quality, distorted, plastic skin, artificial, deformed"
    image = pipe(
        prompt=prompt_usuario, 
        negative_prompt=negative_prompt, 
        num_inference_steps=35,
        guidance_scale=7.5
    ).images[0]
    
    os.makedirs("static", exist_ok=True)
    caminho_imagem = "static/gerado.png"
    image.save(caminho_imagem)

    # Devolve a imagem gerada direto no chat do Telegram
    await update.message.reply_photo(photo=open(caminho_imagem, "rb"), caption="🔥 Imagem 4K gerada com sucesso, cachorro!")

# Inicializa o construtor do bot do Telegram
from telegram.ext import Application
bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
