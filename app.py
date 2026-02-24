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
        background-color: white; padding: 18px; border-radius: 12px;
        border-left: 8px solid #0047AB; margin-bottom: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .nome-principal { color: #0047AB; font-size: 22px; font-weight: bold; line-height: 1.1; }
    .nome-fantasia { color: #5CACE2; font-size: 15px; font-weight: 500; margin-bottom: 10px; font-style: italic; }
    .info-texto { color: #444; font-size: 14px; margin-bottom: 3px; }
    
    /* Botões Lado a Lado */
    div.stLinkButton > a {
        width: 100% !important;
        font-size: 13px !important;
        height: 42px !important;
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
    busca = st.text_input("🔍 O que você procura?", placeholder="Busque por Nome, Cidade ou Responsável...")

    if busca:
        try:
            df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
            res = df[df.apply(lambda r: r.str.contains(busca, case=False).any(), axis=1)]

            if not res.empty:
                cols = df.columns.tolist()
                
                # FUNÇÃO PARA ENCONTRAR COLUNA POR PALAVRA-CHAVE
                def get_c(terms):
                    return next((c for c in cols if any(t in c.lower() for t in terms)), None)

                c_fant = get_c(['fantasia'])
                c_nome = get_c(['nome'])
                c_cid = get_c(['cidade'])
                c_end = get_c(['endere', 'rua', 'local'])
                c_resp = get_c(['responsavel', 'dirigente', 'dono'])
                c_cel = get_c(['celular', 'whats', 'contato', 'fone'])

                for _, row in res.iterrows():
                    val_nome = row[c_nome] if c_nome else "Centro"
                    val_fant = row[c_fant] if c_fant else ""
                    val_resp = row[c_resp] if c_resp else "Não informado"
                    val_end = row[c_end] if c_end else ""
                    val_cid = row[c_cid] if c_cid else ""
                    val_cel = row[c_cel] if c_cel else ""

                    # EXIBIÇÃO DO CARD
                    st.markdown(f"""
                        <div class="card-centro">
                            <div class="nome-principal">{val_nome}</div>
                            <div class="nome-fantasia">{val_fant}</div>
                            <div class="info-texto">👤 <b>Responsável:</b> {val_resp}</div>
                            <div class="info-texto">📍 {val_end}</div>
                            <div class="info-texto">🏙️ {val_cid}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # BOTÕES LADO A LADO
                    col1, col2 = st.columns(2)
                    with col1:
                        if val_end:
                            # MAPS: Codifica endereço e cidade para o link funcionar
                            end_full = f"{val_end} {val_cid}".strip()
                            st.link_button("🗺️ MAPS", f"https://www.google.com{urllib.parse.quote(end_full)}")
                    with col2:
                        if val_cel:
                            # WHATSAPP: Limpa tudo e deixa só números
                            zap = ''.join(filter(str.isdigit, val_cel))
                            if len(zap) >= 10:
                                st.link_button("💬 WHATSAPP", f"https://wa.me{zap}")
                    st.write("") 
            else: st.warning("Nenhum resultado.")
        except Exception as err: st.error(f"Erro: {err}")
    else: st.info("Digite para pesquisar! 🙏")
