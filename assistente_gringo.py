# -*- coding: utf-8 -*-
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

# Servidor Flask falso apenas para abrir a porta que o Render exige
app = Flask(__name__)

@app.route('/')
def home():
    return "Alpha Club Bot está operando na escuta."

def run_flask():
    porta = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=porta)

# CONFIGURAÇÕES DO BOT E DO PAGAMENTO
TELEGRAM_BOT_TOKEN = "8905719627:AAEkdRBkweO-62u_td0jyKfTZYaxGQNZNI0"
LINK_PAGAMENTO_PIX = "https://mpago.la/1psrqrL"
MEU_TOKEN_MESTRE = "8964511789"

testes_usuarios = {}

# Inicializa o cliente do Google Gemini usando a variável de ambiente gratuita
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    termo_consentimento = (
        "🔒 **TERMOS DE USO E ISENÇÃO DE RESPONSABILIDADE - ALPHA CLUB**\n\n"
        "Ao interagir com este sistema, você declara expressamente que leu, compreendeu e concorda "
        "com os nossos Termos de Serviço e Política de Isenção de Responsabilidade (Conforme Art. 427 do Código Civil).\n\n"
        "1. As informações, relatórios e análises geradas por este bot possuem caráter estritamente educacional, "
        "teórico e de simulação macroeconômica, não constituindo recomendação de investimento, consultoria financeira "
        "ou oferta de ativos.\n"
        "2. Os desenvolvedores e operadores do sistema não se responsabilizam por quaisquer perdas financeiras, "
        "tomadas de decisão ou resultados obtidos pelo usuário.\n\n"
        "⚖️ *Ao enviar qualquer termo ou continuar a conversa, você concorda integralmente com estes termos.*\n\n"
        "--- \n\n"
        "Bem-vindo à Matriz de Assimetria Alpha. Envie qualquer termo macroeconômico ou ativo para gerar sua análise executiva inicial de teste."
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
                f"🚨 **ACESSO DE TESTE ESGOTADO** 🚨\n\n"
                f"Sua triagem gratuita expirou. Para continuar recebendo os relatórios semanais de assimetria de mercado e manter seu status no clube exclusivo por R$ 250 mensais, efetue a assinatura:\n\n"
                f"{LINK_PAGAMENTO_PIX}"
            )
            return

    status_msg = await update.message.reply_text("📊 Processando matriz de liquidez sistêmica, cruzando dados de tendência e estruturando o relatório completo... Aguarde.")

    prompt = (
        "Aja como um analista sênior brasileiro de mercado financeiro, focado em educação econômica, "
        "macroeconomia e comportamento de ativos globais. Escreva um relatório técnico de grande porte, "
        "bem estruturado e didático em português do Brasil, explicando o contexto, a dinâmica de oferta e demanda, "
        "os reflexos na economia e os cenários futuros de forma profissional. O texto deve ser enriquecedor, "
        "fazendo o leitor sentir que obteve uma aula de altíssimo nível. Mantenha o foco estritamente educacional e analítico."
        f"\n\nTermo ou ativo solicitado pelo usuário: {texto_usuario}"
    )
    
    try:
        # Chamada corrigida usando o modelo oficial suportado pelo SDK atual do Google GenAI
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        if not response.text:
            raise ValueError("Resposta vazia da IA.")
            
        relatorio = response.text
        mensagem_final = (
            f"📈 **RELATÓRIO DE INTELIGÊNCIA ALPHA #VIP** 📈\n\n{relatorio}\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *Quer desbloquear o fluxo contínuo e garantir sua vaga definitiva no clube?*\n"
            f"Assine agora o acesso completo (R$ 250/mês):\n{LINK_PAGAMENTO_PIX}"
        )
        
        await status_msg.delete()
        
        if len(mensagem_final) > 4000:
            for i in range(0, len(mensagem_final), 4000):
                await update.message.reply_text(mensagem_final[i:i+4000], parse_mode="Markdown")
        else:
            await update.message.reply_text(mensagem_final, parse_mode="Markdown")
        
    except Exception as e:
        print(f"ERRO NA GERACAO: {str(e)}")
        await status_msg.edit_text("❌ Ocorreu um pico de instabilidade na matriz ao processar este termo. Tenta mandar novamente.")

bot_app.add_handler(CommandHandler("start", start_command))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    t_flask = threading.Thread(target=run_flask)
    t_flask.start()
    
    print("Servidor web falso ativo e bot de Telegram rodando com Gemini...")
    bot_app.run_polling(drop_pending_updates=True)
    
