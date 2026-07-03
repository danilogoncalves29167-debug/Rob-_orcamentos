import streamlit as st
from google import genai

# Título do sistema
st.title("Global Construction Estimator")
st.write("Professional Technical and Cost Estimation System")
st.write("---")

# Configuração da chave usando a biblioteca moderna
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# Caixa de texto
pergunta = st.text_area("Enter project specifications or material requirements:")

# Botão de gerar
if st.button("Generate Estimate Report"):
    if pergunta:
        with st.spinner("Processing..."):
            try:
                response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"You are a professional construction estimator. Provide a detailed estimate in English and USD for: {pergunta}. DO NOT use LaTeX formatting or math symbols like '/sqft+' in the text. Write all calculations and units using plain text only."
                )
                
                st.write("---")
                st.write("### 📋 Estimate Report")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
