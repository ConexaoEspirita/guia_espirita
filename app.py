import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# 1. Configuração e Estilo
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .card-centro {
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 8px solid #0047AB; margin-bottom: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .nome-real { color: #0047AB; font-size: 24px; font-weight: bold; }
    .nome-fantasia { color: #5CACE2; font-size: 16px; font-weight: 500; font-style: italic; margin-bottom: 10px; }
    .info-texto { color: #444; font-size: 14px; margin-bottom: 4px; }
    div.stLinkButton > a { width: 100% !important; font-weight: bold !important; height: 45px !important; display: flex !important; align-items: center !important; justify-content: center !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO SUPABASE ---
url = "https://fjqowpuzenqraugcmmtp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZqcW93cHV6ZW5xcmF1Z2NtbXRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE4Njk2NzQsImV4cCI6MjA4NzQ0NTY3NH0.otWbLrbW4zYOb8-PCZwHYP9vQIbcWCRP_drXHGwIjzw"
supabase = create_client(url, key)

if 'logado' not in st.session_state: st.session_state.logado = False

# --- TELA DE ACESSO ---
if not st.session_state.logado:
    st.title("🕊️ Guia Espírita 🕊️")
    e = st.text_input("E-mail").strip().lower()
    s = st.text_input("Senha", type="password")
    if st.button("ACESSAR GUIA"):
        res = supabase.table("acessos").select("*").eq("email", e).eq("senha", s).execute()
        if len(res.data) > 0:
            st.session_state.logado = True; st.rerun()
        else: st.error("Dados incorretos!")
else:
    st.image("https://images.unsplash.com", use_container_width=True)
    st.title("🕊️ Guia Espírita")
    busca = st.text_input("🔍 O que você procura?", placeholder="Digite para buscar...")

    if busca:
        try:
            df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
            res = df[df.apply(lambda r: r.str.contains(busca, case=False).any(), axis=1)]

            if not res.empty:
                for _, row in res.iterrows():
                    # PEGA PELA POSIÇÃO DA COLUNA (0, 1, 2...) PARA NÃO TER ERRO DE NOME
                    # Ordem no Excel deve ser: Fantasia, Nome, Cidade, Endereço, Palestra, Responsável, Celular
                    v_fantasia = row.iloc[0] if len(row) > 0 else ""
                    v_nome = row.iloc[1] if len(row) > 1 else "Centro"
                    v_cidade = row.iloc[2] if len(row) > 2 else ""
                    v_endereco = row.iloc[3] if len(row) > 3 else ""
                    v_palestra = row.iloc[4] if len(row) > 4 else ""
                    v_responsavel = row.iloc[5] if len(row) > 5 else ""
                    v_celular = row.iloc[6] if len(row) > 6 else ""

                    # Card Visual
                    st.markdown(f"""
                        <div class="card-centro">
                            <div class="nome-real">{v_nome}</div>
                            <div class="nome-fantasia">{v_fantasia}</div>
                            <div class="info-texto">👤 <b>Responsável:</b> {v_responsavel}</div>
                            <div class="info-texto">📍 {v_endereco}</div>
                            <div class="info-texto">🏙️ {v_cidade}</div>
                            <div class="info-texto">🗓️ {v_palestra}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if v_endereco:
                            # LINK GOOGLE MAPS BLINDADO
                            endereco_limpo = f"{v_endereco}, {v_cidade}".strip()
                            q = urllib.parse.quote(endereco_limpo)
                            st.link_button("🗺️ MAPS", f"https://www.google.com{q}")
                    with c2:
                        if v_celular:
                            num = ''.join(filter(str.isdigit, v_celular))
                            st.link_button("💬 WHATSAPP", f"https://wa.me{num}")
            else: st.warning("Nenhum resultado.")
        except Exception as e: st.error(f"Erro: {e}")
    else: st.info("Digite acima para pesquisar! 🙏")
