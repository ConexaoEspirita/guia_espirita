import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS Limpo e Responsivo - TARJA BRANCA REMOVIDA ---
st.markdown("""
<style>
/* Remove TARJA BRANCA e espaços estranhos */
.block-container { 
    padding-top: 0rem !important; 
    padding-right: 0 !important;
    padding-left: 0 !important;
    margin: 0 !important;
}
[data-testid="stDecoration"] { display: none !important; }
.stApp > div > div { background: transparent !important; }

.stApp { background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%); }

.titulo-premium { 
    background: linear-gradient(90deg, #0047AB, #1976D2);
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent;
    text-shadow: 0 4px 12px rgba(0,71,171,0.3);
    font-size: 2.8rem !important; 
    font-weight: 800 !important; 
    margin: 0; 
    line-height: 1.1 !important;
    text-align: center;
}

.login-title { 
    font-size: 2.8rem !important; 
    font-weight: 800 !important; 
    color: #1E3A8A !important; 
    text-align: center; 
    margin-bottom: 20px;
    line-height: 1.1 !important;
}

.card-centro { 
    background: rgba(255,255,255,0.95); 
    backdrop-filter: blur(10px);
    padding: 20px; 
    border-radius: 20px; 
    border: 1px solid rgba(0,71,171,0.1);
    box-shadow: 0 8px 32px rgba(0,71,171,0.15); 
    margin-bottom: 16px; 
}

.nome-grande { 
    color: #1E3A8A !important; 
    font-size: 22px !important; 
    font-weight: 800 !important; 
}

.nome-fantasia { 
    color: #3B82F6 !important; 
    font-size: 15px !important; 
    font-weight: 600 !important; 
    font-style: italic; 
}

.info-texto { 
    color: #374151 !important; 
    font-size: 13px !important; 
    display: flex; 
    align-items: center; 
    gap: 6px; 
}

.palestras-verde { 
    color: #10B981 !important; 
    font-weight: 700 !important; 
    font-size: 14px !important; 
    background: rgba(16,185,129,0.15) !important;
    padding: 8px 14px !important; 
    border-radius: 12px !important; 
    border-left: 4px solid #10B981 !important; 
    box-shadow: 0 2px 8px rgba(16,185,129,0.2) !important; 
}

div.stButton > button { 
    background: linear-gradient(135deg, #0047AB, #1E40AF) !important; 
    color: white !important;
    border-radius: 12px !important; 
    height: 50px !important; 
    font-size: 16px !important; 
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(0,71,171,0.4) !important; 
    transition: all 0.2s !important; 
}

div.stButton > button:hover { 
    box-shadow: 0 6px 20px rgba(0,71,171,0.6) !important; 
    transform: translateY(-2px) !important; 
}

div.stButton > button:active { 
    transform: translateY(0px) !important; 
    box-shadow: 0 2px 8px rgba(0,71,171,0.3) !important; 
}

.login-container { 
    max-width: 450px; 
    margin: 20px auto; 
    padding: 30px; 
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px); 
    border-radius: 20px; 
    border: 1px solid rgba(0,71,171,0.1);
    box-shadow: 0 8px 32px rgba(0,71,171,0.15); 
}

input[type="text"], input[type="password"] { 
    height: 45px !important; 
    font-size: 15px !important; 
}
</style>
""", unsafe_allow_html=True)

# --- Supabase ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- Sessão ---
if "logado" not in st.session_state: st.session_state.logado = False
if "usuario" not in st.session_state: st.session_state.usuario = None
if "tem_busca" not in st.session_state: st.session_state.tem_busca = ""

# --- Função auxiliar ---
def limpar_busca(texto):
    if pd.isna(texto): 
        return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\\u0300-\\u036f]', '', texto)
    texto = re.sub(r'[^a-zA-Z0-9\\s]', '', texto)
    return texto

# --- Login / Cadastro ---
if not st.session_state.logado:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🕊️<br>Guia Espírita</div>', unsafe_allow_html=True)
    
    aba = st.radio("", ["Login", "Cadastro"], horizontal=True)

    if aba == "Login":
        email = st.text_input("", placeholder="📧 Digite seu e-mail", label_visibility="collapsed")
        senha = st.text_input("", placeholder="🔒 Digite sua senha", type="password", label_visibility="collapsed")
        if st.button("🚀 ACESSAR", use_container_width=True):
            if email.strip() and senha.strip():
                try:
                    resposta = supabase.table("acessos").select("*").eq("email", email.strip().lower()).eq("senha", senha.strip()).execute()
                    if resposta.data and len(resposta.data) > 0:
                        st.session_state.logado = True
                        st.session_state.usuario = email.strip().lower()
                        st.rerun()
                    else:
                        st.error("❌ E-mail ou senha incorretos!")
                except Exception as e:
                    st.error(f"❌ Erro ao conectar: {str(e)}")
            else:
                st.error("❌ Preencha e-mail e senha!")
    else:
        nome = st.text_input("", placeholder="👤 Digite seu nome completo", label_visibility="collapsed")
        email = st.text_input("", placeholder="📧 Digite seu e-mail", label_visibility="collapsed")
        senha = st.text_input("", placeholder="🔒 Crie uma senha", type="password", label_visibility="collapsed")
        senha_conf = st.text_input("", placeholder="🔒 Confirme a senha", type="password", label_visibility="collapsed")
        if st.button("📝 CADASTRAR", use_container_width=True):
            if not nome.strip() or not email.strip() or not senha.strip() or not senha_conf.strip():
                st.error("❌ Todos os campos são obrigatórios!")
            elif senha != senha_conf:
                st.error("❌ Senhas não conferem!")
            else:
                try:
