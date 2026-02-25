import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re
from datetime import datetime

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# SEU CSS ORIGINAL
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);}
.titulo-premium {background: linear-gradient(90deg, #0047AB, #1976D2);-webkit-background-clip: text;-webkit-text-fill-color: transparent;text-shadow: 0 4px 12px rgba(0,71,171,0.3);font-size: 2.5rem !important;font-weight: 800 !important;}
.card-centro {background: rgba(255,255,255,0.95);backdrop-filter: blur(10px);padding: 20px;border-radius: 20px;border: 1px solid rgba(0,71,171,0.1);box-shadow: 0 8px 32px rgba(0,71,171,0.15);margin-bottom: 16px;}
.nome-grande {color: #1E3A8A !important;font-size: 22px !important;font-weight: 800 !important;}
.nome-fantasia {color: #3B82F6 !important;font-size: 15px !important;font-weight: 600 !important;font-style: italic;}
.info-texto {color: #374151 !important;font-size: 13px !important;display: flex;align-items: center;gap: 6px;}
.palestras-verde {color: #10B981 !important; font-weight: 700 !important; font-size: 14px !important; background: rgba(16,185,129,0.15) !important; padding: 8px 14px !important; border-radius: 12px !important; border-left: 4px solid #10B981 !important; box-shadow: 0 2px 8px rgba(16,185,129,0.2) !important;}

/* Menu Lateral Azul */
[data-testid="stSidebar"] {background-color: #1E3A8A !important;}
[data-testid="stSidebar"] * {color: white !important;}

div.stButton > button {background: linear-gradient(135deg, #0047AB, #1E40AF) !important;color: white !important;border-radius: 12px !important;height: 50px !important;font-size: 16px !important;font-weight: 700 !important;}
#back-to-top-fixed {position: fixed !important; bottom: 30px !important; right: 30px !important; background: linear-gradient(135deg, #10B981, #059669) !important; color: white !important; border: none !important; border-radius: 50px !important; width: 60px !important; height: 60px !important; font-size: 24px !important; z-index: 9999; cursor: pointer;}
</style>""", unsafe_allow_html=True)

def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    return texto

# SESSION STATE ORIGINAL
if "usuarios" not in st.session_state: st.session_state.usuarios = []
if "logado" not in st.session_state: st.session_state.logado = False
if "usuario" not in st.session_state: st.session_state.usuario = ""

# --- TELA DE CADASTRO (IGUAL AO INÍCIO) ---
if not st.session_state.logado:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita - CADASTRO</h1>', unsafe_allow_html=True)
    col1, col2, col_btn = st.columns([1, 1, 0.8])
    with col1: nome = st.text_input("👤 Nome Completo")
    with col2: email = st.text_input("📧 E-mail")
    with col_btn:
        st.write("")
        if st.button("📝 CADASTRAR", use_container_width=True):
            if nome and email:
                st.session_state.logado = True
                st.session_state.usuario = nome
                st.rerun()

# --- ÁREA LOGADA COM MENU LATERAL ---
else:
    with st.sidebar:
        st.markdown(f"### Olá, {st.session_state.usuario}! 🕊️")
        st.divider()
        menu = st.radio("Escolha uma opção:", ["🔍 Busca Geral", "🏙️ Por Cidades", "🚪 Sair"])
        if menu == "🚪 Sair":
            st.session_state.logado = False
            st.rerun()

    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)

    # Carregar Dados
    try:
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        df = df.rename(columns={
            'NOME FANTASIA': 'Nome Fantasia', 'NOME': 'Nome Real / Razão Social',
            'CIDADE DO CENTRO ESPIRITA': 'Cidade', 'ENDERECO': 'Endereço',
            'PALESTRA PUBLICA': 'Palestra Pública', 'RESPONSAVEL': 'Responsável', 'CELULAR': 'Celular'
        })

        # LOGICA DE FILTRO
        if menu == "🏙️ Por Cidades":
            cidades_unificadas = sorted(df['Cidade'].dropna().unique())
            cidade_selecionada = st.selectbox("Selecione a cidade:", ["Todas"] + cidades_unificadas)
            resultados_df = df if cidade_selecionada == "Todas" else df[df['Cidade'] == cidade_selecionada]
        else:
            busca = st.text_input("🔍 Digite o que procura...", label_visibility="collapsed")
            termo_limpo = limpar_busca(busca)
            if termo_limpo:
                mask = df.apply(lambda r: termo_limpo in limpar_busca(' '.join(map(str, r.values))), axis=1)
                resultados_df = df[mask]
            else:
                resultados_df = pd.DataFrame()

        # EXIBIÇÃO DOS SEUS CARDS ORIGINAIS
        for idx, row in resultados_df.iterrows():
            st.markdown(f"""
            <div class="card-centro">
                <div class="nome-grande">{row['Nome Real / Razão Social']} 🕊️</div>
                <div class="nome-fantasia">{row['Nome Fantasia']}</div>
                <div class="palestras-verde">🗣️ PALESTRAS {row['Palestra Pública']}</div>
                <div class="info-texto">👤 <b>Responsável:</b> {row['Responsável']}</div>
                <div class="info-texto">📍 <b>Endereço:</b> {row['Endereço']}</div>
                <div class="info-texto">🏙️ <b>Cidade:</b> {row['Cidade']}</div>
            </div>""", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                query = urllib.parse.quote(f"{row['Endereço']}, {row['Cidade']}")
                st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}", use_container_width=True)
            with c2:
                numero = ''.join(filter(str.isdigit, str(row['Celular'])))
                if len(numero) >= 10:
                    st.link_button("💬 WhatsApp", f"https://wa.me/55{numero}", use_container_width=True)
            st.divider()

    except Exception as e:
        st.error(f"Erro: {e}")

# Botão voltar ao topo
st.markdown('<button onclick="window.scrollTo({top: 0, behavior: \'smooth\'})" id="back-to-top-fixed">⬆️</button>', unsafe_allow_html=True)
