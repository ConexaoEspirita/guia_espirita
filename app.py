import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS PREMIUM: MENU AMPLIADO E CARDS COM SOMBRA ---
st.markdown("""
<style>
    /* Aumenta a letra do Menu Lateral (Radio buttons) */
    [data-testid="stSidebar"] { padding-top: 35px; }
    [data-testid="stSidebar"] .st-emotion-cache-167909c { font-size: 1.2rem !important; font-weight: 600 !important; }
    
    /* Ajuste específico para os labels do rádio no menu */
    div[data-testid="stMarkdownContainer"] p { font-size: 18px !important; font-weight: 600 !important; color: #1E3A8A; }
    
    .stApp { background: #f4f7f9; }
    
    /* Card com Sombra Intensa */
    .card-centro { 
        background: white !important; padding: 25px; border-radius: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.15); 
        margin-bottom: 25px; 
        border-left: 12px solid #0047AB; 
        color: #1e1e1e !important;
    }
    
    .header-card { 
        display: flex; align-items: center; gap: 10px; 
        border-bottom: 2px solid #f0f2f6; padding-bottom: 12px; margin-bottom: 15px; 
    }
    .tag-cidade { 
        background: #0047AB; color: white !important; padding: 5px 12px; 
        border-radius: 8px; font-weight: 800; font-size: 13px; text-transform: uppercase;
        white-space: nowrap;
    }
    .nome-centro { color: #1E3A8A !important; font-size: 20px !important; font-weight: 800; line-height: 1.2; }
    
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
    if pd.isna(txt): return "N/I"
    return str(txt).strip()

def renderizar_card(row):
    nome = ajustar_texto(row.get('NOME', 'Centro Espírita'))
    end = ajustar_texto(row.get('ENDERECO', 'Não informado'))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', 'Não informado'))
    palestras = ajustar_texto(row.get('PALESTRA PUBLICA', 'Consulte a casa'))
    resp = ajustar_texto(row.get('RESPONSAVEL', 'N/I'))
    
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    link_wa = f"https://wa.me{whats_num}" if len(whats_num) >= 10 else "#"
    
    query_maps = urllib.parse.quote(f"{nome}, {end}, {cid}")
    link_maps = f"https://www.google.com{query_maps}"

    st.markdown(f"""
    <div class="card-centro">
        <div class="header-card">
            <span class="tag-cidade">🏙️ {cid}</span>
            <span class="nome-centro">{nome} 🕊️</span>
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

# --- LOGIN / NAVEGAÇÃO ---
if "logado" not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🕊️ Guia Espírita")
    with st.form("login_guia"):
        u = st.text_input("E-mail")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR SISTEMA"):
            st.session_state.logado = True
            st.rerun()
else:
    with st.sidebar:
        st.markdown("### ☰ MENU")
        opcao = st.radio("Escolha a opção:", ["🏠 Início", "🔎 Pesquisar Geral", "📍 Por Cidade", "⚙️ Painel Admin", "🚪 Sair"])
        if opcao == "🚪 Sair":
            st.session_state.logado = False
            st.rerun()

    try:
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        st.stop()

    if opcao == "🏠 Início":
        st.title("🕊️ Guia Espírita")
        st.info("Abra o menu lateral (seta no topo esquerdo) para começar a busca.")

    elif opcao == "🔎 Pesquisar Geral":
        termo = st.text_input("Digite nome, cidade ou palavra-chave:")
        if termo:
            mask = df.astype(str).apply(lambda x: x.str.contains(termo, case=False)).any(axis=1)
            for _, row in df[mask].iterrows():
                renderizar_card(row)

    elif opcao == "📍 Por Cidade":
        col_cidade = 'CIDADE DO CENTRO ESPIRITA'
        cidades = sorted(df[col_cidade].dropna().unique())
        escolha = st.selectbox("Selecione a cidade desejada:", ["-- Selecione --"] + cidades)
        if escolha != "-- Selecione --":
            for _, row in df[df[col_cidade] == escolha].iterrows():
                renderizar_card(row)
