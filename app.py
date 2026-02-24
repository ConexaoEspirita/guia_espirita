import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata

# 1. Configuração e Estilo Profissional
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="centered")

# FORÇA O APP A LER OS DADOS NOVOS TODA VEZ
st.cache_data.clear()

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .card-centro {
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 8px solid #0047AB; margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .nome-grande { color: #0047AB; font-size: 26px; font-weight: bold; line-height: 1.1; }
    .nome-fantasia { color: #5CACE2 !important; font-size: 17px !important; font-weight: 500; font-style: italic; margin-bottom: 12px; display: block; }
    .info-texto { color: #444; font-size: 14px; margin-bottom: 4px; }
    
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

def limpar_busca(txt):
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
        else: st.error("Dados incorretos!")
else:
    st.image("https://images.unsplash.com", use_container_width=True)
    st.title("🕊️ Guia Espírita")
    busca = st.text_input("🔍 O que você procura?", placeholder="Digite aqui...")

    if busca:
        try:
            # Lê a planilha bruta do GitHub
            df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
            
            termo = limpar_busca(busca)
            mascara = df.apply(lambda r: r.apply(limpar_busca).str.contains(termo)).any(axis=1)
            res = df[mascara]

            if not res.empty:
                for _, row in res.iterrows():
                    # ⚠️ SE O NOME SAIR INVERTIDO, TROQUE O 0 PELO 1 E O 1 PELO 0 ABAIXO:
                    v_fantasia = row.iloc[0] # Coluna A
                    v_nome_real = row.iloc[1] # Coluna B
                    
                    v_cidade   = row.iloc[2] # Coluna C
                    v_endereco = row.iloc[3] # Coluna D
                    v_palestra = row.iloc[4] # Coluna E
                    v_resp     = row.iloc[5] # Coluna F
                    v_celular  = row.iloc[6] # Coluna G

                    # Card Visual Estilo Placar
                    st.markdown(f"""
                        <div class="card-centro">
                            <div class="nome-grande">{v_nome_real}</div>
                            <div class="nome-fantasia">{v_fantasia}</div>
                            <div class="info-texto">👤 <b>Responsável:</b> {v_resp}</div>
                            <div class="info-texto">📍 {v_endereco}</div>
                            <div class="info-texto">🏙️ {v_cidade}</div>
                            {f'<div class="info-texto">🗓️ <b>Palestra:</b> {v_palestra}</div>' if v_palestra else ''}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if v_endereco:
                            # MAPS: Formato oficial Google Search (conserta erro DNS)
                            q = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                            st.link_button("🗺️ MAPS", f"https://www.google.com{q}")
                    with c2:
                        if v_celular:
                            # WHATSAPP: Agora com a barra / e código 55 (conserta erro DNS)
                            num = ''.join(filter(str.isdigit, v_celular))
                            if len(num) >= 10:
                                st.link_button("💬 WHATSAPP", f"https://wa.me{num}")
                    st.write("") 
            else: st.warning("Nenhum resultado.")
        except Exception as e: st.error(f"Erro: {e}")
