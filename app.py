import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# 1. Configuração e Estilo Profissional
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .card-centro {
        background-color: white; padding: 18px; border-radius: 12px;
        border-left: 6px solid #0047AB; margin-bottom: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .nome-principal { color: #0047AB; font-size: 22px; font-weight: bold; line-height: 1.1; }
    .nome-fantasia { color: #5CACE2; font-size: 15px; font-weight: 500; margin-bottom: 10px; font-style: italic; }
    .info-texto { color: #555; font-size: 14px; margin-bottom: 3px; }
    
    /* Botões Lado a Lado Pequenos */
    div.stLinkButton > a {
        width: 100% !important;
        font-size: 13px !important;
        height: 40px !important;
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

# --- LOGIN ---
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
    busca = st.text_input("🔍 O que você procura?", placeholder="Nome, Cidade ou Responsável...")

    if busca:
        try:
            df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
            res = df[df.apply(lambda r: r.str.contains(busca, case=False).any(), axis=1)]

            if not res.empty:
                cols = df.columns.tolist()
                # Procura colunas por palavras-chave
                c_nome = next((c for c in cols if 'nome' in c.lower()), cols[0])
                c_fant = next((c for c in cols if 'fantasia' in c.lower()), None)
                c_end = next((c for c in cols if 'endere' in c.lower() or 'rua' in c.lower() or 'local' in c.lower()), None)
                c_cid = next((c for c in cols if 'cidade' in c.lower()), "")
                c_cel = next((c for c in cols if 'celular' in c.lower() or 'whats' in c.lower() or 'contato' in c.lower() or 'fone' in c.lower()), None)

                for _, row in res.iterrows():
                    n = row[c_nome]
                    f = row[c_fant] if c_fant else ""
                    e_txt = row[c_end] if c_end else ""
                    ci = row[c_cid] if c_cid else ""
                    ce = row[c_cel] if c_cel else ""

                    st.markdown(f"""
                        <div class="card-centro">
                            <div class="nome-principal">{n}</div>
                            <div class="nome-fantasia">{f}</div>
                            <div class="info-texto">📍 {e_txt}</div>
                            <div class="info-texto">🏙️ {ci}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # BOTÕES LADO A LADO
                    col1, col2 = st.columns(2)
                    with col1:
                        if e_txt:
                            link_m = f"https://www.google.com{urllib.parse.quote(f'{e_txt} {ci}')}"
                            st.link_button("🗺️ MAPS", link_m)
                    with col2:
                        if ce:
                            num = ''.join(filter(str.isdigit, ce))
                            st.link_button("💬 WHATSAPP", f"https://wa.me{num}")
                    st.write("") 
            else: st.warning("Nenhum resultado.")
        except Exception as e: st.error(f"Erro: {e}")
    else: st.info("Digite para pesquisar! 🙏")


