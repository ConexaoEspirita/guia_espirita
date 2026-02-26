import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# -------- CONTROLE DE PÁGINA --------
if "pagina" not in st.session_state:
    st.session_state.pagina = "🏠 Início"

# --- CSS ---
st.markdown("""
<style>
    .stApp { background: #f4f7f9; }
    .titulo-principal { font-size: 28px !important; color: #1E3A8A !important; }
    .titulo-secundario { font-size: 20px !important; color: #1E3A8A !important; }
</style>
""", unsafe_allow_html=True)

# -------- MENU SUPERIOR --------
col1, col2 = st.columns([9,1])

with col1:
    st.markdown('<h1 class="titulo-principal">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)

with col2:
    with st.popover("☰", help="Menu de navegação"):
        if st.button("🏠 Início", use_container_width=True):
            st.session_state.pagina = "🏠 Início"
            st.rerun()

        if st.button("🔎 Pesquisar Geral", use_container_width=True):
            st.session_state.pagina = "🔎 Pesquisar Geral"
            st.rerun()

        if st.button("📍 Por Cidade", use_container_width=True):
            st.session_state.pagina = "📍 Por Cidade"
            st.rerun()

        if st.button("📊 Admin", use_container_width=True):
            st.session_state.pagina = "📊 Admin"
            st.rerun()

        if st.button("🕊️ Frases", use_container_width=True):
            st.session_state.pagina = "🕊️ Frases"
            st.rerun()

st.divider()

# -------- CARREGAR DADOS --------
df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
df.columns = df.columns.str.strip()

def ajustar_texto(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def renderizar_card(row, index):
    nome = ajustar_texto(row.get('NOME', 'Centro Espírita'))
    fantasia = ajustar_texto(row.get('NOME FANTASIA', ''))
    end = ajustar_texto(row.get('ENDERECO', ''))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', ''))
    palestras = ajustar_texto(row.get('PALESTRA PUBLICA', 'Consulte'))
    resp = ajustar_texto(row.get('RESPONSAVEL', 'N/I'))
    
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    if len(whats_num) >= 10:
        link_wa = f"https://wa.me/+55{whats_num}"
    else:
        link_wa = "#"
    
    link_maps = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{end}, {cid}')}"
    
    st.markdown(f"""
    <div class="card-centro">
        <div class="numero-badge">#{index}</div>
        <span class="nome-centro">{nome} 🕊️</span>
        {f'<span class="nome-fantasia">{fantasia}</span>' if fantasia else ''}
        <div class="palestras-verde">🗣️ PALESTRAS: {palestras}</div>
        <div class="info-linha"><span class="label-bold">🏙️ Cidade:</span> {cid}</div>
        <div class="info-linha"><span class="label-bold">📍 Endereço:</span> {end}</div>
        <div class="info-linha"><span class="label-bold">👤 Responsável:</span> {resp}</div>
        <div class="btn-row">
            <a href="{link_maps}" target="_blank" class="btn-link bg-maps">📍 VER MAPA</a>
            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WHATSAPP</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------- PÁGINAS --------

if st.session_state.pagina == "🏠 Início":
    st.info("👆 Clique no ☰ para navegar pelo sistema.")

elif st.session_state.pagina == "🔎 Pesquisar Geral":
    st.markdown('<h2 class="titulo-secundario">🔍 Pesquisar Geral</h2>', unsafe_allow_html=True)

    termo = st.text_input(
        "🔍 Digite pelo menos 4 letras para buscar:",
        placeholder="Ex: Centro, João, São Paulo...",
        help="Busca em nome, cidade e responsável"
    )

    if termo and len(termo) >= 4:
        palavras = termo.lower().split()

        def normalizar(t):
            if pd.isna(t): return ""
            return str(t).lower()

        def checar(row):
            texto = normalizar(" ".join(row.astype(str)))
            return all(p in texto for p in palavras)

        res = df[df.apply(checar, axis=1)]

        if len(res) > 0:
            st.success(f"✅ Encontrados {len(res)} centro(s)")
            for i, (_, row) in enumerate(res.iterrows(), 1):
                renderizar_card(row, i)
        else:
            st.warning("❌ Nenhum resultado encontrado.")

elif st.session_state.pagina == "📍 Por Cidade":
    st.markdown('<h2 class="titulo-secundario">Buscar por Cidade</h2>', unsafe_allow_html=True)

    cidades = sorted(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique())
    sel = st.selectbox(
        "Selecione a cidade:",
        ["-- Selecione uma cidade --"] + cidades,
        help="Escolha sua cidade para ver os centros espíritas"
    )

    if sel != "-- Selecione uma cidade --":
        res = df[df['CIDADE DO CENTRO ESPIRITA'] == sel]
        st.success(f"✅ Encontrados {len(res)} centro(s) em {sel}")
        for i, (_, row) in enumerate(res.iterrows(), 1):
            renderizar_card(row, i)

elif st.session_state.pagina == "📊 Admin":
    st.markdown('<h2 class="titulo-secundario">📊 Painel Administrativo</h2>', unsafe_allow_html=True)
    st.metric("🏠 Total Centros", len(df))
    st.metric("📍 Cidades Únicas", len(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique()))

elif st.session_state.pagina == "🕊️ Frases":
    st.markdown('<h2 class="titulo-secundario">🕊️ Frases Espíritas</h2>', unsafe_allow_html=True)
    st.markdown("> Fora da caridade não há salvação. — Allan Kardec")
