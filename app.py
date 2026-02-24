import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

st.markdown("""
<style>
.stApp { 
    background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);
}
.titulo-premium {
    background: linear-gradient(90deg, #0047AB, #1976D2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 4px 12px rgba(0,71,171,0.3);
    font-size: 2.5rem !important;
    font-weight: 800 !important;
}
.card-centro {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 20px;
    border: 1px solid rgba(0,71,171,0.1);
    box-shadow: 0 8px 32px rgba(0,71,171,0.15), 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 16px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.card-centro:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0,71,171,0.25);
}
.card-centro::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #0047AB, #5CACE2, #0047AB);
}
.nome-grande { 
    color: #1E3A8A !important;
    font-size: 22px !important; 
    font-weight: 800 !important; 
    line-height: 1.3;
    margin-bottom: 6px;
}
.nome-fantasia { 
    color: #3B82F6 !important;
    font-size: 15px !important; 
    font-weight: 600 !important; 
    font-style: italic; 
    margin-bottom: 10px;
}
.info-texto { 
    color: #374151 !important;
    font-size: 13px !important; 
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}
div.stLinkButton > a { 
    background: linear-gradient(135deg, #10B981, #059669) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    height: 44px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 16px rgba(16,185,129,0.4) !important;
    transition: all 0.2s ease !important;
}
div.stLinkButton > a:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(16,185,129,0.5) !important;
}
div.stButton > button {
    background: linear-gradient(135deg, #0047AB, #1E40AF) !important;
    color: white !important;
    border-radius: 12px !important;
    height: 48px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 16px rgba(0,71,171,0.4) !important;
}
.conta-pequena { 
    font-size: 12px !important; 
    color: #6B7280 !important; 
    margin-bottom: 12px !important;
    background: rgba(255,255,255,0.7);
    padding: 6px 12px;
    border-radius: 20px;
    display: inline-block;
}

/* RESPONSIVO MOBILE - LETRAS MAIORES NO CELULAR */
@media (max-width: 768px) {
    .nome-grande { 
        font-size: 28px !important;
        line-height: 1.2 !important;
    }
    .nome-fantasia { 
        font-size: 20px !important;
    }
    .info-texto { 
        font-size: 16px !important;
        line-height: 1.4 !important;
        padding: 8px 0 !important;
    }
    .card-centro {
        padding: 24px !important;
        margin-bottom: 20px !important;
    }
    div.stButton > button, div.stLinkButton > a {
        height: 52px !important;
        font-size: 18px !important;
        padding: 0 20px !important;
    }
    div.stTextInput > div > div > input {
        font-size: 18px !important;
        padding: 16px !important;
    }
}

@media (max-width: 480px) {
    .nome-grande { font-size: 26px !important; }
    .nome-fantasia { font-size: 18px !important; }
    .info-texto { font-size: 15px !important; }
    .card-centro { padding: 20px !important; }
}

@media (max-width: 600px) {
    .nome-grande { font-size: 24px !important; }
    .nome-fantasia { font-size: 16px !important; }
    .info-texto { font-size: 14px !important; }
    div.stLinkButton > a { height: 42px !important; font-size: 14px !important; }
}
</style>
""", unsafe_allow_html=True)

# Configuração Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def limpar_busca(texto):
    if pd.isna(texto):
        return ""
    texto = unicodedata.normalize('NFD', str(texto))
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\\w\\s]', ' ', texto.lower())
    return texto.strip()

# Estado inicial
if "logado" not in st.session_state:
    st.session_state.logado = False

# TELA DE LOGIN
if not st.session_state.logado:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        email = st.text_input("📧 E-mail")
    with col2:
        senha = st.text_input("🔒 Senha", type="password")
    
    if st.button("🚀 ACESSAR GUIA", use_container_width=True):
        email_limpo = email.strip().lower()  # ✅ CORREÇÃO DO CELULAR
        senha_limpa = senha.strip()          # ✅ CORREÇÃO DO CELULAR
        
        resposta = supabase.table("acessos").select("*") \
            .eq("email", email_limpo) \
            .eq("senha", senha_limpa) \
            .execute()
            
        if resposta.data:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("❌ E-mail ou senha incorretos!")

# TELA PRINCIPAL (LOGADO)
else:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    
    # Barra de busca
    col_busca, col_botao = st.columns([4, 1])
    with col_busca:
        busca_input = st.text_input("🔍 Procure centros espíritas", 
                                  placeholder="Digite nome, cidade ou dia...", 
                                  label_visibility="collapsed",
                                  value=st.session_state.get("busca", ""))
    with col_botao:
        if st.button("🔎", use_container_width=True):
            if busca_input.strip():
                st.session_state.busca = busca_input.strip()
                st.rerun()
    
    busca = st.session_state.get("busca", "").strip()
    
    if busca:
        try:
            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            if 'Unnamed: 0' in df.columns:
                df =
