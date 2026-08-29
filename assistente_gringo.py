import os
import threading
from flask import Flask
import telebot
from telebot import types
import yt_dlp

# --- CONFIGURAÇÃO DO MINI SERVIDOR WEB PARA O RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Robô de download rodando 24h na ativa! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
# -------------------------------------------------------

TOKEN = "8940439614:AAHYjqmLiicZ6dclPR6sUOXqu1l8g4r-khE"
bot = telebot.TeleBot(TOKEN)

# SEU ID OFICIAL DE PATRÃO CONFIGURADO
ADMIN_ID = 8964511789

usuarios_teste = set()
usuarios_vip = set()

def baixar_midia(url, extrair_audio=False):
    ydl_opts = {
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': False,  # Permite baixar carrossel de fotos ou playlists se houver
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    }
    
    if extrair_audio:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        ydl_opts['format'] = 'best'

    os.makedirs('downloads', exist_ok=True)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        
        # Se for uma playlist (como carrossel de fotos do TikTok)
        if 'entries' in info:
            arquivos = []
            for entry in info['entries']:
                if entry:
                    filename = ydl.prepare_filename(entry)
                    if extrair_audio:
                        filename = os.path.splitext(filename)[0] + '.mp3'
                    arquivos.append(filename)
            return arquivos
        else:
            filename = ydl.prepare_filename(info)
            if extrair_audio:
                filename = os.path.splitext(filename)[0] + '.mp3'
            return [filename]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if chat_id == ADMIN_ID:
        bot.send_message(chat_id, "Salve, chefe! O bot tá brabo. Manda o link normal para vídeo ou `/audio [link]` para puxar o MP3! 🔥")
        return

    bot.send_message(
        chat_id,
        "Salve, mano! Mande o link de qualquer vídeo do TikTok, Instagram ou YouTube para baixar limpinho.\n\n"
        "💡 **Quer extrair só o áudio?** Mande o comando `/audio` seguido do link.\n\n"
        "Você tem **1 teste grátis** agora. Cola pra ver a mágica acontecer! Kkkk"
    )

@bot.message_handler(commands=['audio'])
def baixar_audio_cmd(message):
    chat_id = message.chat.id
    partes = message.text.split(maxsplit=1)
    
    if len(partes) < 2:
        bot.send_message(chat_id, "E o link, viado? Digita assim: `/audio SEU_LINK_AQUI`")
        return
        
    url = partes[1].strip()
    
    if chat_id != ADMIN_ID and chat_id not in usuarios_vip and chat_id in usuarios_teste:
        bot.send_message(chat_id, "Seu teste grátis já era, mano! Assina o VIP para continuar puxando áudio.")
        return

    bot.send_message(chat_id, "Buscando e convertendo o áudio na marra, aguenta aí...")
    
    try:
        arquivos = baixar_midia(url, extrair_audio=True)
        for arq in arquivos:
            if os.path.exists(arq):
                with open(arq, 'rb') as aud:
                    bot.send_audio(chat_id, aud, caption="Aí o teu MP3 estralando, mano! 🎵")
                os.remove(arq)
        if chat_id not in usuarios_vip and chat_id != ADMIN_ID:
            usuarios_teste.add(chat_id)
    except Exception as e:
        bot.send_message(chat_id, "Deu ruim para puxar esse áudio, mano. O link pode estar quebrado.")

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
        bot.send_message(chat_id, "Baixando mídia para o patrão...")
        executar_download_e_enviar(chat_id, url)
        return

    if chat_id in usuarios_vip:
        bot.send_message(chat_id, "Baixando tua parada, VIP...")
        executar_download_e_enviar(chat_id, url)
        return

    if chat_id in usuarios_teste:
        markup = types.InlineKeyboardMarkup()
        btn_pagar = types.InlineKeyboardButton("Pagar R$ 65 e Liberar Geral 🚀", url="https://mpago.la/1psrqrL")
        markup.add(btn_pagar)
        
        bot.send_message(
            chat_id,
            "Opa, irmão! Seu teste grátis já era. Kkkk!\n\n"
            "Para continuar baixando sem limite, o investimento é de só **R$ 65 por mês**. Clica no botão abaixo:",
            reply_markup=markup
        )
        return

    usuarios_teste.add(chat_id)
    bot.send_message(chat_id, "Agh, peguei o link! Processando a marola sem marca d'água...")
    
    executar_download_e_enviar(chat_id, url)

def executar_download_e_enviar(chat_id, url):
    try:
        arquivos = baixar_midia(url, extrair_audio=False)
        for arq in arquivos:
            if os.path.exists(arq):
                # Se for foto (carrossel do TikTok)
                if arq.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    with open(arq, 'foto') as f:
                        bot.send_photo(chat_id, f)
                else:
                    with open(arq, 'rb') as vid:
                        bot.send_video(chat_id, vid, caption="Aí o seu vídeo limpinho, mano! 🚀")
                os.remove(arq)
    except Exception as e:
        bot.send_message(chat_id, "Deu ruim nesse link, mano. O servidor bloqueou ou a mídia não existe.")

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.start()
    
    print("Robô pelão e blindado rodando com Flask e FFmpeg na ativa...")
    bot.infinity_polling()
