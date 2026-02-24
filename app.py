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
        border-left: 8px solid #0047AB; margin-bottom: 5px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .nome-real { color: #0047AB; font-size: 24px; font-weight: bold; line-height: 1.1; }
    .nome-fantasia { color: #5CACE2; font-size: 16px; font-weight: 500; margin-bottom: 12px; font-style: italic; }
    .info-texto { color: #444; font-size: 14px; margin-bottom: 4px; }
    
    div.stLinkButton > a {
        width: 100% !important;
        font-size: 14px !important;
        font-weight: bold !important;
        height: 45px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO SUPABASE ---
url = "https://fjqowpuzenqraugcmmtp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZqcW93cHV6ZW5xcmF1Z2NtbXRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE4Njk2NzQsImV4cCI6MjA4NzQ0NTY3NH0.otWbLrbW4zYOb8-PCZwHYP9vQIbcWCRP_drXHGwIjzw"
supabase = create_client(url, key)

if 'logado' not in st.session_state: st.session_state.logado = False

# --- ACESSO ---
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
    busca = st.text_input("🔍 O que você procura?", placeholder="Busque por Nome, Cidade ou Responsável...")

    if busca:
        try:
            df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
            res = df[df.apply(lambda r: r.str.contains(busca, case=False).any(), axis=1)]

            if not res.empty:
                for _, row in res.iterrows():
                    # MAPEAMENTO MANUAL DAS COLUNAS DO SEU EXCEL
                    n_fantasia = row.get('Nome Fantasia', '')
                    n_real = row.get('Nome', 'Centro Espírita')
                    cid = row.get('Cidade', '')
                    end = row.get('Endereco', row.get('Endereço', ''))
                    resp = row.get('Responsavel', row.get('Responsável', ''))
                    cel = row.get('Celular', '')

                    # Card Visual Estilo Placar
                    st.markdown(f"""
                        <div class="card-centro">
                            <div class="nome-real">{n_real}</div>
                            <div class="nome-fantasia">{n_fantasia}</div>
                            <div class="info-texto">👤 <b>Responsável:</b> {resp}</div>
                            <div class="info-texto">📍 {end}</div>
                            <div class="info-texto">🏙️ {cid}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if end:
                            # LINK MAPS CORRIGIDO PARA NÃO DAR ERRO DE DNS
                            q = urllib.parse.quote(f"{end}, {cid}")
                            st.link_button("🗺️ MAPS", f"https://www.google.com{q}")
                    with c2:
                        if cel:
                            # LINK WHATSAPP LIMPO
                            z = ''.join(filter(str.isdigit, cel))
                            if len(z) >= 10:
                                st.link_button("💬 WHATSAPP", f"https://wa.me{z}")
            else: st.warning("Nenhum resultado.")
        except Exception as e: st.error(f"Erro ao carregar dados.")
    else: st.info("Digite acima para pesquisar! 🙏")
