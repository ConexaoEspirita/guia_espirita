import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS PROFISSIONAL: MENU, BUSCA E CARDS ---
st.markdown("""
<style>
    /* Menu Lateral */
    [data-testid="stSidebar"] { padding-top: 35px; }
    div[data-testid="stMarkdownContainer"] p { font-size: 20px !important; font-weight: 700 !important; color: #1E3A8A; }
    
    /* Barra de Pesquisa Profissional */
    .stTextInput input {
        border-radius: 12px !important;
        border: 2px solid #D4E8F7 !important;
        padding: 10px 15px !important;
        font-size: 16px !important;
        box-shadow: 0 2px 8px rgba(0,71,171,0.05) !important;
    }
    .stTextInput input:focus {
        border-color: #0047AB !important;
        box-shadow: 0 2px 12px rgba(0,71,171,0.15) !important;
    }

    .stApp { background: #f4f7f9; }
    
    /* Card com Sombra e Número */
    .card-centro { 
        background: white !important; padding: 25px; border-radius: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.12); 
        margin-bottom: 25px; border-left: 12px solid #0047AB;
        position: relative;
    }
    .numero-badge {
        position: absolute; top: 15px; right: 20px;
        background: #f0f4f8; color: #7f8c8d; padding: 2px 10px;
        border-radius: 20px; font-size: 12px; font-weight: 800;
    }
    
    .nome-centro { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800; display: block; }
    .nome-fantasia { color: #3B82F6 !important; font-size: 16px !important; font-style: italic; font-weight: 500; margin-top: 2px; display: block; }
    
    .palestras-verde { 
        color: #065F46 !important; font-weight: 700; background: #D1FAE5; 
        padding: 10px; border-radius: 10px; margin: 12px 0; border: 1px solid #10B981;
    }
    .info-linha { margin: 8px 0; font-size: 15px; color: #333 !important; }
    .label-bold { font-weight: 800; color: #0047AB; text-transform: uppercase; font-size: 13px; }
    
    .btn-row { display: flex; gap: 12px; margin-top: 20px; }
    .btn-link { 
        text-decoration: none !important; color: white !important; 
        padding: 14px; border-radius: 12px; font-weight: 800; 
        text-align: center; flex: 1; display: inline-block; transition: 0.3s;
    }
    .bg-wa { background-color: #25D366; }
    .bg-maps { background-color: #4285F4; }
    .btn-link:hover { opacity: 0.9; transform: scale(1.02); }
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
    
    # WhatsApp (Lógica Consertada)
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    if len(whats_num) >= 10:
        whats_num = "+55" + whats_num
        link_wa = f"https://wa.me{whats_num}"
    else:
        link_wa = "#"
    
    # Maps (Lógica Consertada)
    query_maps = urllib.parse.quote(f"{nome}, {end}, {cid}")
    link_maps = f"https://www.google.com{query_maps}"

    st.markdown(f"""
    <div class="card-centro">
        <div class="numero-badge">CENTRO #{index}</div>
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

# --- LOGIN E SISTEMA ---
if "logado" not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🕊️ Guia Espírita")
    with st.form("login"):
        u = st.text_input("E-mail")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR SISTEMA"):
            st.session_state.logado = True
            st.rerun()
else:
    with st.sidebar:
        st.markdown("### ☰ MENU")
        opcao = st.radio("Escolha:", ["🏠 Início", "🔎 Pesquisar Geral", "📍 Por Cidade", "🚪 Sair"])
        if opcao == "🚪 Sair":
            st.session_state.logado = False
            st.rerun()

    # Carregamento de dados com tratamento
    try:
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error("Erro ao carregar o arquivo Excel. Verifique se o nome está correto."); st.stop()

    if opcao == "🏠 Início":
        st.title("🕊️ Guia Espírita")
        st.info("Utilize o menu lateral para iniciar sua jornada de busca.")

    elif opcao == "🔎 Pesquisar Geral":
        st.subheader("🔎 Busca Inteligente")
        termo = st.text_input("", placeholder="Digite nome, cidade, endereço ou termo...", key="search_input")
        
        if termo:
            termo_lower = termo.lower().strip()
            # Busca em todas as colunas convertendo para string
            mask = df.fillna("").astype(str).apply(lambda x: x.str.contains(termo_lower, case=False)).any(axis=1)
            res = df[mask]
            
            if not res.empty:
                st.write(f"Encontrados **{len(res)}** resultados:")
                for i, (_, row) in enumerate(res.iterrows(), 1):
                    renderizar_card(row, i)
            else:
                st.warning("Nenhum resultado encontrado para este termo.")

    elif opcao == "📍 Por Cidade":
        cidades = sorted(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique())
        sel = st.selectbox("Selecione a cidade desejada:", ["-- Clique para escolher --"] + cidades)
        if sel != "-- Clique para escolher --":
            dados = df[df['CIDADE DO CENTRO ESPIRITA'] == sel]
            for i, (_, row) in enumerate(dados.iterrows(), 1):
                renderizar_card(row, i)
