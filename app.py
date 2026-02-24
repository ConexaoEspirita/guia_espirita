import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CONEXÃO SUPABASE ---
url = "https://fjqowpuzenqraugcmmtp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZqcW93cHV6ZW5xcmF1Z2NtbXRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE4Njk2NzQsImV4cCI6MjA4NzQ0NTY3NH0.otWbLrbW4zYOb8-PCZwHYP9vQIbcWCRP_drXHGwIjzw"
supabase = create_client(url, key)

# 2. Estilo Visual (CSS)
st.markdown("""
    <style>
    h1 { font-size: clamp(26px, 8vw, 48px) !important; text-align: center; color: #0047AB; }
    .stApp { background-color: #F0F8FF; }
    .stButton button { width: 100% !important; height: 50px !important; font-size: 20px !important; background-color: #0047AB !important; color: white !important; font-weight: bold; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONTROLE DE SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'usuario_email' not in st.session_state:
    st.session_state.usuario_email = ""

# --- ⚠️ COLOQUE SEU E-MAIL REAL ABAIXO ⚠️ ---
EMAIL_MESTRE = "seu-email-aqui@gmail.com" 

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    st.title("🕊️ Guia Espírita 🕊️")
    st.subheader("Digite seu e-mail para acessar:")
    email_input = st.text_input("E-mail", label_visibility="collapsed", placeholder="exemplo@email.com").strip().lower()
    
    if st.button("✨ ACESSAR O GUIA"):
        if email_input:
            try:
                supabase.table("acessos").insert({"email": email_input, "status": "ENTRADA"}).execute()
            except:
                pass
            st.session_state.logado = True
            st.session_state.usuario_email = email_input
            st.rerun()

# --- ÁREA EXCLUSIVA DO ADMINISTRADOR ---
elif st.session_state.usuario_email == EMAIL_MESTRE:
    st.title("📊 Painel do Administrador")
    
    if st.sidebar.button("Ir para o Guia (Visão Usuário)"):
        st.session_state.usuario_email = "visualizacao@admin.com"
        st.rerun()

    try:
        dados = supabase.table("acessos").select("*").execute()
        df_adm = pd.DataFrame(dados.data)
        
        # FORMATAÇÃO DA DATA (24/02/2026 as 07h52:50)
        df_adm['created_at'] = pd.to_datetime(df_adm['created_at'])
        df_adm['Data/Hora'] = df_adm['created_at'].dt.strftime('%d/%m/%Y as %Hh%M:%S')

        total_cadastros = len(df_adm[df_adm['status'] == 'ENTRADA'])
        total_saidas = len(df_adm[df_adm['status'] == 'SAIDA'])
        ativos = total_cadastros - total_saidas

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Cadastros", total_cadastros)
        col2.metric("Encerraram Experiência", total_saidas)
        col3.metric("Usuários Ativos (Aprox.)", ativos if ativos > 0 else 0)

        st.write("### Histórico de Movimentação")
        # Exibe apenas as colunas importantes e formatadas
        df_exibir_adm = df_adm[['Data/Hora', 'email', 'status']].sort_values(by='Data/Hora', ascending=False)
        st.dataframe(df_exibir_adm, use_container_width=True, hide_index=True)
    except Exception as e:
        st.info("Aguardando registros...")

# --- TELA DO GUIA ESPÍRITA ---
else:
    st.title("🕊️ Guia Espírita 🕊️")
    with st.sidebar:
        st.write(f"Conectado: \n**{st.session_state.usuario_email}**")
        if st.button("👋 ENCERRAR EXPERIÊNCIA"):
            try:
                supabase.table("acessos").insert({"email": st.session_state.usuario_email, "status": "SAIDA"}).execute()
            except:
                pass
            st.session_state.logado = False
            st.session_state.usuario_email = ""
            st.rerun()

    try:
        df = pd.read_excel("guia.xlsx")
        df = df.astype(str).replace('nan', '')
        busca = st.text_input("🔍 O QUE VOCÊ PROCURA?", placeholder="Cidade, Centro, Bairro...")
        
        if busca:
            mask = df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)
            df_exibir = df[mask]
        else:
            df_exibir = df

        st.dataframe(df_exibir, use_container_width=True, hide_index=True)
    except:
        st.error("Erro ao carregar o Guia.")

