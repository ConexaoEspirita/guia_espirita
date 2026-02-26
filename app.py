import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { padding-top: 20px; }
    div[data-testid="stSidebar"] .st-emotion-cache-167909c { font-size: 1.2rem !important; font-weight: 600 !important; }
    .stApp { background: #f4f7f9; }
    
    .stTextInput > div > div > input {
        border: 3px solid #3B82F6 !important; border-radius: 12px !important;
        padding: 15px 20px !important; font-size: 16px !important; font-weight: 600 !important;
        background: linear-gradient(145deg, #ffffff, #f8fafc) !important;
        box-shadow: 0 4px 15px rgba(59,130,246,0.2) !important;
    }
    .titulo-principal { font-size: 28px !important; color: #1E3A8A !important; }
    .titulo-secundario { font-size: 20px !important; color: #1E3A8A !important; }
    
    .card-centro { background: white !important; padding: 25px; border-radius: 20px; 
                   box-shadow: 0 10px 30px rgba(0,0,0,0.12); margin-bottom: 25px; 
                   border-left: 12px solid #0047AB; position: relative; }
    .numero-badge { position: absolute; top: 15px; right: 20px; background: #f0f4f8; 
                    color: #7f8c8d; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 800; }
    .nome-centro { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800; display: block; }
    .nome-fantasia { color: #3B82F6 !important; font-size: 16px !important; font-style: italic; font-weight: 500; margin-top: 2px; display: block; }
    .palestras-verde { color: #065F46 !important; font-weight: 700; background: #D1FAE5; padding: 10px; border-radius: 10px; margin: 12px 0; border: 1px solid #10B981; }
    .info-linha { margin: 8px 0; font-size: 15px; color: #333 !important; }
    .label-bold { font-weight: 800; color: #0047AB; text-transform: uppercase; font-size: 13px; }
    .btn-row { display: flex; gap: 12px; margin-top: 20px; }
    .btn-link { text-decoration: none !important; color: white !important; padding: 14px; border-radius: 12px; font-weight: 800; text-align: center; flex: 1; display: inline-block; }
    .bg-wa { background-color: #25D366; }
    .bg-maps { background-color: #4285F4; }
</style>
""", unsafe_allow_html=True)

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
        whats_num_com_prefixo = "+55" + whats_num
        link_wa = f"https://wa.me/{whats_num_com_prefixo}"
    else:
        link_wa = "#"
    
    if end.strip():
        link_maps = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{end}, {cid}')}"
    else:
        link_maps = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{nome}, {cid}')}"
    
    st.markdown(f"""
    <div class="card-centro">
        <div class="numero-badge">#{index}</div>
        <div style="border-bottom: 2px solid #f0f2f6; padding-bottom: 12px; margin-bottom: 15px;">
            <span class="nome-centro">{nome} 🕊️</span>
            {f'<span class="nome-fantasia">{fantasia}</span>' if fantasia else ''}
        </div>
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

# --- LOGIN ---
if "logado" not in st.session_state: 
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🕊️ Guia Espírita")
    with st.form("login_guia"):
        u = st.text_input("E-mail")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("🔐 ACESSAR", use_container_width=True):
            st.session_state.logado = True
            st.rerun()
else:
    with st.sidebar:
        opcao = st.radio("Navegação:", 
                         ["🏠 Início", "🔎 Pesquisar Geral", "📍 Por Cidade", "📊 Admin", "🕊️ Frases", "🚪 Sair"], 
                         label_visibility="collapsed",
                         help="👆 Navegação principal do sistema")

    if opcao == "🚪 Sair":
        st.session_state.logado = False
        st.cache_data.clear()
        st.rerun()

    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()

    if opcao == "🔎 Pesquisar Geral":
        col1, col2 = st.columns([8,1])
        with col1:
            st.markdown('<h2 class="titulo-secundario">🔍 Pesquisar Geral</h2>', unsafe_allow_html=True)

        with col2:
            with st.popover("☰", help="Menu rápido"):
                if st.button("🔎 Pesquisar Geral", use_container_width=True):
                    st.rerun()
                if st.button("📍 Por Cidade", use_container_width=True):
                    st.rerun()
                if st.button("📊 Admin", use_container_width=True):
                    st.rerun()
                if st.button("🕊️ Frases", use_container_width=True):
                    st.rerun()

        termo = st.text_input("🔍 Digite pelo menos 4 letras para buscar:",
                              placeholder="Ex: Centro, João, São Paulo...",
                              help="Busca em nome, cidade e responsável")
