import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai
import os
import time

# ==========================================
# 🧠 FUNÇÃO PARA A GEMINI CRIAR A ISCA EM INGLÊS
# ==========================================
def gerar_proposta_gringo(nome_empresa, ramo, cidade):
    """
    Usa a Gemini para criar um e-mail de abordagem único em inglês.
    """
    # Pega a chave da Gemini configurada na nuvem
    genai_api_key = os.environ.get("GEMINI_API_KEY")
    if not genai_api_key:
        print("🛑 ERRO: Chave da Gemini não encontrada nas configurações da nuvem!")
        return None
        
    genai.configure(api_key=genai_api_key)
    
    prompt = f"""
    You are a professional B2B sales expert. Write a cold outreach email to a business owner.
    Business Name: {nome_empresa}
    Industry: {ramo}
    Location: {cidade}
    
    Guidelines:
    1. The email must be written in natural, fluent English.
    2. Keep it short, direct, and conversational (not stiff or overly formal).
    3. Point out that they are missing local clients due to an unoptimized Google page and lack of an automated booking system.
    4. Offer a powerful hook: a text chat to show how to guarantee 15 to 20 new clients in the next 30 days.
    5. Signature should be just 'Best regards, Orlando'.
    6. Return ONLY the subject line and the email body. Do not include any notes or explanations.
    Format your response exactly like this:
    Subject: [Subject here]
    
    [Body here]
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Erro ao gerar texto na Gemini: {e}")
        return None

# ==========================================
# 🚀 FUNÇÃO PRINCIPAL DO SEU ROBÔ ORIGINAL
# ==========================================
def enviar_robo_inteligente():
    # 1. Configurações de Conexão (Suas configurações originais do 4G)
    smtp_server = "smtp.gmail.com"
    port = 587
    
    # 2. Credenciais com a Senha de App que você gerou!
    email_orlando = "orlandolocalmarketing888@gmail.com"
    senha_app_orlando = "ttezzpnnfgthonmv" 
    
    # 📋 LISTA DE ALVOS (Dados do gringo para o Robô Caçador)
    gringos_alvo = [
        {
            "email": "danilogoncalves29167@gmail.com", # Mandando pro Danilo para testar se chega bonito!
            "empresa": "Miami Elite Auto Repair",
            "ramo": "Auto Repair Shop",
            "cidade": "Miami"
        }
    ]
    
    print("🤖 O MOTOR DA GAIOLA TÁ LIGADO! Preparando envio com inteligência na Nuvem...")

    for alvo in gringos_alvo:
        print(f"\n🔎 Puxando cérebro da Gemini para analisar: {alvo['empresa']}...")
        
        # Chama a Gemini para criar o texto com base no gringo da vez
        conteudo_gerado = gerar_proposta_gringo(alvo['empresa'], alvo['ramo'], alvo['cidade'])
        
        if not conteudo_gerado:
            print("⚠️ Pulando envio desse alvo devido a erro na IA.")
            continue
            
        # Separa o Assunto do Corpo que a IA criou
        linhas = conteudo_gerado.split('\n')
        assunto = "Quick question"
        corpo_mensagem = conteudo_gerado
        
        for linha in linhas:
            if linha.startswith("Subject:"):
                assunto = linha.replace("Subject:", "").strip()
                corpo_mensagem = conteudo_gerado.replace(linha, "").strip()
                break

        try:
            # Conexão segura na nuvem igualzinha à do seu 4G
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()
            server.login(email_orlando, senha_app_orlando)
            
            msg = MIMEMultipart()
            msg['From'] = email_orlando
            msg['To'] = alvo['email']
            msg['Subject'] = assunto
            msg.attach(MIMEText(corpo_mensagem, 'plain'))
            
            # Enviar de fato
            server.sendmail(email_orlando, alvo['email'], msg.as_string())
            server.quit()
            
            print(f"✅ SUCESSO ABSOLUTO! E-mail enviado com sucesso para: {alvo['email']}")
            
        except Exception as e:
            print(f"❌ Erro inesperado ao enviar para {alvo['email']}: {e}")
            
        # Delay de segurança anti-spam de 10 segundos para esse teste na nuvem
        time.sleep(10)

if __name__ == "__main__":
    enviar_robo_inteligente()
    
