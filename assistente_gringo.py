import os
import telebot
from telebot import types
import yt_dlp

TOKEN = "8940439614:AAHYjqmLiicZ6dclPR6sUOXqu1l8g4r-khE"
bot = telebot.TeleBot(TOKEN)

# SEU ID OFICIAL DE PATRÃO CONFIGURADO
ADMIN_ID = 8964511789

usuarios_teste = set()
usuarios_vip = set()

def baixar_midia(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    }
    os.makedirs('downloads', exist_ok=True)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if chat_id == ADMIN_ID:
        bot.send_message(chat_id, "Salve, chefe! O bot tá no teu comando. Manda qualquer link aí que é vapo! 🔥")
        return

    bot.send_message(
        chat_id,
        "Salve, mano! Mande o link de qualquer vídeo do TikTok, Instagram ou YouTube para baixar limpinho, sem marca d'água.\n\n"
        "Você tem **1 teste grátis** agora. Cola pra ver a mágica acontecer! Kkkk"
    )

@bot.message_handler(commands=['vip'])
def dar_vip(message):
    chat_id = message.chat.id
    
    if chat_id != ADMIN_ID:
        bot.send_message(chat_id, "Sai fora, mano! Tu não é o dono da porra toda. Kkkk")
        return
        
    try:
        partes = message.text.split()
        alvo_id = int(partes[1])
        usuarios_vip.add(alvo_id)
        if alvo_id in usuarios_teste:
            usuarios_teste.remove(alvo_id)
        bot.send_message(chat_id, f"Mano, o usuário `{alvo_id}` foi promovido a **VIP MASTER** com sucesso! 🚀")
        bot.send_message(alvo_id, "Opa, chefe! Seu pagamento foi confirmado. Seu acesso VIP tá liberado geral, pode mandar os links sem limite! 🔥")
    except Exception as e:
        bot.send_message(chat_id, "Uso incorreto, mano. Digita assim: `/vip ID_DO_USUARIO`")

@bot.message_handler(func=lambda message: True)
def processar_link(message):
    chat_id = message.chat.id
    url = message.text.strip()

    if chat_id == ADMIN_ID:
        bot.send_message(chat_id, "Baixando para o patrão rapidão...")
        executar_download_e_enviar(chat_id, url)
        return

    if chat_id in usuarios_vip:
        bot.send_message(chat_id, "Baixando tua parada rapidão, VIP...")
        executar_download_e_enviar(chat_id, url)
        return

    if chat_id in usuarios_teste:
        markup = types.InlineKeyboardMarkup()
        btn_pagar = types.InlineKeyboardButton("Pagar R$ 65 e Liberar Geral 🚀", url="https://mpago.la/1psrqrL")
        markup.add(btn_pagar)
        
        bot.send_message(
            chat_id,
            "Opa, irmão! Seu teste grátis já era. Kkkk!\n\n"
            "Para continuar baixando sem limite e sem marca d'água, o investimento é de só **R$ 65 por mês**. Clica no botão abaixo:",
            reply_markup=markup
        )
        return

    usuarios_teste.add(chat_id)
    bot.send_message(chat_id, "Agh, peguei o link! Processando tua marola sem marca d'água, aguenta aí...")
    
    try:
        arquivo = baixar_midia(url)
        with open(arquivo, 'rb') as vid:
            bot.send_video(chat_id, vid, caption="Aí o seu vídeo limpinho, mano! O próximo já é com o passe VIP. Kkkk")
        os.remove(arquivo)
    except Exception as e:
        bot.send_message(chat_id, "Deu ruim nesse link, mano. O TikTok travou aqui.")

def executar_download_e_enviar(chat_id, url):
    try:
        arquivo = baixar_midia(url)
        with open(arquivo, 'rb') as vid:
            bot.send_video(chat_id, vid)
        os.remove(arquivo)
    except:
        bot.send_message(chat_id, "Erro ao baixar o arquivo, mano.")

if __name__ == "__main__":
    print("Robô raiz rodando com disfarce anti-bloqueio...")
    bot.infinity_polling()
