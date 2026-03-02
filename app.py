import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import datetime
import os
from supabase import create_client, Client

# =========================
# SUPABASE (USA SECRETS DO STREAMLIT CLOUD)
# =========================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Supabase não configurado. Configure em Settings → Secrets.")
    st.stop()

if not SUPABASE_URL.startswith("https://"):
    st.error("❌ URL do Supabase inválida.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="🕊️ Guia Espírita", layout="wide")

# =========================
# SESSION
# =========================
if "pagina" not in st.session_state:
    st.session_state["pagina"] = None
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "admin_logado" not in st.session_state:
    st.session_state["admin_logado"] = False

# =========================
# LOGIN
# =========================
if not st.session_state["logado"]:

    st.title("🕊️ Guia Espírita")

    tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])

    with tab1:
        with st.form("login"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                st.session_state["logado"] = True
                st.rerun()

    with tab2:
        with st.form("cadastro"):
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")

            if st.form_submit_button("Cadastrar"):
                try:
                    supabase.table("participantes").insert({
                        "nome": nome,
                        "email": email,
                        "status": "ativo"
                    }).execute()

                    st.success("✅ Cadastrado com sucesso!")
                    st.session_state["logado"] = True
                    st.rerun()

                except Exception as e:
                    st.error(f"Erro Supabase: {e}")

# =========================
# SISTEMA
# =========================
else:

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Admin"):
            st.session_state["pagina"] = "admin"
            st.session_state["admin_logado"] = False
            st.rerun()

    with col2:
        if st.button("🚪 Sair"):
            st.session_state.clear()
            st.rerun()

    if st.session_state["pagina"] == "admin":

        if not st.session_state["admin_logado"]:

            st.header("🔐 Login Admin")

            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")

            if st.button("Entrar Admin"):
                if usuario == "estudantesabio" and senha == "2026":
                    st.session_state["admin_logado"] = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos")

        else:

            st.header("📊 Participantes")

            try:
                res = supabase.table("participantes") \
                    .select("*") \
                    .order("created_at", desc=True) \
                    .execute()

                dados = res.data

                if dados:

                    st.info(f"Total: {len(dados)} participantes")

                    for i, p in enumerate(dados, 1):

                        created_at = p.get("created_at")

                        if created_at:
                            try:
                                dt = datetime.datetime.fromisoformat(
                                    created_at.replace("Z", "+00:00")
                                )
                                data_fmt = dt.strftime("%d/%m/%Y - %H:%M:%S")
                            except:
                                data_fmt = created_at
                        else:
                            data_fmt = "-"

                        st.markdown(f"""
                        **{i}. {p.get('nome','N/D')}**  
                        {p.get('email','N/D')}  
                        📅 {data_fmt}
                        ---
                        """)

                else:
                    st.info("Nenhum participante cadastrado.")

                if st.button("🔐 Sair Admin"):
                    st.session_state["admin_logado"] = False
                    st.rerun()

            except Exception as e:
                st.error(f"Erro Supabase: {e}")
