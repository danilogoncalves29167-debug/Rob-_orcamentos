import streamlit as st
from google import genai
import time

# Painel do Robô Autônomo - MODO PIRATA GLOBO
st.set_page_config(page_title="Robô Minerador CPA", page_icon="🤖", layout="centered")

st.title("🤖 Robô Minerador de Comissões v2.0")
st.write("Status: [ATIVO] - Focado em extrair dólares de gringos otários 🇺🇸 🇬🇧")
st.write("---")

# Configuração da API
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# Configurações do seu QG para CPA (OGAds / CPAGrip)
link_padrao_cpa = "DIGITE_AQUI_SEU_LINK_DE_CPA"

cpa_link = st.text_input("🔗 Seu Link de Oferta CPA (OGAds / CPAGrip):", link_padrao_cpa)

# Seleção do Alvo (Onde a grana tá bombando hoje em 2026)
nicho_alvo = st.selectbox(
    "🎯 Escolha a Isca (Nicho Atualizado 2026):",
    ["Brawl Stars (Free Gems Cheat)", "Roblox (Free Robux Generator)", "TikTok Premium App Mod"]
)

n_copies = st.slider("🔄 Quantas variações de copy gerar por ciclo:", 3, 15, 5)

st.write("---")

if st.button("🚀 Iniciar Motor de Atração (CPA)"):
    if cpa_link == "DIGITE_AQUI_SEU_LINK_DE_CPA" or cpa_link == "":
        st.error("⚠️ Mano, você esqueceu de colocar o seu link de CPA! Pega lá na OGAds ou CPAGrip e cola aí.")
    else:
        st.info(f"Motor iniciado. Gerando iscas altamente viciantes para o nicho: {nicho_alvo}...")
        
        # O prompt agora ensina a IA a agir como um adolescente americano em fóruns/redes sociais
        prompt = (
            f"You are a tech-savvy 16-year-old American teenager posting on Twitter, TikTok comments, and Reddit. "
            f"Write {n_copies} different short, punchy, and highly persuasive social media comments/posts "
            f"convincing other kids that you found a working, undetected exploit/glitch to get free stuff for '{nicho_alvo}'.\n\n"
            f"CRITICAL RULES:\n"
            f"1. Use current US teen slang (e.g., 'no cap', 'fr fr', 'it actually worked', 'goated', 'bruh', 'blessed').\n"
            f"2. Keep them short (under 280 characters each) so they look natural, like real comments.\n"
            f"3. Include the tracking link naturally in every single copy: {cpa_link}\n"
            f"4. Do NOT sound like an ad or a salesman. Sound like a hyped kid who just got lucky.\n"
            f"5. Separate each copy clearly with numbers."
        )
        
        try:
            # Usando o mesmo modelo 2.5-flash que você configurou
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            st.success("✅ Iscas em inglês geradas com sucesso!")
            
            st.write("### 📥 Só copiar e bombardear na gringa:")
            st.markdown(response.text)
            
            st.write("---")
            st.caption("💡 **Dica de Pirata:** Vá nos vídeos mais recentes do YouTube/TikTok sobre esse jogo na gringa ou busque por tweets recentes e jogue essas copies nos comentários. Deixa o robô trabalhar!")
            
        except Exception as e:
            st.error(f"Erro no processador da IA: {e}")
            
        
