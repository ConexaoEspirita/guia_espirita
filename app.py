import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Guia Espírita", layout="wide")

# =========================
# SESSION STATE
# =========================
if "pagina" not in st.session_state:
    st.session_state["pagina"] = None
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "termo_pesquisa" not in st.session_state:
    st.session_state["termo_pesquisa"] = ""

# =========================
# CSS
# =========================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

[data-testid="stStatusWidget"], 
[data-testid="stToolbar"], 
[data-testid="stDecoration"],
.viewerBadge_container__1QSob,
.styles_viewerBadge__1yB5_ {
    display: none !important;
}

.stApp { background: #f4f7f9; }
.titulo-grande { font-size: 32px; font-weight: 800; margin-bottom: 8px; }

.card-centro { 
    background: white;
    padding: 25px;
    border-radius: 20px; 
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.12); 
    border-left: 12px solid #0060D0;
    position: relative;
}

.btn-link { 
    text-decoration:none; 
    color:white !important; 
    padding:10px; 
    border-radius:10px; 
    font-weight:700; 
    text-align:center; 
    display:inline-block; 
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES
# =========================
def ajustar(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def normalize_text(text):
    if pd.isna(text): return ""
    return unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8').lower()

def renderizar_card(row, index):
    nome = ajustar(row.get('NOME', 'Centro Espírita'))
    fantasia = ajustar(row.get('NOME FANTASIA'))
    endereco = ajustar(row.get('ENDERECO'))
    cidade = ajustar(row.get('CIDADE DO CENTRO ESPIRITA'))
    palestra = ajustar(row.get('PALESTRA PUBLICA'))
    responsavel = ajustar(row.get('RESPONSAVEL'))
    numero = "".join(filter(str.isdigit, str(row.get('CELULAR'))))

    query = urllib.parse.quote(f"{endereco}, {cidade}")
    link_maps = f"https://www.google.com/maps/search/?api=1&query={query}"
    link_wa = f"https://wa.me/55{numero}" if len(numero)>=10 else "#"

    st.markdown(f"""
    <div class="card-centro">
        <div style="position:absolute; top:10px; right:15px; font-size:12px; color:#6B7280; background:rgba(255,255,255,0.8); padding:2px 6px; border-radius:12px; font-weight:500;">#{index}</div>
        <div style="color: #1E3A8A; font-size: 22px; font-weight: 800;">{nome} 🕊️</div>
        {"<div style='color: #3B82F6; font-style: italic;'>" + fantasia + "</div>" if fantasia else ""}
        <div style="color:#065F46; font-weight:700; background:#D1FAE5; padding:8px; border-radius:8px; margin:10px 0;">🗣️ PALESTRA: {palestra}</div>
        <div>👤 <b>Responsável:</b> {responsavel}</div>
        <div>🏙️ <b>Cidade:</b> {cidade}</div>
        <div>📍 <b>Endereço:</b> {endereco}</div>
        <div style="margin-top:15px; display:flex; gap:10px;">
            <a href="{link_maps}" target="_blank" class="btn-link" style="background:#4285F4;">📍 Maps</a>
            <a href="{link_wa}" target="_blank" class="btn-link" style="background:#25D366;">WhatsApp</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# LOGIN
# =========================
if not st.session_state.get("logado", False):

    st.markdown("<div style='text-align: center; color: #60A5FA; font-size: 32px; font-weight: 800; margin-bottom: 30px;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🚪 Entrar", "✨ Cadastrar"])

    with tab1:
        with st.form("login"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                st.session_state["logado"] = True
                st.rerun()

    with tab2:
        with st.form("cadastro"):
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Cadastrar", use_container_width=True):
                st.session_state["logado"] = True
                st.rerun()

# =========================
# APP PRINCIPAL
# =========================
else:

    @st.cache_data
    def carregar_dados():
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        return df

    df = carregar_dados()

    pagina = st.session_state.get("pagina")

    if pagina is None:

        st.markdown("<div class='titulo-grande' style='color: #60A5FA; text-align: center;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            if st.button("🔎 Busca Avançada", use_container_width=True):
                st.session_state["pagina"] = "pesquisar"
                st.rerun()

            if st.button("📍 Por Cidade", use_container_width=True):
                st.session_state["pagina"] = "cidade"
                st.rerun()

        with c2:
            if st.button("📊 Admin", use_container_width=True):
                st.session_state["pagina"] = "admin"
                st.rerun()

            if st.button("🕊️ Frases", use_container_width=True):
                st.session_state["pagina"] = "frases"
                st.rerun()

        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear()
            st.cache_data.clear()
            st.rerun()

    else:

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬅️ VOLTAR", use_container_width=True):
                st.session_state["pagina"] = None
                st.rerun()

        with col2:
            if st.button("🔄 LIMPAR", use_container_width=True):
                st.session_state["termo_pesquisa"] = ""
                st.rerun()

        if pagina == "admin":

            admin_senha = st.text_input("Senha Admin:", type="password")

            if admin_senha == "estudantesabio2026":

                agora = datetime.datetime.now()

                linha1 = st.columns(2)
                linha1[0].metric("🕊️ Total de Centros", len(df))
                linha1[1].metric("🏙️ Cidades Únicas", df["CIDADE DO CENTRO ESPIRITA"].nunique())

                st.markdown("---")

                linha2 = st.columns(4)
                linha2[0].metric("📅 Data", agora.strftime("%d/%m/%Y"))
                linha2[1].metric("🕐 Hora", agora.strftime("%H:%M"))
                linha2[2].metric("⏱️ Segundos", agora.strftime("%S"))
                linha2[3].metric("📊 Total Centros", len(df))

                st.caption(f"Atualizado em tempo real: {agora.strftime('%d/%m/%Y %H:%M:%S')}")

            else:
                st.warning("❌ Senha Admin necessária")
