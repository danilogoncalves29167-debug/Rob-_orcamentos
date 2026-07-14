import os
import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()

# ==========================================
# 🔑 CONFIGURAÇÕES E TRAVAS
# ==========================================
# Lista de Tokens Ativos (gringos que pagaram $30)
TOKENS_ATIVOS = {"PREMIUM_GRINGO_123", "MATEIRO_SUCESSO_2026"}

# Controle de uso gratuito por IP (limite de 3 envios de graça)
historico_gratis = {}

# ==========================================
# 🧠 FUNÇÃO DA GEMINI
# ==========================================
def gerar_proposta_gringo(nome_empresa, ramo, cidade, sender_name):
    genai_api_key = os.environ.get("GEMINI_API_KEY")
    if not genai_api_key:
        return "Error: Gemini API Key missing."
    
    genai.configure(api_key=genai_api_key)
    prompt = (
        f"Write a short, casual cold outreach email to a business owner. "
        f"Business Name: {nome_empresa}, Industry: {ramo}, Location: {cidade}. "
        f"Offer a chat to guarantee 15 to 20 clients in 30 days. "
        f"Short, conversational, English. Sign as 'Best regards, {sender_name}'. "
        f"Return ONLY 'Subject: [text]' and the body."
    )
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# 📬 MOTOR DE DISPARO (Roda com os dados do Gringo)
# ==========================================
def enviar_email_async(sender_email, sender_password, destinatario, assunto, corpo):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo, 'plain'))
        
        server.sendmail(sender_email, destinatario, msg.as_string())
        server.quit()
        print(f"✅ SUCESSO! E-mail enviado por {sender_email} para: {destinatario}")
    except Exception as e:
        print(f"❌ Erro no envio de {sender_email} para {destinatario}: {e}")

# ==========================================
# 🎨 INTERFACE WEB (HTML Embutido e Atualizado)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Cold Outreach Generator & Sender</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen flex flex-col items-center justify-center p-4">
    <div class="max-w-md w-full bg-gray-800 p-8 rounded-xl shadow-2xl border border-gray-700 my-8">
        <h1 class="text-2xl font-bold text-center mb-2 text-indigo-400">🚀 AI Cold Outreach</h1>
        <p class="text-gray-400 text-xs text-center mb-6">Connect your Gmail, generate personalized emails with AI, and send them instantly.</p>
        
        <form action="/send" method="post" class="space-y-4">
            <!-- Configurações do Remetente (O Gringo) -->
            <div class="p-4 bg-gray-900/50 rounded-lg border border-gray-700/50 space-y-3">
                <h3 class="text-xs font-bold text-indigo-400 uppercase tracking-wider">Your Sender Config</h3>
                <div>
                    <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">Your Gmail</label>
                    <input type="email" name="sender_email" required class="w-full p-2 bg-gray-900 rounded border border-gray-700 focus:outline-none focus:border-indigo-500 text-xs text-white" placeholder="yourname@gmail.com">
                </div>
                <div>
                    <div class="flex justify-between items-center mb-1">
                        <label class="block text-xs font-semibold text-gray-400 uppercase">App Password</label>
                        <a href="https://support.google.com/accounts/answer/185833" target="_blank" class="text-[10px] text-indigo-400 hover:underline">How to generate?</a>
                    </div>
                    <input type="password" name="sender_password" required class="w-full p-2 bg-gray-900 rounded border border-gray-700 focus:outline-none focus:border-indigo-500 text-xs text-white" placeholder="xxxx xxxx xxxx xxxx">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">Your Name / Agency</label>
                    <input type="text" name="sender_name" required class="w-full p-2 bg-gray-900 rounded border border-gray-700 focus:outline-none focus:border-indigo-500 text-xs text-white" placeholder="John from PixelMedia">
                </div>
            </div>

            <!-- Dados do Lead -->
            <div class="space-y-3">
                <h3 class="text-xs font-bold text-indigo-400 uppercase tracking-wider">Target Lead Details</h3>
                <div>
                    <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">Target Client Email</label>
                    <input type="email" name="target_email" required class="w-full p-2 bg-gray-900 rounded border border-gray-700 focus:outline-none focus:border-indigo-500 text-xs text-white" placeholder="owner@miamiautorepair.com">
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">Business Name</label>
                        <input type="text" name="empresa" required class="w-full p-2 bg-gray-900 rounded border border-gray-700 focus:outline-none focus:border-indigo-500 text-xs text-white" placeholder="Miami Auto Repair">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">Industry / Niche</label>
                        <input type="text" name="ramo" required class="w-full p-2 bg-gray-900 rounded border border-gray-700 focus:outline-none focus:border-indigo-500 text-xs text-white" placeholder="Auto Repair Shop">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">Location / City</label>
                    <input type="text" name="cidade" required class="w-full p-2 bg-gray-900 rounded border border-gray-700 focus:outline-none focus:border-indigo-500 text-xs text-white" placeholder="Miami, FL">
                </div>
            </div>

            <!-- Token -->
            <div>
                <label class="block text-xs font-semibold text-gray-400 uppercase mb-1">Access Token (Required after 3 free campaigns)</label>
                <input type="text" name="token" class="w-full p-2 bg-gray-900 rounded border border-gray-700 focus:outline-none focus:border-indigo-500 text-xs text-white" placeholder="Enter your paid token here">
            </div>
            
            <button type="submit" class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 rounded font-semibold transition duration-200 text-sm">Generate & Send Email ⚡</button>
        </form>

        {% if error %}
        <div class="mt-6 p-4 bg-red-950 border border-red-800 rounded text-red-200 text-xs">
            <strong>Access Denied:</strong> {{ error }}
            <br><br>
            <a href="mailto:orlandolocalmarketing888@gmail.com" class="text-indigo-400 underline font-semibold">Subscribe now for $30/month</a> to unlock unlimited campaigns.
        </div>
        {% endif %}

        {% if success %}
        <div class="mt-6 p-4 bg-emerald-950 border border-emerald-800 rounded text-emerald-200 text-xs">
            <strong>Success!</strong> {{ success }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

# ==========================================
# 🛣️ ROTAS DO SERVIDOR
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_TEMPLATE

@app.post("/send", response_class=HTMLResponse)
async def send_email_campaign(
    request: Request, 
    sender_email: str = Form(...),
    sender_password: str = Form(...),
    sender_name: str = Form(...),
    target_email: str = Form(...), 
    empresa: str = Form(...), 
    ramo: str = Form(...), 
    cidade: str = Form(...), 
    token: str = Form(None)
):
    client_ip = request.client.host
    token_valido = token in TOKENS_ATIVOS
    
    # Limpa possíveis espaços que o gringo digite na senha de app
    clean_password = sender_password.replace(" ", "")

    # Validação do Limite Grátis
    if not token_valido:
        usos = historico_gratis.get(client_ip, 0)
        if usos >= 3:
            error_msg = "You have reached your limit of 3 free email campaigns. Please purchase an Access Token to unlock unlimited usage."
            return HTML_TEMPLATE.replace("{% if error %}", "").replace("{{ error }}", error_msg).replace("{% endif %}", "").replace("{% if success %}", "<!--").replace("{% endif %}", "-->")
        
        # Contabiliza o uso grátis
        historico_gratis[client_ip] = usos + 1

    # 1. Gera o conteúdo usando a inteligência artificial do Gemini
    conteudo_gerado = gerar_proposta_gringo(empresa, ramo, cidade, sender_name)
    
    if "Error" in conteudo_gerado:
        error_msg = f"Failed to generate email content: {conteudo_gerado}"
        return HTML_TEMPLATE.replace("{% if error %}", "").replace("{{ error }}", error_msg).replace("{% endif %}", "").replace("{% if success %}", "<!--").replace("{% endif %}", "-->")

    # 2. Separa o Assunto do Corpo da mensagem
    linhas = conteudo_gerado.split('\n')
    assunto = "Quick question"
    corpo_mensagem = conteudo_gerado
    for linha in linhas:
        if linha.startswith("Subject:"):
            assunto = linha.replace("Subject:", "").strip()
            corpo_mensagem = conteudo_gerado.replace(linha, "").strip()
            break

    # 3. Dispara o e-mail em segundo plano usando a conta do próprio gringo
    threading.Thread(
        target=enviar_email_async, 
        args=(sender_email, clean_password, target_email, assunto, corpo_mensagem), 
        daemon=True
    ).start()

    success_msg = f"Email campaign successfully generated and scheduled! Sent from {sender_email} to {target_email}."
    return HTML_TEMPLATE.replace("{% if success %}", "").replace("{{ success }}", success_msg).replace("{% endif %}", "").replace("{% if error %}", "<!--").replace("{% endif %}", "-->")
    
