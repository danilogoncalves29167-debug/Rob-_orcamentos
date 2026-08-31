import os
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
historico_progresso = {}

# ACERVO COM FILE_ID DO TELEGRAM OU LINKS DIRETOS DE STREAMING
# Dica: Para mandar o vídeo direto na tela, tu podes usar o ID do arquivo que o Telegram gera quando tu encaminhas o vídeo para o bot!
ACERVO_SERIES = {
    "the walking dead": {
        "nome": "The Walking Dead",
        "partes": {
            "1": "https://www.w3schools.com/html/mov_bbb.mp4", # Exemplo de link direto em MP4 que roda direto no player nativo
            "2": "https://www.w3schools.com/html/mov_bbb.mp4"
        }
    },
    "homem aranha": {
        "nome": "Homem-Aranha",
        "partes": {
            "1": "https://www.w3schools.com/html/mov_bbb.mp4",
            "2": "https://www.w3schools.com/html/mov_bbb.mp4"
        }
    }
}

bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id == MEU_TOKEN_MESTRE:
        await update.message.reply_text("Salve, chefe! Acesso total e ilimitado liberado para o patrão. Manda o nome da fita!")
    else:
        await update.message.reply_text(
            "🍿 **Cinema no Bolso**\n\n"
            "Digite o nome da série ou filme que tu quer assistir. O vídeo vai direto na tua tela!\n\n"
            "(Você tem direito a 1 teste gratuito)."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_id = str(update.effective_user.id)
    texto_usuario = update.message.text.strip().lower()

    # CORREÇÃO CRUCIAL: O chefe (tu) nunca é bloqueado e tem passe livre eterno!
    if user_id == MEU_TOKEN_MESTRE:
        pass # Deixa passar direto pro catálogo sem barrar
    else:
        usos_atuais = testes_usuarios.get(user_id, 0)
        if usos_atuais < 1:
            testes_usuarios[user_id] = usos_atuais + 1
            await update.message.reply_text("Teste grátis liberado! Carregando o player...")
        else:
            await update.message.reply_text(
                f"Seu teste gratuito acabou. Para continuar maratonando tudo sem limite por apenas **R$ 25**, efetue a assinatura VIP:\n\n{LINK_PAGAMENTO_PIX}"
            )
            return

    # Verifica se o usuário pediu continuação (parte 2)
    if "parte 2" in texto_usuario or "2" in texto_usuario or "continuar" in texto_usuario:
        ultimo_pedido = historico_progresso.get(user_id)
        if ultimo_pedido and ultimo_pedido in ACERVO_SERIES:
            serie_info = ACERVO_SERIES[ultimo_pedido]
            link_video = serie_info["partes"].get("2")
            
            await update.message.reply_text(f"🎬 Mandando a Parte 2 de {serie_info['nome']}...")
            try:
                await update.message.reply_video(video=link_video, caption="🔥 Aproveite a continuação direto na tela!")
            except Exception:
                await update.message.reply_text(f"🔗 Link direto da parte 2:\n{link_video}")
            return

    # Busca da obra pelo nome
    obra_encontrada = None
    for chave in ACERVO_SERIES:
        if chave in texto_usuario:
            obra_encontrada = chave
            break

    if obra_encontrada:
        historico_progresso[user_id] = obra_encontrada
        serie_info = ACERVO_SERIES[obra_encontrada]
        link_video = serie_info["partes"].get("1")
        
        await update.message.reply_text(f"🎬 Achando a fita: {serie_info['nome']}...")
        
        try:
            # Manda o vídeo direto para rodar na tela do Telegram do usuário
            await update.message.reply_video(
                video=link_video, 
                caption=f"🍿 **{serie_info['nome']} (Parte 1)**\n\n💡 Acabou? Manda 'quero a parte dois' que eu libero a sequência!"
            )
        except Exception:
            # Fallback caso o link seja apenas texto/url web
            await update.message.reply_text(
                f"🎬 **{serie_info['nome']}**\n\n🔗 **Link Direto:**\n{link_video}\n\n💡 Terminou? Manda 'parte 2'!"
            )
    else:
        await update.message.reply_text(
            f"Eita, o brabo '{texto_usuario}' não tá na base de teste rápida, chefe. Mas no acervo completo tá liberado!"
        )

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
    
