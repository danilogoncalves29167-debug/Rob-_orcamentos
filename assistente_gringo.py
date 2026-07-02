import streamlit as st
from google import genai
from google.genai import types

# Configuração da página em inglês para o mercado gringo
st.set_page_config(page_title="AI Budget & Estimate System", page_icon="🤖", layout="centered")

st.title("🤖 Advanced AI Estimation System")
st.subheader("Generate professional construction and technical estimates in seconds")
st.write("---")

# Configuração segura da chave usando os Segredos do Streamlit
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# Placeholder com exemplos internacionais (ex: sq ft, commercial building)
pergunta = st.text_area("Enter the project specifications or material requirements:", 
                        placeholder="Ex: I need a complete cost estimate for labor and materials for a 2,000 sq ft concrete block warehouse...")

if st.button("📊 GENERATE IMMEDIATE ESTIMATE"):
    if pergunta.strip():
        with st.spinner("The AI is calculating costs, local rates, and margins... Please wait."):
            try:
                # Criando uma instrução de sistema para o robô agir como um orçamentista internacional
                system_instruction = """
                You are an expert international construction estimator and cost analyst. 
                Your job is to provide detailed, professional, and structured cost estimates based on the user's request.
                
                Guidelines:
                1. If the user does not specify a country, default to US standards (currency in USD $, measurements in square feet, inches, yards, etc.).
                2. Breakdown the estimate into: Material Costs, Labor Costs, Equipment, and Estimated Timeline/Margin.
                3. Include a disclaimer that estimates are based on market averages and should be verified locally.
                4. Keep a highly professional, corporate technical tone.
                5. Always reply in English (or the language specified by the client request).
                """

                # Rodando o modelo com a instrução do sistema embutida
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=pergunta,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.3 # Temperatura mais baixa para o cálculo ser mais preciso e menos "criativo"
                    )
                )
                st.success("✅ Estimate Generated Successfully!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Server connection error: {e}")
    else:
        st.warning("Please enter some project details before generating the estimate.")

st.write("---")
st.caption("© Private Enterprise Artificial Intelligence System - Exclusive Corporate License.")
