# -*- coding: utf-8 -*-
import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

# Configura logs para aparecerem no Render
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Servidor Flask essencial para o Render manter a porta ativa
app = Flask(__name__)

@app.route('/')
def home():
    return "Alpha Club Bot está operando na escuta."

# CONFIGURAÇÕES DO BOT E DO PAGAMENTO
TELEGRAM_BOT_TOKEN = "8905719627:AAEkdRBkweO-62u_td0jyKfTZYaxGQNZNI0"
LINK_PAGAMENTO_PIX = "https://mpago.la/1psrqrL"
MEU_TOKEN_MESTRE = "8964511789"

testes_usuarios = {}

# Inicializa o cliente do Google Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    termo_consentimento = (
        "🔒 *TERMOS DE USO E ISENÇÃO DE RESPONSABILIDADE - ALPHA CLUB*\n\n"
        "Ao interagir com este sistema, você declara expressamente que leu, compreendeu e concorda "
        "com os nossos Termos de Serviço e Política de Isenção de Responsabilidade.\n\n"
        "1. As informações e análises geradas possuem caráter estritamente educacional e teórico.\n"
        "2. Os desenvolvedores não se responsabilizam por decisões ou resultados financeiros.\n\n"
        "⚖️ *Ao enviar qualquer termo, você concorda integralmente com estes termos.*\n\n"
        "--- \n\n"
        "Bem-vindo à Matriz Alpha. Envie qualquer termo macroeconômico ou ativo para gerar sua análise executiva inicial."
    )
    
    await update.message.reply_text(termo_consentimento, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_id = str(update.effective_user.id)
    texto_usuario = update.message.text.strip()

    if user_id == MEU_TOKEN_MESTRE:
        pass 
    else:
        usos_atuais = testes_usuarios.get(user_id, 0)
        if usos_atuais < 1:
            testes_usuarios[user_id] = usos_atuais + 1
        else:
            await update.message.reply_text(
                f"🚨 *ACESSO DE TESTE ESGOTADO* 🚨\n\n"
                f"Sua triagem gratuita expirou. Para continuar recebendo os relatórios e manter seu status no clube por R$ 250 mensais, efetue a assinatura:\n\n"
                f"{LINK_PAGAMENTO_PIX}",
                parse_mode="Markdown"
            )
            return

    # Manda a mensagem inicial de status para ser editada depois (evita sumir mensagens)
    status_msg = await update.message.reply_text("📊 Processando análise de inteligência de mercado... Aguarde.")

    prompt = (
        "Aja como um analista sênior brasileiro de mercado financeiro, direto ao ponto e altamente técnico. "
        "Escreva um relatório executivo de tamanho médio, rico em conceitos de macroeconomia, dinâmica de preços "
        "e comportamento de ativos, explicando o tema com clareza em português do Brasil. O foco é entregar "
        "um conteúdo de alto valor educacional que faça o leitor absorver a lógica de mercado instantaneamente."
        f"\n\nTermo ou ativo solicitado pelo usuário: {texto_usuario}"
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        if not response.text:
            raise ValueError("Resposta vazia da IA.")
            
        relatorio = response.text
        
        # Limpa eventuais marcações markdown quebradas que o Gemini possa mandar para não dar crash no Telegram
        relatorio_limpo = relatorio.replace("*", "").replace("_", "")
        
        mensagem_final = (
            f"📈 *RELATÓRIO DE INTELIGÊNCIA ALPHA #VIP* 📈\n\n{relatorio_limpo}\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *Quer desbloquear o fluxo contínuo e garantir sua vaga definitiva?*\n"
            f"Assine agora o acesso completo (R$ 250/mês):\n{LINK_PAGAMENTO_PIX}"
        )
        
        # Edita a mensagem anterior em vez de apagar, garantindo que o texto nunca suma
        await status_msg.edit_text(mensagem_final, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"ERRO NA GERACAO: {str(e)}")
        await status_msg.edit_text("❌ Ocorreu um pico de instabilidade na matriz ao processar este termo. Tenta mandar novamente.")

def main():
    bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    porta = int(os.environ.get("PORT", 10000))
    
    import threading
    t_flask = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=porta, debug=False, use_reloader=False))
    t_flask.daemon = True
    t_flask.start()
    
    logger.info("Servidor Flask e Bot do Telegram iniciando...")
    bot_app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
            
