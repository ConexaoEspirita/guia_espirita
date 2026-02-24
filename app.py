import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata

# 1. Configuração e Estilo Profissional
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .card-centro {
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 8px solid #0047AB; margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .nome-real { color: #0047AB; font-size: 24px; font-weight: bold; line-height: 1.1; }
    .nome-fantasia { color: #5CACE2 !important; font-size: 17px !important; font-weight: 500; font-style: italic; margin-bottom: 10px; display: block; }
    .info-texto { color: #444; font-size: 14px; margin-bottom: 4px; }
    .tag-palestra { background-color: #E3F2FD; color: #0D47A1; padding: 5px 10px; border-radius: 8px; font-size: 13px; font-weight: bold; display: inline-block; margin-top: 8px; }
    
    div.stLinkButton > a {
        width: 100% !important; font-weight: bold !important; height: 45px !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO SUPABASE ---
url = "https://fjqowpuzenqraugcmmtp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZqcW93cHV6ZW5xcmF1Z2NtbXRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE4Njk2NzQsImV4cCI6MjA4NzQ0NTY3NH0.otWbLrbW4zYOb8-PCZwHYP9vQIbcWCRP_drXHGwIjzw"
supabase = create_client(url, key)

# Função para busca inteligente (ignora acentos)
def limpar(txt):
    return ''.join(c for c in unicodedata.normalize('NFD', str(txt)) if unicodedata.category(c) != 'Mn').lower()

if 'logado' not in st.session_state: st.session_state.logado = False

# --- ACESSO ---
if not st.session_state.logado:
    st.title("🕊️ Guia Espírita 🕊️")
    e = st.text_input("E-mail").strip().lower()
    s = st.text_input("Senha", type="password")
    if st.button("ACESSAR GUIA"):
        res = supabase.table("acessos").select("*").eq("email", e).eq("senha", s).execute()
        if len(res.data) > 0: st.session_state.logado = True; st.rerun()
        else: st.error("Incorreto!")
else:
    st.image("https://images.unsplash.com", use_container_width=True)
    st.title("🕊️ Guia Espírita")
    busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Geronimo, Rio Preto...")

    if busca:
        try:
            df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
            
            # Filtro que ignora acentos
            termo = limpar(busca)
            mascara = df.apply(lambda r: r.apply(limpar).str.contains(termo)).any(axis=1)
            res = df[mascara]

            if not res.empty:
                cols = df.columns.tolist()
                # Localizador de colunas por nome (não por número)
                def f_col(termos): return next((c for c in cols if any(t in c.lower() for t in termos)), None)

                c_nome = f_col(['nome'])
                c_fant = f_col(['fantasia'])
                c_resp = f_col(['responsavel', 'dirigente', 'dono'])
                c_end  = f_col(['endere', 'rua', 'local'])
                c_cid  = f_col(['cidade', 'municip'])
                c_pal  = f_col(['palestra', 'dia'])
                c_cel  = f_col(['celular', 'whats', 'contato', 'fone'])

                for _, row in res.iterrows():
                    n = row[c_nome] if c_nome else "Centro"
                    fant = row[c_fant] if c_fant else ""
                    resp = row[c_resp] if c_resp else "Não informado"
                    end  = row[c_end] if c_end else ""
                    cid  = row[c_cid] if c_cid else ""
                    pal  = row[c_pal] if c_pal else ""
                    cel  = row[c_cel] if c_cel else ""

                    # Card Visual
                    st.markdown(f"""
                        <div class="card-centro">
                            <div class="nome-real">{n}</div>
                            <div class="nome-fantasia">{fant}</div>
                            <div class="info-texto">👤 <b>Responsável:</b> {resp}</div>
                            <div class="info-texto">📍 {end}</div>
                            <div class="info-texto">🏙️ {cid}</div>
                            {f'<div class="tag-palestra">🗓️ Palestra: {pal}</div>' if pal else ''}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if end:
                            q = urllib.parse.quote(f"{end}, {cid}")
                            st.link_button("🗺️ MAPS", f"https://www.google.com{q}")
                    with c2:
                        if cel:
                            num = ''.join(filter(str.isdigit, cel))
                            if len(num) >= 10:
                                st.link_button("💬 WHATSAPP", f"https://wa.me{num}")
                    st.write("") 
            else: st.warning("Nenhum resultado.")
        except Exception as e: st.error(f"Erro: {e}")
    else: st.info("Digite acima para pesquisar! 🙏")
