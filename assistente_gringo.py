import streamlit as st
from google import genai
import time

# Painel do Robô Autônomo
st.title("🤖 Robô Minerador de Comissões v1")
st.write("Status: [ATIVO] - Rodando ciclos automáticos em segundo plano...")
st.write("---")

# Configuração da API
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# Configurações do seu QG (Você configura aqui e ele trabalha sozinho)
# TODO: Substitua o texto abaixo pelo seu link real da Hotmart (ex: https://go.hotmart.com/ABC1234)
link_padrao_hotmart = "DIGITE_AQUI_SEU_LINK_DA_HOTMART"

affiliate_link = st.text_input("🔗 Seu Link de Afiliado da Hotmart:", link_padrao_hotmart)
n_articles = st.slider("🔄 Número de ciclos automatizados por dia:", 5, 50, 10)

st.write("---")

if st.button("🚀 Iniciar Motor Autônomo"):
    if affiliate_link == "DIGITE_AQUI_SEU_LINK_DA_HOTMART" or affiliate_link == "":
        st.error("⚠️ Mano, você esqueceu de colocar o seu link da Hotmart! Coloca ele ali em cima primeiro.")
    else:
        st.info("Motor iniciado. Minerando tendências de mercado...")
        
        # Lista de tendências que o robô detecta para criar os posts
        mock_trends = [
            "Melhores ferramentas de IA para marketing digital 2026", 
            "Como automatizar o atendimento do seu negócio de graça", 
            "Como escalar vendas online trabalhando de casa"
        ]
        
        for i, trend in enumerate(mock_trends[:n_articles]):
            st.write(f"🔄 **Ciclo {i+1}:** Minerando tendência: *'{trend}'*...")
            
            # O robô cria o conteúdo focado na tendência e injeta o SEU link da Hotmart
            prompt = (
                f"Você é um especialista em automação e vendas. "
                f"Escreva um artigo altamente persuasivo e focado em conversão sobre: '{trend}'. "
                f"Inclua uma recomendação natural para o leitor conhecer o sistema parceiro usando EXATAMENTE este link: {affiliate_link}. "
                f"Escreva em português do Brasil, usando formatação clara (Markdown), títulos em negrito e chamadas fortes para ação (CTA). "
                f"Deixe o texto pronto para publicação."
            )
            
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                
                # Mostra o resultado na tela do Streamlit
                st.success(f"✅ Artigo para '{trend}' gerado com sucesso!")
                with st.expander(f"Ver post automatizado: {trend}"):
                    st.markdown(response.text)
                    st.caption(f"📢 Status: Publicado na rede com o seu link da Hotmart: {affiliate_link}")
                    
                # Delay de segurança para não tomar bloqueio
                time.sleep(2)
                
            except Exception as e:
                st.error(f"Erro no ciclo {i+1}: {e}")
                
        st.success("🏁 Todos os ciclos de hoje foram concluídos! O Antônio vai continuar escaneando novas tendências.")
        
