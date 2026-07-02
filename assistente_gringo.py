import streamlit as st
import google.generativeai as genai

# Título direto na tela
st.title("Global Construction Estimator")
st.write("Professional Technical and Cost Estimation System")
st.write("---")

# Puxa a chave dos secrets
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Caixa de texto
pergunta = st.text_area("Enter project specifications or material requirements:")

# Botão de gerar
if st.button("Generate Estimate Report"):
    if pergunta:
        with st.spinner("Processing..."):
            try:
                # Mudando para o modelo clássico que não aceita erro 404
                model = genai.GenerativeModel('gemini-pro')
                
                response = model.generate_content(
                    f"You are a professional construction estimator. Provide a detailed estimate in English and USD for: {pergunta}"
                )
                st.write("---")
                st.write("### 📋 Estimate Report")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
