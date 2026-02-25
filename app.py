import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- PERSISTÊNCIA DE LOGIN (NÃO DESCONECTA NA ATUALIZAÇÃO) ---
if "logado" not in st.session_state:
    st.session_state.logado = False

@st.cache_data(ttl=3600)  # 1 hora de validade
def get_login_status():
    return st.session_state.logado

if get_login_status():
    st.session_state.logado = True

# --- CSS PREMIUM: MENU GRANDE, CARDS COM SOMBRA E ITALICO ---
st.markdown("""
<style>
    /* Menu Lateral com Letra Grande */
    [data-testid="stSidebar"] { padding-top: 35px; }
    div[data-testid="stMarkdownContainer"] p { font-size: 20px !important; font-weight: 700 !important; color: #1E3A8A; }
    
    .stApp { background: #f4f7f9; }
    
    /* Card com Sombra e Design Limpo */
    .card-centro { 
        background: white !important; padding: 25px; border-radius: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.15); 
        margin-bottom: 25px; border-left: 12px solid #0047AB; 
    }
    
    .header-card { border-bottom: 2px solid #f0f2f6; padding-bottom: 12px; margin-bottom: 15px; }
    .linha-topo { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
    .tag-cidade { 
        background: #0047AB; color: white !important; padding: 5px 12px; 
        border-radius: 8px; font-weight: 800; font-size: 13px; text-transform: uppercase;
    }
    .nome-centro { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800; margin: 0; }
    
    /* Nome Fantasia em Itálico logo abaixo */
    .nome-fantasia { 
        color: #3B82F6 !important; font-size: 17px !important; 
        font-weight: 500 !important; font-style: italic !important; 
        margin-top: 4px; display: block; 
    }
    
    .palestras-verde { 
        color: #065F46 !important; font-weight: 700; background: #D1FAE5; 
        padding: 10px; border-radius: 10px; margin: 12px 0; border: 1px solid #10B981;
    }
    
    .info-linha { margin: 8px 0; font-size: 15px; color: #333 !important; }
    .label-bold { font-weight: 800; color: #0047AB; }
    
    .btn-row { display: flex; gap: 12px; margin-top: 20px; }
    .btn-link { 
        text-decoration: none !important; color: white !important; 
        padding: 14px; border-radius: 12px; font-weight: 800; 
        text-align: center; flex: 1; display: inline-block;
    }
    .bg-wa { background-color: #25D366; }
    .bg-maps { background-color: #4285F4; }
</style>
""", unsafe_allow_html=True)

def ajustar_texto(txt):
    if pd.isna(txt): return ""
    return str(txt).strip()

def renderizar_card(row):
    nome = ajustar_texto(row.get('NOME', 'Centro Espírita'))
    fantasia = ajustar_texto(row.get('NOME FANTASIA', ''))
    end = ajustar_texto(row.get('ENDERECO', 'Não informado'))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', 'Não informado'))
    palestras = ajustar_texto(row.get('PALESTRA PUBLICA', 'Consulte a casa'))
    resp = ajustar_texto(row.get('RESPONSAVEL', 'N/I'))
    
    # WhatsApp CORRIGIDO ✅
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    if len(whats_num) >= 10:
        whats_num = "+55" + whats_num  # Brasil
        link_wa = f"https://wa.me/{whats_num}"
    else:
        link_wa = "#"
    
    # Maps CORRIGIDO ✅
    query_maps = urllib.parse.quote(f"{nome}, {end}, {cid}")
    link_maps = f"https://www.google.com/maps/search/?api=1&query={query_maps}"

    # Bloco do Fantasia (só aparece se existir)
    html_fantasia = f'<span class="nome-fantasia">✨ {fantasia}</span>' if fantasia else ""

    st.markdown(f"""
    <div class="card-centro">
        <div class="header-card">
            <div class="linha-topo">
                <span class="tag-cidade">🏙️ {cid}</span>
                <span class="nome-centro">{nome} 🕊️</span>
            </div>
            {html_fantasia}
        </div>
        <div class="palestras-verde">🗣️ PALESTRAS: {palestras}</div>
        <div class="info-linha"><span class="label-bold">📍 ENDEREÇO:</span> {end}</div>
        <div class="info-linha"><span class="label-bold">👤 RESPONSÁVEL:</span> {resp}</div>
        <div class="btn-row">
            <a href="{link_maps}" target="_blank" class="btn-link bg-maps">📍 GOOGLE MAPS</a>
            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WHATSAPP</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
if not st.session_state.logado:
    st.title("🕊️ Guia Espírita")
    with st.form("login_app"):
        u = st.text_input("E-mail")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR"):
            st.session_state.logado = True
            st.rerun()
else:
    with st.sidebar:
        st.markdown("### ☰ MENU")
        opcao = st.radio("Selecione:", ["🏠 Início", "🔎 Pesquisar Geral", "📍 Por Cidade", "🚪 Sair"])
        if opcao == "🚪 Sair":
            st.session_state.logado = False
            st.cache_data.clear()  # Limpa cache na saída
            st.rerun()

    try:
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"Erro no Excel: {e}")
        st.stop()

    if opcao == "🏠 Início":
        st.title("🕊️ Guia Espírita")
        st.info("Abra o menu lateral para iniciar sua busca.")

    elif opcao == "🔎 Pesquisar Geral":
        termo = st.text_input("Busca por nome, cidade ou palavra-chave:")
        if termo:
            mask = df.astype(str).apply(lambda x: x.str.contains(termo, case=False)).any(axis=1)
            for _, row in df[mask].iterrows():
                renderizar_card(row)

    elif opcao == "📍 Por Cidade":
        col_cid = 'CIDADE DO CENTRO ESPIRITA'
        cidades = sorted(df[col_cid].dropna().unique())
        escolha = st.selectbox("Selecione a cidade:", ["-- Selecione --"] + cidades)
        if escolha != "-- Selecione --":
            for _, row in df[df[col_cid] == escolha].iterrows():
                renderizar_card(row)
