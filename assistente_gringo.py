import os
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI

# CONFIGURAÇÕES DO BOT E DO PAGAMENTO
TELEGRAM_BOT_TOKEN = "8905719627:AAEkdRBkweO-62u_td0jyKfTZYaxGQNZNI0"
OPENAI_API_KEY =
LINK_PAGAMENTO_PIX = "https://mpago.la/1psrqrL"
MEU_TOKEN_MESTRE = "8964511789"

testes_usuarios = {}

client = OpenAI(api_key=OPENAI_API_KEY)
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

    status_msg = await update.message.reply_text("📊 Processando matriz de liquidez sistêmica e cruzando dados de tendência... Aguarde.")

    prompt = (
        "Aja como um analista sênior de um fundo de investimento global de Nova York. "
        "Escreva um relatório macroeconômico de 4 parágrafos extremamente técnico, "
        "densamente recheado com jargões financeiros avançados (como fluxo de capital alavancado, "
        "assimetria de mercado, liquidez sistêmica, macro-hedge e descorrelação de ativos), "
        "mas sem revelar nenhuma fórmula prática, operacional ou passo a passo que o leitor possa executar. "
        "O tom deve ser intimidador, exclusivo, elitista e focado em 'tendências ocultas'."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        relatorio = response.choices[0].message.content
        mensagem_final = (
            f"📈 **RELATÓRIO DE INTELIGÊNCIA ALPHA #VIP** 📈\n\n{relatorio}\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *Quer desbloquear o fluxo contínuo e garantir sua vaga definitiva no clube?*\n"
            f"Assine agora o acesso completo (R$ 250/mês):\n{LINK_PAGAMENTO_PIX}"
        )
        
        await status_msg.delete()
        await update.message.reply_text(mensagem_final, parse_mode="Markdown")
        
    except Exception as e:
        await status_msg.edit_text("❌ Deu pau na geração da matriz. Tenta mandar outro termo.")

bot_app.add_handler(CommandHandler("start", start_command))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("Bot 1 a 1 com termos e link de pagamento rodando no talo...")
    bot_app.run_polling()
