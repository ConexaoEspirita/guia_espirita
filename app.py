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

# Função para remover acentos e deixar tudo minúsculo
def remover_acentos(txt):
    return ''.join(c for c in unicodedata.normalize('NFD', str(txt))
                  if unicodedata.category(c) != 'Mn').lower()

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
    
    busca = st.text_input("🔍 Digite o que procura:", placeholder="Ex: Geronimo")

    if busca:
        try:
            df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
            
            # FILTRO INTELIGENTE: Ignora acentos e maiúsculas
            termo_busca = remover_acentos(busca)
            mascara = df.apply(lambda r: r.apply(remover_acentos).str.contains(termo_busca)).any(axis=1)
            res = df[mascara]

            if not res.empty:
                for _, row in res.iterrows():
                    # MAPEAMENTO POR POSIÇÃO (A=0, B=1, C=2, D=3, E=4, F=5, G=6)
                    v_fantasia = row.iloc[0] if len(row) > 0 else ""
                    v_nome     = row.iloc[1] if len(row) > 1 else "Centro"
                    v_cidade   = row.iloc[2] if len(row) > 2 else ""
                    v_endereco = row.iloc[3] if len(row) > 3 else ""
                    v_responsavel = row.iloc[5] if len(row) > 5 else "Não informado"
                    v_celular  = row.iloc[6] if len(row) > 6 else ""

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
                            q_maps = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                            st.link_button("🗺️ MAPS", f"https://www.google.com{q_maps}")
                    with c2:
                        if v_celular:
                            num = ''.join(filter(str.isdigit, v_celular))
                            if len(num) >= 10:
                                st.link_button("💬 WHATSAPP", f"https://wa.me{num}")
                    st.write("") 
            else:
                st.warning(f"Nenhum resultado para '{busca}'.")
        except Exception as e:
            st.error(f"Erro ao ler a planilha: {e}")
    else:
        st.info("Digite um nome acima para pesquisar! 🙏")
