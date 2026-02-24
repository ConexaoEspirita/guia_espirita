import streamlit as st
import pandas as pd
from supabase import create_client

# --- COFRE (COLA OS TEUS TEXTOS DO SUPABASE AQUI) ---
url = "https://fjqowpuzenqraugcmmtp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZqcW93cHV6ZW5xcmF1Z2NtbXRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE4Njk2NzQsImV4cCI6MjA4NzQ0NTY3NH0.otWbLrbW4zYOb8-PCZwHYP9vQIbcWCRP_drXHGwIjzw"
supabase = create_client(url, key)

st.title("🕊️ Guia Espírita")
st.markdown("<style>.stApp { background-color: #F0F8FF; }</style>", unsafe_allow_html=True)

# LOGIN (CONTADOR)
email = st.text_input("E-mail para acesso")
if st.button("ACESSAR GUIA"):
    if email:
        supabase.table("acessos").insert({"email": email}).execute()
        st.success("Acesso registrado!")

# TABELA (OS CENTROS)
try:
    df = pd.read_excel("guia.xlsx")
    st.dataframe(df)
except:
    st.error("Arquivo 'guia.xlsx' não encontrado no Desktop!")
