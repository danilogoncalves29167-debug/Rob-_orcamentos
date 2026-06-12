import streamlit as st
from google import genai

st.set_page_config(page_title="Sistema Orçamentista Inteligente", page_icon="🤖", layout="centered")

st.title("🤖  Inteligência Orçamentária Avançada")
st.subheader("Gere orçamentos e relatórios técnicos em segundos")
st.write("---")

# Configuração segura da chave usando os Segredos do Streamlit
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

pergunta = st.text_area("Digite as especificações da obra ou usina para calcular:", 
                        placeholder="Ex: Preciso do orçamento completo de materiais e mão de obra para um galpão de alvenaria de 200m²...")

if st.button("📊  GERAR ORÇAMENTO IMEDIATO"):
    if pergunta.strip():
        with st.spinner("A Inteligência está calculando os custos e margens... Aguarde."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=pergunta,
                )
                st.success("✅  Orçamento Gerado com Sucesso!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro na conexão com o servidor: {e}")
    else:
        st.warning("Por favor, digite alguma informação sobre a obra antes de calcular.")

st.write("---")
st.caption("© Sistema Privado de Inteligência Artificial - Licença Exclusiva Corporativa.")
