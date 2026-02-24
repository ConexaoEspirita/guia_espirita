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
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 8px solid #0047AB; margin-bottom: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .nome-real { color: #0047AB; font-size: 24px; font-weight: bold; line-height: 1.1; }
    .nome-fantasia { color: #5CACE2 !important; font-size: 17px !important; font-weight: 500; font-style: italic; margin-bottom: 10px; display: block; }
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
                cols = df.columns.tolist()
                # Localizador inteligente de colunas
                def achar(termos): return next((c for c in cols if any(t in c.lower() for t in termos)), None)
                
                c_fant = achar(['fantasia'])
                c_nome = achar(['nome'])
                c_cid = achar(['cidade'])
                c_end = achar(['endere', 'rua', 'local'])
                c_resp = achar(['responsavel', 'dirigente', 'dono'])
                c_cel = achar(['celular', 'whats', 'contato', 'fone'])

                for _, row in res.iterrows():
                    v_fantasia = row[c_fant] if c_fant else ""
                    v_nome = row[c_nome] if c_nome else "Centro"
                    v_cidade = row[c_cid] if c_cid else ""
                    v_endereco = row[c_end] if c_end else ""
                    v_responsavel = row[c_resp] if c_resp else "Não informado"
                    v_celular = row[c_cel] if c_cel else ""

                    # Card Visual
                    st.markdown(f"""
                        <div class="card-centro">
                            <div class="nome-real">{v_nome}</div>
                            <div class="nome-fantasia">{v_fantasia}</div>
                            <div class="info-texto">👤 <b>Responsável:</b> {v_responsavel}</div>
                            <div class="info-texto">📍 {v_endereco}</div>
                            <div class="info-texto">🏙️ {v_cidade}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if v_endereco:
                            # Link do Google Maps formatado corretamente
                            q_end = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                            st.link_button("🗺️ MAPS", f"https://www.google.com{q_end}")
                    with c2:
                        if v_celular:
                            num = ''.join(filter(str.isdigit, v_celular))
                            st.link_button("💬 WHATSAPP", f"https://wa.me{num}")
            else: st.warning("Nenhum resultado.")
        except Exception as e: st.error(f"Erro: {e}")
    else: st.info("Digite acima para pesquisar! 🙏")
