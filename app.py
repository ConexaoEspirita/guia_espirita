import streamlit as st
import pandas as pd
import urllib.parse
import re
import os
import hashlib
from datetime import datetime

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# =========================
# CONFIG ADMIN
# =========================
ADMIN_EMAIL = "admin@guia.com"
ADMIN_SENHA = hashlib.sha256("1234".encode()).hexdigest()

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Criar arquivo usuarios se não existir
if not os.path.exists("usuarios.csv"):
    pd.DataFrame(columns=["nome","email","senha","data"]).to_csv("usuarios.csv", index=False)

# --- CSS ---
st.markdown("""
<style>
    [data-testid="stArrowBack"] { display: none !important; }
    section[data-testid="stSidebar"] > div { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    .stApp { background: #E0F2FE; }  /* AZUL CÉU CLARO */

    .login-box {
        background: white;
        padding: 35px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
        max-width: 420px;
        margin: auto;
    }

    .card-centro { 
        background: white !important; padding: 25px; border-radius: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.12); 
        margin-bottom: 25px; border-left: 12px solid #0047AB; position: relative;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "menu_aberto" not in st.session_state:
    st.session_state.menu_aberto = False

# =========================
# LOGIN / CADASTRO / RESET
# =========================
if not st.session_state.logado:

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.title("🕊️ Guia Espírita")

    aba = st.radio("", ["Login", "Cadastrar", "Esqueci a senha"], horizontal=True)

    df_users = pd.read_csv("usuarios.csv")

    if aba == "Login":
        with st.form("login"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR"):

                # ADMIN
                if email.lower() == ADMIN_EMAIL and hash_senha(senha) == ADMIN_SENHA:
                    st.session_state.logado = True
                    st.rerun()

                user = df_users[
                    (df_users["email"].str.lower() == email.lower()) &
                    (df_users["senha"] == hash_senha(senha))
                ]

                if not user.empty:
                    st.session_state.logado = True
                    st.rerun()
                else:
                    st.error("Email ou senha incorretos.")

    elif aba == "Cadastrar":
        with st.form("cadastro"):
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")

            if st.form_submit_button("Cadastrar"):
                if not nome.strip() or not email.strip() or not senha.strip():
                    st.error("Preencha todos os campos.")
                elif email.lower() == ADMIN_EMAIL:
                    st.error("Email reservado.")
                elif email.lower() in df_users["email"].str.lower().values:
                    st.warning("Email já cadastrado.")
                else:
                    novo = pd.DataFrame([{
                        "nome": nome,
                        "email": email.lower(),
                        "senha": hash_senha(senha),
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }])
                    df_users = pd.concat([df_users, novo], ignore_index=True)
                    df_users.to_csv("usuarios.csv", index=False)
                    st.success("Cadastro realizado!")

    elif aba == "Esqueci a senha":
        with st.form("reset"):
            email = st.text_input("E-mail cadastrado")
            nova = st.text_input("Nova senha", type="password")
            if st.form_submit_button("Redefinir"):
                if email.lower() not in df_users["email"].str.lower().values:
                    st.error("Email não encontrado.")
                else:
                    df_users.loc[
                        df_users["email"].str.lower() == email.lower(),
                        "senha"
                    ] = hash_senha(nova)
                    df_users.to_csv("usuarios.csv", index=False)
                    st.success("Senha redefinida!")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# RESTANTE DO SEU SISTEMA
# =========================
else:

    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()

    st.title("🕊️ Bem-vindo ao Guia Espírita")

    if st.button("📋 " + ("Fechar Menu" if st.session_state.menu_aberto else "Abrir Menu"), use_container_width=True):
        st.session_state.menu_aberto = not st.session_state.menu_aberto
        st.rerun()

    if st.session_state.menu_aberto:
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔎 Pesquisar Geral", use_container_width=True):
                st.session_state.pagina = "pesquisar"
                st.session_state.menu_aberto = False
                st.rerun()

            if st.button("📍 Por Cidade", use_container_width=True):
                st.session_state.pagina = "cidade"
                st.session_state.menu_aberto = False
                st.rerun()

        with col2:
            if st.button("📊 Admin", use_container_width=True):
                st.session_state.pagina = "admin"
                st.session_state.menu_aberto = False
                st.rerun()

            if st.button("🕊️ Frases", use_container_width=True):
                st.session_state.pagina = "frases"
                st.session_state.menu_aberto = False
                st.rerun()

        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logado = False
            st.session_state.menu_aberto = False
            st.rerun()

        st.markdown("---")

    pagina = st.session_state.get('pagina', None)

    # AQUI CONTINUA EXATAMENTE COMO VOCÊ JÁ TINHA (não alterei nada)
