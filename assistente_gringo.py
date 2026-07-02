import streamlit as st
import google.generativeai as genai

# Configuração da página profissional
st.set_page_config(
    page_title="Global Construction Estimator",
    page_layout="centered"
)

# Título limpo e profissional
st.title("Global Construction Estimator")
st.markdown("##### Professional Technical and Cost Estimation System")
st.write("---")

# Configuração segura da chave usando os Secrets nos bastidores
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Área de entrada direta e sem enrolação
pergunta = st.text_area("Enter project specifications or material requirements:", 
                        placeholder="e.g., Provide a cost estimate for a 2,500 sq ft residential build...",
                        height=150)

# Botão de ação direto
if st.button("Generate Estimate Report", use_container_width=True):
    if pergunta.strip():
        with st.spinner("Processing calculations..."):
            try:
                # Usando o modelo estável para o sistema funcionar direto
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                system_instruction = """
                You are a Professional Construction Estimator.
                Provide a structured, technical cost and material estimation based on the user's input.
                
                RULES:
                1. Always respond in English.
                2. Structure the report clearly: Summary, Estimated Materials, Labor, and Contingency.
                3. Use standard international metrics and USD currency.
                4. End with a professional engineering disclaimer.
                """
                
                response = model.generate_content(
                    f"{system_instruction}\n\nUser Request: {pergunta}"
                )
                
                st.write("---")
                st.write("### 📋 Estimate Report")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"System temporarily unavailable. Please try again. [Details: {e}]")
    else:
        st.warning("Please enter project details first.")

# Rodapé corporativo padrão
st.write("---")
st.markdown("<div style='text-align: center; color: #777; font-size: 0.8rem;'>Global Construction Estimator © All Rights Reserved</div>", unsafe_allow_with_html=True)

