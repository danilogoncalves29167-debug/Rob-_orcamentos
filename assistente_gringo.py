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
# Memória para rastrear onde o usuário parou (ex: user_id -> última série assistida e parte/temporada atual)
historico_progresso = {}

# BASE DE DADOS DE FITA COM SEQUÊNCIA (Parte 1, Parte 2, Temporadas)
# Aqui tu substituis os links pelos arquivos reais (file_id do Telegram ou links diretos de streaming)
ACERVO_SERIES = {
    "the walking dead": {
        "nome": "The Walking Dead",
        "partes": {
            "1": "https://t.me/seu_canal_player/temporada_1_episodio_1",
            "2": "https://t.me/seu_canal_player/temporada_1_episodio_2",
            "3": "https://t.me/seu_canal_player/temporada_1_episodio_3"
        }
    },
    "homem aranha": {
        "nome": "Homem-Aranha (Saga Completa)",
        "partes": {
            "1": "https://t.me/seu_canal_player/homem_aranha_1",
            "2": "https://t.me/seu_canal_player/homem_aranha_2_de_volta_ao_lar"
        }
    }
}

bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id == MEU_TOKEN_MESTRE:
        await update.message.reply_text("Salve, chefe! Sistema de episódios sequenciais pronto.")
    else:
        await update.message.reply_text(
            "🍿 **Cinema no Bolso**\n\n"
            "Manda o nome da série ou filme que tu quer começar a assistir. Quando acabar, é só pedir a parte dois que eu mando na hora!\n\n"
            "(Você tem direito a 1 teste gratuito)."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_id = str(update.effective_user.id)
    texto_usuario = update.message.text.strip().lower()

    if user_id == MEU_TOKEN_MESTRE:
        await update.message.reply_text("⚡ Modo patrão ativado...")
    else:
        usos_atuais = testes_usuarios.get(user_id, 0)
        if usos_atuais < 1:
            testes_usuarios[user_id] = usos_atuais + 1
            await update.message.reply_text("Teste grátis liberado! Carregando a fita...")
        else:
            await update.message.reply_text(
                f"Seu teste gratuito acabou. Para continuar maratonando tudo sem limite por apenas **R$ 25**, efetue a assinatura VIP:\n\n{LINK_PAGAMENTO_PIX}"
            )
            return

    # Identifica se o usuário está pedindo a continuação (ex: "parte 2", "proximo", "temporada 2")
    if "parte 2" in texto_usuario or "2" in texto_usuario or "continuar" in texto_usuario:
        ultimo_pedido = historico_progresso.get(user_id)
        if ultimo_pedido and ultimo_pedido in ACERVO_SERIES:
            serie_info = ACERVO_SERIES[ultimo_pedido]
            link_parte_2 = serie_info["partes"].get("2", "Link da parte 2 em breve no canal oficial!")
            await update.message.reply_text(
                f"🎬 **Mandando a continuação: {serie_info['nome']} (Parte 2)**\n\n"
                f"🔗 **Link Direto:**\n{link_parte_2}\n\n"
                "🔥 Bom filme, cachorro!"
            )
            return

    # Busca normal pelo nome da obra
    obra_encontrada = None
    for chave in ACERVO_SERIES:
        if chave in texto_usuario:
            obra_encontrada = chave
            break

    if obra_encontrada:
        historico_progresso[user_id] = obra_encontrada
        serie_info = ACERVO_SERIES[obra_encontrada]
        link_parte_1 = serie_info["partes"].get("1", "Link indisponível")
        
        await update.message.reply_text(
            f"🎬 **Achei a fita: {serie_info['nome']}**\n\n"
            f"📺 **Parte 1 / Início liberado:**\n{link_parte_1}\n\n"
            "💡 *Terminou de ver? É só mandar 'quero a parte dois' que eu libero a sequência na hora!*"
        )
    else:
        await update.message.reply_text(
            f"Eita, essa fita exata ainda não tá na agulha da base de teste, mano. Mas no acervo VIP completo tem tudo!"
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
    
