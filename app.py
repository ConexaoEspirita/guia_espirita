import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CONEXÃO SUPABASE ---
url = "https://fjqowpuzenqraugcmmtp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZqcW93cHV6ZW5xcmF1Z2NtbXRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE4Njk2NzQsImV4cCI6MjA4NzQ0NTY3NH0.otWbLrbW4zYOb8-PCZwHYP9vQIbcWCRP_drXHGwIjzw"
supabase = create_client(url, key)

# --- ESTILO GERAL ---
st.markdown("<style>.stApp { background-color: #F0F8FF; } h1 {text-align: center; color: #0047AB; font-size: 40px;}</style>", unsafe_allow_html=True)

# --- CONTROLE DE SESSÃO ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuario_email' not in st.session_state: st.session_state.usuario_email = ""

# --- SEU E-MAIL DE ADMIN ---
EMAIL_MESTRE = "seu-email-aqui@gmail.com" 

# --- TELA DE ACESSO ---
if not st.session_state.logado:
    st.title("🕊️ Guia Espírita 🕊️")
    aba1, aba2 = st.tabs(["🔐 Entrar", "📝 Criar Conta"])

    with aba1:
        e_log = st.text_input("E-mail", key="e_log").strip().lower()
        s_log = st.text_input("Senha", type="password", key="s_log")
        if st.button("ACESSAR GUIA"):
            res = supabase.table("acessos").select("*").eq("email", e_log).eq("senha", s_log).execute()
            if len(res.data) > 0:
                supabase.table("acessos").insert({"email": e_log, "status": "ENTRADA"}).execute()
                st.session_state.logado = True
                st.session_state.usuario_email = e_log
                st.rerun()
            else:
                st.error("E-mail ou Senha incorretos!")

    with aba2:
        e_cad = st.text_input("E-mail para cadastro", key="e_cad").strip().lower()
        s_cad = st.text_input("Escolha uma senha", type="password", key="s_cad")
        if st.button("CADASTRAR AGORA"):
            if e_cad and len(s_cad) >= 4:
                try:
                    supabase.table("acessos").insert({"email": e_cad, "senha": s_cad, "status": "CADASTRO"}).execute()
                    st.success("Conta criada com sucesso! Vá na aba 'Entrar'.")
                except:
                    st.error("Erro ao cadastrar. Verifique se o e-mail já existe.")
            else:
                st.warning("Preencha o e-mail e use uma senha de pelo menos 4 dígitos.")

# --- PAINEL ADMIN (SÓ VOCÊ) ---
elif st.session_state.usuario_email == EMAIL_MESTRE:
    st.title("📊 Painel Administrativo")
    if st.sidebar.button("Ir para o Guia"): st.session_state.usuario_email = "admin@view.com"; st.rerun()
    
    dados = supabase.table("acessos").select("*").execute()
    df_adm = pd.DataFrame(dados.data)
    if not df_adm.empty:
        df_adm['created_at'] = pd.to_datetime(df_adm['created_at']).dt.tz_convert('America/Sao_Paulo')
        df_adm['Data/Hora'] = df_adm['created_at'].dt.strftime('%d/%m/%Y as %Hh%M:%S')
        st.dataframe(df_adm[['Data/Hora', 'email', 'status', 'senha']].sort_values(by='Data/Hora', ascending=False), use_container_width=True)

# --- GUIA DOS CENTROS ---
else:
    st.title("🕊️ Guia Espírita 🕊️")
    with st.sidebar:
        if st.button("👋 SAIR"):
            supabase.table("acessos").insert({"email": st.session_state.usuario_email, "status": "SAIDA"}).execute()
            st.session_state.logado = False; st.rerun()
    
    try:
        df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
        busca = st.text_input("🔍 O QUE VOCÊ PROCURA?")
        if busca:
            df = df[df.apply(lambda r: r.str.contains(busca, case=False).any(), axis=1)]
        st.dataframe(df, use_container_width=True, hide_index=True)
    except:
        st.error("Erro ao carregar o arquivo guia.xlsx")
