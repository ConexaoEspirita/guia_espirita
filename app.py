import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

# --- Configuração da página ---
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS ---
st.markdown("""
<style>
.block-container { padding-top: 3rem !important; }
.stApp { background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%); }
.titulo-premium { background: linear-gradient(90deg, #0047AB, #1976D2);
-webkit-background-clip: text; -webkit-text-fill-color: transparent;
text-shadow: 0 4px 12px rgba(0,71,171,0.3);
font-size: 2.5rem !important; font-weight: 800 !important; margin: 0; padding-bottom: 1rem; }

.search-container { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.search-container input { flex: 1; padding: 8px 12px; font-size: 16px; border-radius: 8px; border: 2px solid #1E3A8A; outline: none; }
.search-container button { padding: 8px 16px; font-size: 16px; background-color: #0047AB; color: white; border: none; border-radius: 8px; cursor: pointer; }
.search-container button:hover { background-color: #1E40AF; }

.card-centro { background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
padding: 20px; border-radius: 20px; border: 1px solid rgba(0,71,171,0.1);
box-shadow: 0 8px 32px rgba(0,71,171,0.15); margin-bottom: 16px; position: relative; }
.nome-grande { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800 !important; }
.nome-fantasia { color: #3B82F6 !important; font-size: 15px !important; font-weight: 600 !important; font-style: italic; }
.info-texto { color: #374151 !important; font-size: 13px !important; display: flex; align-items: center; gap: 6px; }
.palestras-verde { color: #10B981 !important; font-weight: 700 !important; font-size: 14px !important;
background: rgba(16,185,129,0.15) !important; padding: 8px 14px !important;
border-radius: 12px !important; border-left: 4px solid #10B981 !important; box-shadow: 0 2px 8px rgba(16,185,129,0.2) !important; }
.num-card { position: absolute; top: 8px; right: 12px; font-size: 12px; font-weight: 600; color: rgba(0,0,0,0.4); }
</style>
""", unsafe_allow_html=True)

# --- Conexão Supabase ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- Sessão ---
if "logado" not in st.session_state: st.session_state.logado = True  # assume logado para teste
if "cards_visiveis" not in st.session_state: st.session_state.cards_visiveis = {}

# --- Função de limpeza ---
def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    texto = re.sub(r'[^a-zA-Z0-9\s]', '', texto)
    return texto

# --- Carregar planilha ---
try:
    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()
except:
    st.error("Erro ao carregar planilha")
    df = pd.DataFrame()

# --- Barra de pesquisa funcional ---
st.markdown('<div class="search-container">', unsafe_allow_html=True)
termo_busca = st.text_input("", placeholder="🔍 Pesquise por nome, cidade ou palavra...", key="busca_input")
pesquisar = st.button("Pesquisar")
st.markdown('</div>', unsafe_allow_html=True)

# --- Resultados da pesquisa ---
resultados = []
if pesquisar and termo_busca.strip():
    termo_limpo = limpar_busca(termo_busca)
    for idx, row in df.iterrows():
        texto_row = " ".join([limpar_busca(str(row.get(c,""))) for c in ['NOME FANTASIA','NOME','CIDADE DO CENTRO ESPIRITA','ENDERECO','RESPONSAVEL','PALESTRA PUBLICA']])
        if termo_limpo in texto_row:
            resultados.append(row.to_dict())

# --- Menu Hamburger ---
with st.expander("☰ Menu", expanded=False):
    st.markdown("### Admin")
    st.markdown("### Cidades")
    cidades_unicas = sorted(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique())
    for cidade in cidades_unicas:
        count_centro = len(df[df['CIDADE DO CENTRO ESPIRITA']==cidade])
        if cidade not in st.session_state.cards_visiveis:
            st.session_state.cards_visiveis[cidade] = False

        def toggle_cidade(cidade=cidade):
            st.session_state.cards_visiveis[cidade] = not st.session_state.cards_visiveis[cidade]

        st.button(f"{cidade} ({count_centro})", key=f"btn_{cidade}", on_click=toggle_cidade)

        if st.session_state.cards_visiveis[cidade]:
            centros = df[df['CIDADE DO CENTRO ESPIRITA']==cidade].reset_index()
            for idx, row in centros.iterrows():
                v_nome_real = row.get('NOME','Centro Espírita') + " 🕊️"
                v_fantasia = row.get('NOME FANTASIA','N/I')
                v_endereco = row.get('ENDERECO','N/I')
                v_resp = row.get('RESPONSAVEL','N/I')
                v_celular = str(row.get('CELULAR',''))
                v_palestras = row.get('PALESTRA PUBLICA','')
                v_cidade = row.get('CIDADE DO CENTRO ESPIRITA','')
                query = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                numero = ''.join(filter(str.isdigit, v_celular))

                st.markdown(f"""
                <div class="card-centro">
                    <div class="num-card">{idx+1}</div>
                    <div class="nome-grande">{v_nome_real}</div>
                    <div class="nome-fantasia">{v_fantasia}</div>
                    <div class="palestras-verde">🗣️ PALESTRAS {v_palestras}</div>
                    <div class="info-texto">👤 <b>Responsável:</b> {v_resp}</div>
                    <div class="info-texto">📍 <b>Endereço:</b> {v_endereco}</div>
                    <div class="info-texto">🏙️ <b>Cidade:</b> {v_cidade}</div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    if v_endereco != 'N/I':
                        st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}", use_container_width=True)
                with col2:
                    if len(numero) >= 10:
                        st.link_button("💬 WhatsApp", f"https://wa.me/55{numero}", use_container_width=True)

            st.button(f"− Recolher {cidade}", key=f"recolher_{cidade}", on_click=toggle_cidade)

# --- Exibir resultados da pesquisa ---
if resultados:
    st.success(f"✨ Encontrados {len(resultados)} centros!")
    for idx, row in enumerate(resultados):
        v_nome_real = row.get('NOME','Centro Espírita') + " 🕊️"
        v_fantasia = row.get('NOME FANTASIA','N/I')
        v_endereco = row.get('ENDERECO','N/I')
        v_resp = row.get('RESPONSAVEL','N/I')
        v_celular = str(row.get('CELULAR',''))
        v_palestras = row.get('PALESTRA PUBLICA','')
        v_cidade = row.get('CIDADE DO CENTRO ESPIRITA','')
        query = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
        numero = ''.join(filter(str.isdigit, v_celular))

        st.markdown(f"""
        <div class="card-centro">
            <div class="num-card">{idx+1}</div>
            <div class="nome-grande">{v_nome_real}</div>
            <div class="nome-fantasia">{v_fantasia}</div>
            <div class="palestras-verde">🗣️ PALESTRAS {v_palestras}</div>
            <div class="info-texto">👤 <b>Responsável:</b> {v_resp}</div>
            <div class="info-texto">📍 <b>Endereço:</b> {v_endereco}</div>
            <div class="info-texto">🏙️ <b>Cidade:</b> {v_cidade}</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if v_endereco != 'N/I':
                st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}", use_container_width=True)
        with col2:
            if len(numero) >= 10:
                st.link_button("💬 WhatsApp", f"https://wa.me/55{numero}", use_container_width=True)
