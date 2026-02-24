import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# 1. Estilo Profissional
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .card-centro {
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 8px solid #0047AB; margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .nome-principal { color: #0047AB; font-size: 26px; font-weight: bold; line-height: 1.1; }
    .nome-fantasia { color: #5CACE2; font-size: 17px; font-weight: 500; margin-bottom: 12px; font-style: italic; }
    .info-texto { color: #555; font-size: 15px; margin-bottom: 4px; }
    .tag-palestra { background-color: #D4EDDA; color: #155724; padding: 5px 10px; border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block; margin-top: 10px; }
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
    if st.button("ENTRAR NO GUIA"):
        res = supabase.table("acessos").select("*").eq("email", e).eq("senha", s).execute()
        if len(res.data) > 0:
            st.session_state.logado = True; st.rerun()
        else: st.error("Incorreto!")
else:
    st.image("https://images.unsplash.com", use_container_width=True)
    st.title("🕊️ Guia Espírita 🕊️")
    busca = st.text_input("🔍 O que você procura?", placeholder="Busque por Nome, Cidade...")

    if busca:
        try:
            df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
            res = df[df.apply(lambda r: r.str.contains(busca, case=False).any(), axis=1)]

            if not res.empty:
                # --- IDENTIFICADOR INTELIGENTE DE COLUNAS ---
                cols = df.columns.tolist()
                def achar_col(termos):
                    return next((c for c in cols if any(t in c.lower() for t in termos)), None)

                c_nome = achar_col(['nome'])
                c_fant = achar_col(['fantasia'])
                c_resp = achar_col(['responsavel', 'dirigente', 'dono'])
                c_end = achar_col(['endere', 'rua', 'local'])
                c_cid = achar_col(['cidade', 'municip'])
                c_pal = achar_col(['palestra', 'publica', 'dia'])
                c_cel = achar_col(['celular', 'whats', 'contato', 'fone'])

                for _, row in res.iterrows():
                    n = row[c_nome] if c_nome else "Centro Espírita"
                    f = row[c_fant] if c_fant else ""
                    r = row[c_resp] if c_resp else "Não informado"
                    e = row[c_end] if c_end else ""
                    ci = row[c_cid] if c_cid else ""
                    p = row[c_pal] if c_pal else ""
                    ce = row[c_cel] if c_cel else ""

                    st.markdown(f"""
                        <div class="card-centro">
                            <div class="nome-principal">{n}</div>
                            <div class="nome-fantasia">{f}</div>
                            <div class="info-texto">👤 <b>Responsável:</b> {r}</div>
                            <div class="info-texto">📍 {e}</div>
                            <div class="info-texto">🏙️ {ci}</div>
                            {f'<div class="tag-palestra">🗓️ Palestra: {p}</div>' if p else ''}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if e:
                            u = f"https://www.google.com{urllib.parse.quote(e + ' ' + ci)}"
                            st.link_button("🗺️ MAPS", u)
                    with c2:
                        if ce:
                            num = ''.join(filter(str.isdigit, ce))
                            st.link_button("💬 WHATSAPP", f"https://wa.me{num}")
            else:
                st.warning("Nenhum resultado.")
        except Exception as err:
            st.error(f"Erro ao ler planilha: {err}")
    else:
        st.info("Digite para pesquisar! 🙏")
