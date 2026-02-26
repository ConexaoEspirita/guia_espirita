import streamlit as st
import pandas as pd
import urllib.parse
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide", initial_sidebar_state="collapsed")

# --- CSS COMPLETO (SÓ ESCONDE O QUE É NECESSÁRIO) ---
st.markdown("""
<style>
header[data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
.block-container { padding-top: 1rem !important; }
.stApp { background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%) !important; }
.card-centro { 
    background: white !important; padding: 25px; border-radius: 20px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.12); margin-bottom: 25px; 
    border-left: 12px solid #0047AB; position: relative;
}
.numero-badge { position: absolute; top: 15px; right: 20px; background: #f0f4f8; color: #7f8c8d; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 800; }
.nome-centro { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800; display: block; }
.nome-fantasia { color: #3B82F6 !important; font-size: 16px !important; font-style: italic; font-weight: 500; margin-top: 2px; display: block; }
.palestras-verde { color: #065F46 !important; font-weight: 700; background: #D1FAE5; padding: 10px; border-radius: 10px; margin: 12px 0; border: 1px solid #10B981; }
.btn-row { display: flex; gap: 12px; margin-top: 20px; }
.btn-link { text-decoration: none !important; color: white !important; padding: 14px; border-radius: 12px; font-weight: 800; text-align: center; flex: 1; display: inline-block; }
.bg-wa { background-color: #25D366; }
.bg-maps { background-color: #4285F4; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
def ajustar_texto(txt): return str(txt).strip() if pd.notna(txt) else ""

def remover_acentos(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower()
    return re.sub(r'[àáâãäå]', 'a', re.sub(r'[èéêë]', 'e', re.sub(r'[ìíîï]', 'i', re.sub(r'[òóôõö]', 'o', re.sub(r'[ùúûü]', 'u', texto)))))

def criar_link_maps(row):
    nome_g = ajustar_texto(row.get('NOME_GOOGLE_MAPS', ''))
    end = ajustar_texto(row.get('ENDERECO', ''))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', ''))
    query = f"{nome_g if nome_g else end}, {cid}, SP"
    return f"https://www.google.com{urllib.parse.quote(query)}"

def renderizar_card(row, index):
    nome = ajustar_texto(row.get('NOME', 'Centro Espírita'))
    fantasia = ajustar_texto(row.get('NOME FANTASIA', ''))
    palestras = ajustar_texto(row.get('PALESTRA PUBLICA', 'Consulte'))
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    link_wa = f"https://wa.me{whats_num}" if len(whats_num) >= 10 else "#"

    st.markdown(f"""
    <div class="card-centro">
        <div class="numero-badge">#{index}</div>
        <span class="nome-centro">{nome} 🕊️</span>
        {f'<span class="nome-fantasia">{fantasia}</span>' if fantasia else ''}
        <div class="palestras-verde">🗣️ PALESTRAS: {palestras}</div>
        <div style="color:#333; margin-bottom:10px;"><b>📍 Endereço:</b> {ajustar_texto(row.get('ENDERECO', ''))}, {ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', ''))}</div>
        <div class="btn-row">
            <a href="{criar_link_maps(row)}" target="_blank" class="btn-link bg-maps">📍 MAPA</a>
            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WhatsApp</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- LOGIN E NAVEGAÇÃO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "pagina" not in st.session_state: st.session_state.pagina = None
if "menu_aberto" not in st.session_state: st.session_state.menu_aberto = False

if not st.session_state.logado:
    st.title("🕊️ Guia Espírita - Login")
    with st.form("login_guia"):
        st.text_input("👤 E-mail")
        st.text_input("🔒 Senha", type="password")
        if st.form_submit_button("🚀 ACESSAR", use_container_width=True):
            st.session_state.logado = True
            st.rerun()
else:
    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()

    # MENU SUPERIOR
    c1, c2 = st.columns([3,1])
    with c1: st.title("🕊️ Guia Espírita")
    with c2: 
        if st.button("📋 MENU", use_container_width=True):
            st.session_state.menu_aberto = not st.session_state.menu_aberto
            if not st.session_state.menu_aberto: st.session_state.pagina = None
            st.rerun()

    if st.session_state.menu_aberto:
        st.markdown("---")
        m1, m2 = st.columns(2)
        with m1:
            if st.button("🔎 Pesquisar", use_container_width=True): st.session_state.pagina = "busca"; st.session_state.menu_aberto = False; st.rerun()
        with m2:
            if st.button("📍 Cidades", use_container_width=True): st.session_state.pagina = "cidade"; st.session_state.menu_aberto = False; st.rerun()
        with m1:
            if st.button("🕊️ Frases", use_container_width=True): st.session_state.pagina = "frases"; st.session_state.menu_aberto = False; st.rerun()
        with m2:
            if st.button("🚪 Sair", use_container_width=True): st.session_state.clear(); st.rerun()
        st.markdown("---")

    # CONTEÚDO
    p = st.session_state.pagina
    if p == "busca":
        t = st.text_input("Busque por nome ou parte dele:")
        if len(t) >= 3:
            res = df[df.apply(lambda r: t.lower() in str(r.values).lower(), axis=1)]
            for i, (_, r) in enumerate(res.iterrows(), 1): renderizar_card(r, i)

    elif p == "cidade":
        counts = df['CIDADE DO CENTRO ESPIRITA'].value_counts().to_dict()
        opts = [f"{c} ({q})" for c, q in sorted(counts.items())]
        sel = st.selectbox("Escolha a cidade:", ["-- Selecione --"] + opts)
        if sel != "-- Selecione --":
            cid_nome = re.sub(r'\s\(\d+\)$', '', sel)
            res = df[df['CIDADE DO CENTRO ESPIRITA'] == cid_nome]
            for i, (_, r) in enumerate(res.iterrows(), 1): renderizar_card(r, i)

    elif p == "frases":
        st.info('"Fora da caridade não há salvação." - Allan Kardec')
        st.info('"Tudo o que é teu virá ter contigo." - Chico Xavier')
    
    elif not st.session_state.menu_aberto:
        st.info("Toque no MENU para começar! 🕊️")
