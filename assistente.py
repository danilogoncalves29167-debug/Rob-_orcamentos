import streamlit as st
from google import genai

st.set_page_config(page_title="Smart Construction Estimator", page_icon="🤖", layout="centered")

st.title("🤖 Advanced Budget & Estimation AI")
st.subheader("Generate technical cost estimates and reports in seconds")
st.write("---")

# Secure API Key configuration using Streamlit Secrets
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

pergunta = st.text_area("Enter the project specifications or blueprints data to calculate:", 
                        placeholder="e.g., I need a complete bill of materials and labor cost estimation for a 2,000 sq ft brick warehouse...")

if st.button("📊 GENERATE INSTANT ESTIMATE"):
    if pergunta.strip():
        with st.spinner("AI is calculating costs, materials, and margins... Please wait."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=pergunta,
                )
                st.success("✅ Estimate Generated Successfully!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Server connection error: {e}")
    else:
        st.warning("Please enter some project specifications before calculating.")

st.write("---")
st.caption("© Private Artificial Intelligence System - Exclusive Corporate License.")
