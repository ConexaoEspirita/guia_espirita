import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS PARA LOGIN E APP PROFISSIONAL ---
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);}
    
    /* Centralização da Caixa de Login */
    .login-container {
        background: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,71,171,0.2);
        text-align: center;
        border: 1px solid #D1E9FF;
    }
    
    /* Menu Lateral Azul Navy */
    [data-testid="stSidebar"] {background-color: #1E3A8A !important;}
    [data-testid="stSidebar"] * {color: white !important;}
    
    /* Cards do Guia */
    .card-centro {
        background: rgba(255,255,255,0.95);
        padding: 20px;
        border-radius: 15px;
        border-left: 6px solid #1E3A8A;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    
    .nome-grande {color: #1E3A8A !important; font-size: 22px !important; font-weight: 800 !important;}
    .palestras-verde {color: #10B981 !important; font-weight: 700; background: #E6F9F1; padding: 5px 10px; border-radius: 8px;}
    
    /* Botões */
    div.stButton > button {
        background: linear-gradient(135deg, #0047AB, #1E40AF) !important;
        color: white !important;
        border-radius: 10px !important;
        height: 45px !important;
        font-weight: 700 !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES TÉCNICAS ---
def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    return re.sub(r'[^a-z0-9\s]', '', texto)

# --- CONTROLE DE SESSÃO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# ==========================================
# 1. ÁREA DE LOGIN E CADASTRO (TELA INICIAL)
# ==========================================
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("<h1 style='color: #1E3A8A;'>🕊️ Guia Espírita</h1>", unsafe_allow_html=True)
        
        aba_login, aba_cadastro = st.tabs(["🔑 Login", "📝 Cadastro"])
        
        with aba_login:
            email_log = st.text_input("E-mail", key="l_email")
            senha_log = st.text_input("Senha", type="password", key="l_senha")
            if st.button("ENTRAR AGORA"):
                if email_log and senha_log:
                    st.session_state.autenticado = True
                    st.session_state.usuario = email_log.split('@')[0]
                    st.rerun()
                else:
                    st.error("Preencha os dados de acesso.")
        
        with aba_cadastro:
            nome_cad = st.text_input("Nome Completo", key="c_nome")
            email_cad = st.text_input("E-mail", key="c_email")
            senha_cad = st.text_input("Crie uma Senha", type="password", key="c_senha")
            if st.button("CRIAR CONTA"):
                if nome_cad and email_cad and senha_cad:
                    st.success("Cadastro realizado! Use a aba Login.")
                else:
                    st.error("Preencha todos os campos para cadastrar.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 2. APP PRINCIPAL (SÓ APARECE APÓS LOGIN)
# ==========================================
else:
    # MENU HAMBÚRGUER (SIDEBAR)
    with st.sidebar:
        st.markdown(f"### Bem-vindo, \n## {st.session_state.usuario} 🕊️")
        st.divider()
        menu = st.radio("Navegação:", ["🔍 Buscar Centros", "🏙️ Por Cidades", "🚪 Sair"])
        
        if menu == "🚪 Sair":
            st.session_state.autenticado = False
            st.rerun()

    st.markdown("<h1 style='color: #1E3A8A; text-align:center;'>🕊️ Guia de Centros Espíritas</h1>", unsafe_allow_html=True)

    try:
        # Carregamento dos dados
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        df = df.rename(columns={
            'NOME FANTASIA': 'Fantasia', 'NOME': 'Nome',
            'CIDADE DO CENTRO ESPIRITA': 'Cidade', 'ENDERECO': 'Endereco',
            'PALESTRA PUBLICA': 'Palestra', 'CELULAR': 'Celular'
        })

        # --- LÓGICA DE FILTRAGEM ---
        if menu == "🏙️ Por Cidades":
            cidades = sorted(df['Cidade'].dropna().unique())
            escolha_cidade = st.selectbox("Selecione a cidade:", ["Todas"] + cidades)
            resultados = df if escolha_cidade == "Todas" else df[df['Cidade'] == escolha_cidade]
        else:
            busca = st.text_input("Pesquisar por nome ou palavra-chave...")
            termo = limpar_busca(busca)
            if termo:
                mask = df.apply(lambda r: termo in limpar_busca(' '.join(map(str, r.values))), axis=1)
                resultados = df[mask]
            else:
                resultados = pd.DataFrame()

        # --- EXIBIÇÃO DOS CARDS ---
        if not resultados.empty:
            for _, row in resultados.iterrows():
                st.markdown(f"""
                <div class="card-centro">
                    <div class="nome-grande">{row['Nome']}</div>
                    <div style="color:#3B82F6; font-style:italic; margin-bottom:10px;">{row['Fantasia']}</div>
                    <div class="info-texto">📍 <b>Endereço:</b> {row['Endereco']}</div>
                    <div class="info-texto">🏙️ <b>Cidade:</b> {row['Cidade']}</div>
                    <div class="palestras-verde">🗣️ Palestras: {row['Palestra']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    q = urllib.parse.quote(f"{row['Endereco']}, {row['Cidade']}")
                    st.link_button("🗺️ VER NO MAPA", f"https://www.google.com/maps/search/{q}", use_container_width=True)
                with c2:
                    num = ''.join(filter(str.isdigit, str(row['Celular'])))
                    if len(num) >= 10:
                        st.link_button("💬 WHATSAPP", f"https://wa.me/55{num}", use_container_width=True)
                st.divider()

    except Exception as e:
        st.error(f"Erro ao carregar banco de dados: {e}")

# Botão de voltar ao topo
st.markdown("""
    <button onclick="window.scrollTo({top: 0, behavior: 'smooth'})" 
    style="position: fixed; bottom: 20px; right: 20px; background: #1E3A8A; color: white; 
    border: none; border-radius: 50%; width: 50px; height: 50px; cursor: pointer; z-index: 100;">↑</button>
""", unsafe_allow_html=True)
