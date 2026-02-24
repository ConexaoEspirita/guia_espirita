import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# 1. Configuração e Estilo
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CONEXÃO SUPABASE ---
url = "https://fjqowpuzenqraugcmmtp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZqcW93cHV6ZW5xcmF1Z2NtbXRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE4Njk2NzQsImV4cCI6MjA4NzQ0NTY3NH0.otWbLrbW4zYOb8-PCZwHYP9vQIbcWCRP_drXHGwIjzw"
supabase = create_client(url, key)

# --- CONTROLE DE SESSÃO ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuario_email' not in st.session_state: st.session_state.usuario_email = ""

# ⚠️ SEU E-MAIL DE ADMIN ⚠️
EMAIL_MESTRE = "seu-email@gmail.com" 

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
                st.session_state.logado = True
                st.session_state.usuario_email = e_log
                st.rerun()
    with aba2:
        e_cad = st.text_input("E-mail para cadastro", key="e_cad").strip().lower()
        s_cad = st.text_input("Escolha uma senha", type="password", key="c_cad")
        if st.button("CADASTRAR"):
            supabase.table("acessos").insert({"email": e_cad, "senha": s_cad, "status": "CADASTRO"}).execute()
            st.success("Conta criada! Vá em 'Entrar'.")

# --- PAINEL ADMIN ---
elif st.session_state.usuario_email == EMAIL_MESTRE:
    st.title("📊 Painel Admin")
    if st.sidebar.button("Sair"): st.session_state.logado = False; st.rerun()
    dados = supabase.table("acessos").select("*").execute()
    st.dataframe(pd.DataFrame(dados.data), use_container_width=True)

# --- GUIA DOS CENTROS (COM MAPS E WHATSAPP) ---
else:
    st.title("🕊️ Guia Espírita 🕊️")
    with st.sidebar:
        if st.button("👋 SAIR"): st.session_state.logado = False; st.rerun()
    
    try:
        df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
        
        # Lógica para criar links de Maps e WhatsApp
        def criar_link_maps(end):
            return f"https://www.google.com{urllib.parse.quote(end)}"
        
        def criar_link_whats(num):
            num_limpo = ''.join(filter(str.isdigit, num))
            return f"https://wa.me{num_limpo}?text=Olá,%20vi%20seu%20contato%20no%20Guia%20Espírita"

        # Criando as colunas de clique (supondo que as colunas no Excel chamem 'Endereco' e 'Celular')
        if 'Endereco' in df.columns:
            df['📍 Ir ao Local'] = df['Endereco'].apply(criar_link_maps)
        if 'Celular' in df.columns:
            df['💬 WhatsApp'] = df['Celular'].apply(criar_link_whats)

        busca = st.text_input("🔍 O QUE VOCÊ PROCURA?")
        if busca:
            df = df[df.apply(lambda r: r.str.contains(busca, case=False).any(), axis=1)]

        # Configura a tabela para mostrar os links como botões clicáveis
        st.dataframe(
            df,
            column_config={
                "📍 Ir ao Local": st.column_config.LinkColumn("📍 Rota Maps"),
                "💬 WhatsApp": st.column_config.LinkColumn("💬 Chamar no Zap")
            },
            use_container_width=True,
            hide_index=True
        )
    except Exception as e:
        st.error(f"Erro: {e}")
