import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);}
.titulo-premium {background: linear-gradient(90deg, #0047AB, #1976D2);-webkit-background-clip: text;-webkit-text-fill-color: transparent;text-shadow: 0 4px 12px rgba(0,71,171,0.3);font-size: 2.5rem !important;font-weight: 800 !important;}
.card-centro {background: rgba(255,255,255,0.95);backdrop-filter: blur(10px);padding: 20px;border-radius: 20px;border: 1px solid rgba(0,71,171,0.1);box-shadow: 0 8px 32px rgba(0,71,171,0.15);margin-bottom: 16px;position: relative;}
.nome-grande {color: #1E3A8A !important;font-size: 22px !important;font-weight: 800 !important;}
.nome-fantasia {color: #3B82F6 !important;font-size: 15px !important;font-weight: 600 !important;font-style: italic;}
.info-texto {color: #374151 !important;font-size: 13px !important;display: flex !important;align-items: center !important;gap: 6px !important;padding: 4px 0 !important;margin: 4px 0 !important;}
.palestras-verde {color: #10B981 !important;font-weight: 700 !important;font-size: 14px !important;background: rgba(16,185,129,0.15) !important;padding: 8px 12px !important;border-radius: 12px !important;border-left: 4px solid #10B981 !important;box-shadow: 0 2px 8px rgba(16,185,129,0.2) !important;display: flex !important;align-items: center !important;margin: 8px 0 !important;}
.numero-card {position: absolute !important;bottom: 12px !important;right: 16px !important;top: auto !important;background: rgba(0,71,171,0.8) !important;color: white !important;width: 28px !important;height: 28px !important;border-radius: 50% !important;font-size: 12px !important;font-weight: 700 !important;display: flex !important;align-items: center !important;justify-content: center !important;box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;}
div.stButton > button {background: linear-gradient(135deg, #0047AB, #1E40AF) !important;color: white !important;border-radius: 12px !important;height: 50px !important;font-size: 16px !important;font-weight: 700 !important;box-shadow: 0 4px 12px rgba(0,71,171,0.4) !important;transition: all 0.2s !important;}
div.stButton > button:hover {box-shadow: 0 6px 20px rgba(0,71,171,0.6) !important;transform: translateY(-2px) !important;}
div.stButton > button:active {transform: translateY(0px) !important;box-shadow: 0 2px 8px rgba(0,71,171,0.3) !important;}
div.stLinkButton > a {background: linear-gradient(135deg, #10B981, #059669) !important;color: white !important;border-radius: 12px !important;height: 44px !important;font-size: 15px !important;}
div[data-testid="stTextInputBlock"] > label > div > small {display: none !important;}
div[data-testid="stInfoBlock"] div {display: none !important;}
@media (max-width: 768px) {.nome-grande {font-size: 28px !important;}.nome-fantasia {font-size: 20px !important;}.info-texto {font-size: 16px !important;}.stButton > button {height: 55px !important;font-size: 18px !important;}.numero-card {width: 32px !important;height: 32px !important;font-size: 14px !important;}}
</style>""", unsafe_allow_html=True)

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def limpar_busca(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower().strip()
    texto = re.sub(r'[^a-zA-Z0-9áàâãéêíóôõúç\s]', '', texto)
    return texto

def busca_flexivel(termo, texto_row):
    termo_limpo = limpar_busca(termo)
    texto_limpo = limpar_busca(texto_row)
    
    if termo_limpo in texto_limpo:
        return True
    
    termo_sem_vogais = re.sub(r'[aeiouáéíóú]', '', termo_limpo)
    texto_sem_vogais = re.sub(r'[aeiouáéíóú]', '', texto_limpo)
    
    return termo_sem_vogais in texto_sem_vogais

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        email = st.text_input("📧 E-mail")
    with col2:
        senha = st.text_input("🔒 Senha", type="password")
    
    if st.button("🚀 ACESSAR GUIA", use_container_width=True):
        email_limpo = email.strip().lower()
        senha_limpa = senha.strip()
        resposta = supabase.table("acessos").select("*").eq("email", email_limpo).eq("senha", senha_limpa).execute()
        if resposta.data:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("❌ E-mail ou senha incorretos!")
else:
    st.markdown('<h1 class="titulo-premium">🕊️
