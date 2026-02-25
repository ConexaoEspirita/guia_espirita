import streamlit as st
from supabase import create_client
import pandas as pd
import urllib.parse
import unicodedata
import re

# --- CSS unificado para login/cadastro e app principal ---
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);}
.titulo-premium {background: linear-gradient(90deg, #0047AB, #1976D2);-webkit-background-clip: text;-webkit-text-fill-color: transparent;text-shadow: 0 4px 12px rgba(0,71,171,0.3);font-size: 2.5rem !important;font-weight: 800 !important;}
.card-centro {background: rgba(255,255,255,0.95);backdrop-filter: blur(10px);padding: 20px;border-radius: 20px;border: 1px solid rgba(0,71,171,0.1);box-shadow: 0 8px 32px rgba(0,71,171,0.15);margin-bottom: 16px;}
.nome-grande {color: #1E3A8A !important;font-size: 22px !important;font-weight: 800 !important;}
.nome-fantasia {color: #3B82F6 !important;font-size: 15px !important;font-weight: 600 !important;font-style: italic;}
.info-texto {color: #374151 !important;font-size: 13px !important;display: flex;align-items: center;gap: 6px;}
.palestras-verde {color: #10B981 !important; font-weight: 700 !important; font-size: 14px !important; background: rgba(16,185,129,0.15) !important; padding: 8px 14px !important; border-radius: 12px !important; border-left: 4px solid #10B981 !important; box-shadow: 0 2px 8px rgba(16,185,129,0.2) !important;}
div.stButton > button {background: linear-gradient(135deg, #0047AB, #1E40AF) !important;color: white !important;border-radius: 12px !important;height: 50px !important;font-size: 16px !important;font-weight: 700 !important;box-shadow: 0 4px 12px rgba(0,71,171,0.4) !important;transition: all 0.2s !important;}
div.stButton > button:hover {box-shadow: 0 6px 20px rgba(0,71,171,0.6) !important;transform: translateY(-2px) !important;}
div.stButton > button:active {transform: translateY(0px) !important;box-shadow: 0 2px 8px rgba(0,71,171,0.3) !important;}
div[data-testid="stTextInputBlock"] > label > div > small {display: none !important;}
.login-container {background: rgba(255,255,255,0.95);backdrop-filter: blur(10px);padding: 30px;border-radius: 20px;border: 1px solid rgba(0,71,171,0.1);box-shadow: 0 8px 32px rgba(0,71,171,0.15);width: 400px;margin:auto;margin-top:60px;}
.login-title {font-size: 2rem !important;font-weight: 800 !important;color: #1E3A8A !important;text-align: center;margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

# --- Supabase ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- Sessão ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# --- Tela de login/cadastro ---
if not st.session_state.logado:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🕊️ Guia Espírita</div>', unsafe_allow_html=True)
    
    aba = st.radio("Escolha:", ["Login", "Cadastro"], horizontal=True)
    
    if aba == "Login":
        email = st.text_input("", placeholder="📧 Digite seu e-mail", label_visibility="collapsed")
        senha = st.text_input("", placeholder="🔒 Digite sua senha", type="password", label_visibility="collapsed")
        if st.button("🚀 ACESSAR", key="login", use_container_width=True):
            email_limpo = email.strip().lower()
            senha_limpa = senha.strip()
            resposta = supabase.table("acessos").select("*").eq("email", email_limpo).eq("senha", senha_limpa).execute()
            if resposta.data:
                st.session_state.logado = True
                st.session_state.usuario = email_limpo
                st.experimental_rerun()
            else:
                st.error("❌ E-mail ou senha incorretos!")
    
    elif aba == "Cadastro":
        nome = st.text_input("", placeholder="👤 Digite seu nome completo", label_visibility="collapsed")
        email = st.text_input("", placeholder="📧 Digite seu e-mail", label_visibility="collapsed")
        senha = st.text_input("", placeholder="🔒 Crie uma senha", type="password", label_visibility="collapsed")
        senha_conf = st.text_input("", placeholder="🔒 Confirme a senha", type="password", label_visibility="collapsed")
        
        if st.button("📝 CADASTRAR", key="cadastro", use_container_width=True):
            if not nome.strip() or not email.strip() or not senha.strip() or not senha_conf.strip():
                st.error("❌ Todos os campos são obrigatórios!")
            elif senha != senha_conf:
                st.error("❌ Senhas não conferem!")
            else:
                email_limpo = email.strip().lower()
                existe = supabase.table("acessos").select("*").eq("email", email_limpo).execute()
                if existe.data:
                    st.error("❌ E-mail já cadastrado!")
                else:
                    supabase.table("acessos").insert({"nome": nome.strip(), "email": email_limpo, "senha": senha}).execute()
                    st.success("✅ Cadastro realizado! Agora faça login.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Tela principal do app (não mexer em nada) ---
else:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    
    # --- Todo o código de busca e exibição do seu app permanece exatamente como está aqui ---
    
    # --- Botão de logout ---
    col_spacer, col_logout = st.columns([5, 1])
    with col_logout:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logado = False
            st.session_state.usuario = None
            if "tem_busca" in st.session_state:
                del st.session_state.tem_busca
            st.experimental_rerun()
