import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata

# 1. Configuração e Estilo "Placar de Futebol"
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="centered")

# LIMPA O CACHE PARA FORÇAR A MUDANÇA
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
    
    /* Botões Lado a Lado no Celular */
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

def limpar_texto(txt):
    return ''.join(c for c in unicodedata.normalize('NFD', str(txt)) if unicodedata.category(c) != 'Mn').lower()

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
    busca = st.text_input("🔍 O que você procura?", placeholder="Digite aqui...")

    if busca:
        try:
            # LÊ A PLANILHA DO GITHUB
            df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
            
            # FILTRO QUE IGNORA ACENTOS E MAIÚSCULAS
            termo = limpar_texto(busca)
            mascara = df.apply(lambda r: r.apply(limpar_texto).str.contains(termo)).any(axis=1)
            res = df[mascara]

            if not res.empty:
                for _, row in res.iterrows():
                    # --- CONFIGURAÇÃO MANUAL DAS COLUNAS (Ajuste aqui se inverter) ---
                    # 0=A, 1=B, 2=C, 3=D, 4=E, 5=F, 6=G
                    p_fantasia = row.iloc if len(row) > 0 else "" # COLUNA A
                    p_nome_real = row.iloc if len(row) > 1 else "Centro" # COLUNA B
                    p_cidade   = row.iloc if len(row) > 2 else "" # COLUNA C
                    p_endereco = row.iloc if len(row) > 3 else "" # COLUNA D
                    p_palestra = row.iloc if len(row) > 4 else "" # COLUNA E
                    p_respons  = row.iloc if len(row) > 5 else "" # COLUNA F
                    p_celular  = row.iloc if len(row) > 6 else "" # COLUNA G

                    # Card Visual Estilo Placar
                    st.markdown(f"""
                        <div class="card-centro">
                            <div class="nome-grande">{p_nome_real}</div>
                            <div class="nome-fantasia">{p_fantasia}</div>
                            <div class="info-texto">👤 <b>Responsável:</b> {p_respons}</div>
                            <div class="info-texto">📍 {p_endereco}</div>
                            <div class="info-texto">🏙️ {p_cidade}</div>
                            <div class="info-texto">🗓️ <b>Palestra:</b> {p_palestra}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if p_endereco:
                            # MAPS SEM ERRO: Formato universal
                            q_maps = urllib.parse.quote(f"{p_endereco}, {p_cidade}")
                            st.link_button("🗺️ MAPS", f"https://www.google.com{q_maps}")
                    with col2:
                        if p_celular:
                            # WHATSAPP SEM ERRO: Com a barra / e código 55
                            so_numeros = ''.join(filter(str.isdigit, p_celular))
                            if len(so_numeros) >= 10:
                                st.link_button("💬 WHATSAPP", f"https://wa.me{so_numeros}")
                    st.write("") 
            else:
                st.warning("Nenhum resultado.")
        except Exception as e:
            st.error(f"Erro ao carregar o Guia: {e}")
    else:
        st.info("Digite para pesquisar! 🙏")
