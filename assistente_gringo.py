import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# ==========================================
# 🧠 FUNÇÃO PARA A GEMINI CRIAR A ISCA
# ==========================================
def gerar_proposta_gringo(nome_empresa, ramo, cidade):
    genai_api_key = os.environ.get("GEMINI_API_KEY")
    if not genai_api_key:
        print("🛑 ERRO: Chave da Gemini não encontrada nas configurações da nuvem!")
        return None
    genai.configure(api_key=genai_api_key)
    
    prompt = f"Write a short, casual cold outreach email to a business owner. Business Name: {nome_empresa}, Industry: {ramo}, Location: {cidade}. Offer a chat to guarantee 15 to 20 clients in 30 days. Short, conversational, English. Sign as 'Best regards, Orlando'. Return ONLY 'Subject: [text]' and the body."
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Erro na Gemini: {e}")
        return None

# ==========================================
# 🚀 ENVIAR OS E-MAILS (O MOTOR DA GAIOLA)
# ==========================================
def rodar_disparos_loopeados():
    smtp_server = "smtp.gmail.com"
    port = 587
    email_orlando = "orlandolocalmarketing888@gmail.com"
    senha_app_orlando = "ttezzpnnfgthonmv"
    
    gringos_alvo = [
        {
            "email": "danilogoncalves29167@gmail.com", # Teste pro Danilo
            "empresa": "Miami Elite Auto Repair",
            "ramo": "Auto Repair Shop",
            "cidade": "Miami"
        }
    ]
    
    print("🤖 MOTOR LIGADO! Iniciando disparos...")
    for alvo in gringos_alvo:
        conteudo_gerado = gerar_proposta_gringo(alvo['empresa'], alvo['ramo'], alvo['cidade'])
        if not conteudo_gerado:
            continue
            
        linhas = conteudo_gerado.split('\n')
        assunto = "Quick question"
        corpo_mensagem = conteudo_gerado
        for linha in linhas:
            if linha.startswith("Subject:"):
                assunto = linha.replace("Subject:", "").strip()
                corpo_mensagem = conteudo_gerado.replace(linha, "").strip()
                break

        try:
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()
            server.login(email_orlando, senha_app_orlando)
            msg = MIMEMultipart()
            msg['From'] = email_orlando
            msg['To'] = alvo['email']
            msg['Subject'] = assunto
            msg.attach(MIMEText(corpo_mensagem, 'plain'))
            server.sendmail(email_orlando, alvo['email'], msg.as_string())
            server.quit()
            print(f"✅ SUCESSO! E-mail enviado para: {alvo['email']}")
        except Exception as e:
            print(f"❌ Erro no envio: {e}")
        time.sleep(10)

# ==========================================
# 🌐 SERVIDOR DE MENTIRA (Pra enganar o Render Grátis)
# ==========================================
class ServidorFake(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Robo Ativo e Rodando!")

def rodar_servidor_fake():
    porta = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', porta), ServidorFake)
    print(f"🌐 Servidor fake ativo na porta {porta}")
    server.serve_forever()

if __name__ == "__main__":
    # Liga o robô de e-mails em segundo plano
    threading.Thread(target=rodar_disparos_loopeados, daemon=True).start()
    # Liga o servidor fake para o Render achar que é um site grátis
    rodar_servidor_fake()
                
