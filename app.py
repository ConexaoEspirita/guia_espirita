import streamlit as st
import pandas as pd
import urllib.parse
from supabase import create_client, Client

# --- CONEXÃO ---
# Certifique-se que no Streamlit Cloud os Secrets estão como: supabase_url e supabase_key
try:
    supabase: Client = create_client(st.secrets["supabase_url"], st.secrets["supabase_key"])
except Exception as e:
    st.error("Erro na conexão com Supabase. Verifique os Secrets.")
    st.stop()

# --- ESTADO DE LOGIN ---
if "logado" not in st.session_state:
    st.session_state.logado = False

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    st.title("🕊️ Guia Espírita - Acesso")
    
    # Abas simples
    tab1, tab2 = st.tabs(["Login", "Cadastro"])
    
    with tab1:
        email_input = st.text_input("E-mail")
        senha_input = st.text_input("Senha", type="password")
        if st.button("ENTRAR"):
            # O código olha exatamente para as colunas que você criou: email e senha
            res = supabase.table("usuarios").select("*").eq("email", email_input).eq("senha", senha_input).execute()
            
            if res.data:
                st.session_state.logado = True
                st.session_state.usuario = email_input # Usa o email como nome
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos no banco de dados.")

    with tab2:
        novo_email = st.text_input("Novo E-mail")
        nova_senha = st.text_input("Nova Senha", type="password")
        if st.button("CADASTRAR"):
            if novo_email and nova_senha:
                # Insere exatamente nas colunas email e senha
                supabase.table("usuarios").insert({"email": novo_email, "senha": nova_senha}).execute()
                st.success("Cadastrado! Agora faça login.")

# --- APP PRINCIPAL ---
else:
    st.sidebar.title(f"Olá, {st.session_state.usuario}")
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title("🕊️ Guia de Centros Espíritas")
    
    # Aqui entra o seu código original do Excel (df = pd.read_excel...)
    # [COLE AQUI O RESTANTE DO SEU CÓDIGO DO EXCEL QUE JÁ ESTAVA FUNCIONANDO]
