import os
import torch
from flask import Flask, request, render_template_string
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from diffusers import StableDiffusionPipeline

app = Flask(__name__)

# CONFIGURAÇÕES OFICIAIS: API do Bot, ID Mestre e Link de Pagamento Integrados
TELEGRAM_BOT_TOKEN = "8940699833:AAFRxnt0Ew__V0g223oNHRaftvO246GPeyQ"
MEU_TOKEN_MESTRE = "8964511789"
LINK_PAGAMENTO_PIX = "https://mpago.la/33m86YJ"

# Dicionário simples para controlar quem já usou os testes grátis
testes_usuarios = {}

# Carrega um modelo leve (Stable Diffusion 1.5) que cabe nos 512MB de RAM do Render
print("Carregando o motor leve otimizado...")
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(
    model_id, 
    torch_dtype=torch.float16, 
    use_safetensors=True
)
pipe = pipe.to("cpu")
pipe.enable_attention_slicing()

# Template HTML básico para a rota web
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
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    return "OK", 200

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    prompt_usuario = update.message.text

    # Se for o teu ID mestre, passa direto sem limite
    if user_id == MEU_TOKEN_MESTRE:
        pass
    else:
        # Pega quantas vezes o maluco já usou (começa em 0)
        usos_atuais = testes_usuarios.get(user_id, 0)
        
        if usos_atuais < 2:
            # Ainda tem direito aos testes grátis (2 chances)
            testes_usuarios[user_id] = usos_atuais + 1
            restantes = 2 - testes_usuarios[user_id]
            await update.message.reply_text(f"🎁 Teste grátis liberado! (Faltam {restantes + 1} usos gratuitos). Processando...")
        else:
            # Acabaram os testes, manda direto para o Pix de 65 contos
            await update.message.reply_text(
                f"⚠️ Seus testes grátis acabaram! Para continuar gerando imagens no talo, assine o acesso VIP:\n\n{LINK_PAGAMENTO_PIX}"
            )
            return

    await update.message.reply_text("⚡ Processando tua imagem no motor otimizado, chefe...")

    negative_prompt = "cartoon, illustration, painting, blurry, low quality, distorted, deformed"
    image = pipe(
        prompt=prompt_usuario, 
        negative_prompt=negative_prompt, 
        num_inference_steps=20,
        guidance_scale=7.5
    ).images[0]
    
    os.makedirs("static", exist_ok=True)
    caminho_imagem = "static/gerado.png"
    image.save(caminho_imagem)

    await update.message.reply_photo(photo=open(caminho_imagem, "rb"), caption="🔥 Imagem gerada com sucesso, cachorro!")

bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
