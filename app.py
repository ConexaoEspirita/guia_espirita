import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# =========================
# CSS MENU FIXO REAL
# =========================
st.markdown("""
<style>
    [data-testid="stArrowBack"] { display: none !important; }
    section[data-testid="stSidebar"] > div { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    .menu-container {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        z-index: 9999 !important;
        background: rgba(30, 64, 175, 0.95) !important;
        backdrop-filter: blur(15px) !important;
        padding: 15px 20px !important;
        border-radius: 0 0 20px 20px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
    }

    .block-container {
        padding-top: 120px !important;
    }

    .stApp { 
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%) !important;
        background-attachment: fixed !important;
    }

    .card-centro { 
        background: white !important;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
        margin-bottom: 25px;
        border-left: 12px solid #0047AB;
        position: relative;
    }

    .numero-badge {
        position: absolute;
        top: 15px;
        right: 20px;
        background: #f0f4f8;
        color: #7f8c8d;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 800;
    }

    .nome-centro {
        color: #1E3A8A !important;
        font-size: 22px !important;
        font-weight: 800;
        display: block;
    }

    .nome-fantasia {
        color: #3B82F6 !important;
        font-size: 16px !important;
        font-style: italic;
        font-weight: 500;
        margin-top: 2px;
        display: block;
    }

    .palestras-verde {
        color: #065F46 !important;
        font-weight: 700;
        background: #D1FAE5;
        padding: 10px;
        border-radius: 10px;
        margin: 12px 0;
        border: 1px solid #10B981;
    }

    .info-linha {
        margin: 8px 0;
        font-size: 15px;
        color: #333 !important;
    }

    .label-bold {
        font-weight: 800;
        color: #0047AB;
        text-transform: uppercase;
        font-size: 13px;
    }

    .btn-row {
        display: flex;
        gap: 12px;
        margin-top: 20px;
    }

    .btn-link {
        text-decoration: none !important;
        color: white !important;
        padding: 14px;
        border-radius: 12px;
        font-weight: 800;
        text-align: center;
        flex: 1;
        display: inline-block;
    }

    .bg-wa { background-color: #25D366; }
    .bg-maps { background-color: #4285F4; }
</style>
""", unsafe_allow_html=True)


# =========================
# FUNÇÕES
# =========================
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
    link_wa = f"https://wa.me/+55{whats_num}" if len(whats_num) >= 10 else "#"

    nome_google = ajustar_texto(row.get('NOME_GOOGLE_MAPS', ''))
    if nome_google:
        query_maps = urllib.parse.quote(nome_google)
    else:
        endereco_limpo = re.sub(r'[,\\s]+', ', ', end)[:100]
        query_maps = urllib.parse.quote(f"{endereco_limpo}, {cid}")

    link_maps = f"https://www.google.com/maps/search/?api=1&query={query_maps}"

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


# =========================
# SESSION STATE
# =========================
if "menu_aberto" not in st.session_state:
    st.session_state.menu_aberto = False
if "pagina" not in st.session_state:
    st.session_state.pagina = None
if "logado" not in st.session_state:
    st.session_state.logado = False


# =========================
# LOGIN
# =========================
if not st.session_state.logado:

    st.title("🕊️ Guia Espírita")

    nome = st.text_input("Nome")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        st.session_state.logado = True
        st.session_state.nome_usuario = nome
        st.rerun()

# =========================
# SISTEMA
# =========================
else:

    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()

    st.markdown('<div class="menu-container">', unsafe_allow_html=True)

    if st.button("📋 Menu", use_container_width=True):
        st.session_state.menu_aberto = not st.session_state.menu_aberto
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.menu_aberto:
        if st.button("🔎 Pesquisar Geral"):
            st.session_state.pagina = "pesquisar"
        if st.button("📍 Por Cidade"):
            st.session_state.pagina = "cidade"
        if st.button("📊 Admin"):
            st.session_state.pagina = "admin"
        if st.button("🕊️ Frases"):
            st.session_state.pagina = "frases"
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    pagina = st.session_state.get("pagina")

    if pagina == "admin":
        st.subheader("📊 Admin")
        st.metric("Total Centros", len(df))

    elif pagina == "frases":
        st.subheader("🕊️ Frases")
        st.markdown("> **Fora da caridade não há salvação.** — Allan Kardec")
