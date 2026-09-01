# -*- coding: utf-8 -*-
import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Alpha Club Bot está operando na escuta."

TELEGRAM_BOT_TOKEN = "8905719627:AAEkdRBkweO-62u_td0jyKfTZYaxGQNZNI0"
LINK_PAGAMENTO_PIX = "https://mpago.la/1psrqrL"
MEU_TOKEN_MESTRE = "8964511789"

testes_usuarios = {}

gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    termo_consentimento = (
        "TERMOS DE USO E ISENCAO DE RESPONSABILIDADE - ALPHA CLUB\n\n"
        "Ao interagir com este sistema, você declara expressamente que leu, compreendeu e concorda "
        "com os nossos Termos de Serviço.\n\n"
        "1. As informações e análises geradas possuem caráter estritamente educacional e teórico.\n"
        "2. Os desenvolvedores não se responsabilizam por decisões ou resultados financeiros.\n\n"
        "Envie qualquer termo macroeconômico ou ativo para gerar sua análise executiva inicial."
    )
    
    await update.message.reply_text(termo_consentimento)

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
                f"ACESSO DE TESTE ESGOTADO\n\n"
                f"Sua triagem gratuita expirou. Para continuar recebendo os relatórios por R$ 250 mensais, efetue a assinatura:\n\n"
                f"{LINK_PAGAMENTO_PIX}"
            )
            return

    status_msg = await update.message.reply_text("Processando análise de inteligência de mercado... Aguarde.")

    prompt = (
        "Aja como um analista sênior brasileiro de mercado financeiro, direto ao ponto e técnico. "
        "Escreva um relatório executivo de tamanho moderado, direto, objetivo e rico em conceitos macroeconômicos, "
        "explicando o tema com clareza em português do Brasil."
        f"\n\nTermo ou ativo solicitado: {texto_usuario}"
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        if not response.text:
            raise ValueError("Resposta vazia da IA.")
            
        relatorio = response.text
        
        # Trava de segurança contra o erro Message_too_long (corta se passar de 3500 caracteres)
        if len(relatorio) > 3500:
            relatorio = relatorio[:3500] + "\n\n[Relatório resumido por limite de espaço]"
            
        # Remove caracteres especiais para evitar qualquer crash de markdown no Telegram
        relatorio_limpo = relatorio.replace("*", "").replace("_", "").replace("`", "")
        
        mensagem_final = (
            f"RELATÓRIO DE INTELIGÊNCIA ALPHA #VIP\n\n{relatorio_limpo}\n\n"
            f"-----------------------------------\n"
            f"Quer desbloquear o fluxo contínuo e garantir sua vaga definitiva?\n"
            f"Assine agora o acesso completo (R$ 250/mês):\n{LINK_PAGAMENTO_PIX}"
        )
        
        await status_msg.edit_text(mensagem_final)
        
    except Exception as e:
        logger.error(f"ERRO NA GERACAO: {str(e)}")
        await status_msg.edit_text("Ocorreu uma instabilidade ao processar este termo. Tenta mandar novamente.")

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
