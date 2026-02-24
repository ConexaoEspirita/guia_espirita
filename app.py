import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
from datetime import datetime

# 1. Configuração de App Profissional
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# Estilo Visual (Cards e Cores)
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .centro-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border-left: 6px solid #0047AB;
    }
    .titulo-centro { color: #0047AB; font-size: 1.3rem; font-weight: bold; }
    .info-texto { color: #666; font-size: 0.9rem; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

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
    aba_l, aba_c = st.tabs(["🔐 Entrar", "📝 Criar Conta"])
    with aba_l:
        e = st.text_input("E-mail").strip().lower()
        s = st.text_input("Senha", type="password")
        if st.button("ACESSAR GUIA"):
            res = supabase.table("acessos").select("*").eq("email", e).eq("senha", s).execute()
            if len(res.data) > 0:
                supabase.table("acessos").insert({"email": e, "status": "ENTRADA"}).execute()
                st.session_state.logado = True
                st.session_state.usuario_email = e
                st.rerun()
    with aba_c:
        ec = st.text_input("Novo E-mail").strip().lower()
        sc = st.text_input("Nova Senha", type="password")
        if st.button("CADASTRAR"):
            supabase.table("acessos").insert({"email": ec, "senha": sc, "status": "CADASTRO"}).execute()
            st.success("Conta criada!")

# --- PAINEL DO ADMINISTRADOR (ONDE FICA O EXCEL ESCONDIDO) ---
elif st.session_state.usuario_email == EMAIL_MESTRE:
    st.title("📊 Painel Administrativo")
    if st.sidebar.button("Visualizar Guia (Cards)"): 
        st.session_state.usuario_email = "modo_visualizacao@admin.com"; st.rerun()
    
    aba_dados, aba_excel = st.tabs(["📈 Estatísticas de Acesso", "📂 Planilha Bruta (Excel)"])
    
    try:
        # Busca dados do Supabase para estatísticas
        acessos = supabase.table("acessos").select("*").execute()
        df_ac = pd.DataFrame(acessos.data)
        
        with aba_dados:
            st.metric("Total de Movimentações", len(df_ac))
            st.dataframe(df_ac.sort_values(by='id', ascending=False), use_container_width=True)

        with aba_excel:
            st.info("Aqui você vê os dados originais do arquivo guia.xlsx")
            df_bruto = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
            st.dataframe(df_bruto, use_container_width=True) # O Excel escondido só para você
    except:
        st.error("Erro ao carregar dados do administrador.")

# --- TELA DO GUIA (VISÃO PROFISSIONAL COM CARDS) ---
else:
    st.title("🕊️ Guia Espírita 🕊️")
    with st.sidebar:
        if st.button("👋 SAIR"):
            supabase.table("acessos").insert({"email": st.session_state.usuario_email, "status": "SAIDA"}).execute()
            st.session_state.logado = False; st.rerun()

    try:
        df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
        busca = st.text_input("🔍 O que você procura hoje?", placeholder="Cidade, Centro ou Bairro...")
        
        if busca:
            df = df[df.apply(lambda r: r.str.contains(busca, case=False).any(), axis=1)]

        # EXIBIÇÃO EM CARDS (SEM TABELA)
        for _, row in df.iterrows():
            nome = row.get('Nome', 'Centro Espírita')
            end = row.get('Endereco', row.get('Endereço', ''))
            cid = row.get('Cidade', '')
            cel = row.get('Celular', '')

            # O Card Visual
            st.markdown(f"""
            <div class="centro-card">
                <div class="titulo-centro">{nome}</div>
                <div class="info-texto">📍 {end} - {cid}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Botões de Ação embaixo do Card
            c1, c2 = st.columns(2)
            with c1:
                if end:
                    url_m = f"https://www.google.com{urllib.parse.quote(end + ' ' + cid)}"
                    st.link_button("🗺️ ABRIR MAPS", url_m, use_container_width=True)
            with c2:
                if cel:
                    num = ''.join(filter(str.isdigit, cel))
                    st.link_button("📲 WHATSAPP", f"https://wa.me{num}", use_container_width=True)
            st.write("") # Espaço entre cards

    except Exception as e:
        st.error("Erro ao carregar o Guia das Pombinhas.")
