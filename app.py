import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- ESTILO CSS PROFISSIONAL (CORES DE PAZ) ---
st.markdown("""
<style>
    /* Fundo e Fonte */
    .stApp {background-color: #F8FAFC;}
    
    /* Menu Lateral (Hambúrguer no Mobile) */
    [data-testid="stSidebar"] {
        background-color: #1E3A8A !important;
        color: white !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Títulos Premium */
    .titulo-premium {
        color: #1E3A8A;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 20px;
        text-align: center;
    }

    /* Cards dos Centros */
    .card-centro {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #3B82F6;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .card-centro:hover { transform: translateY(-3px); }
    
    .nome-grande { color: #1E3A8A; font-size: 22px; font-weight: 800; margin-bottom: 5px; }
    .nome-fantasia { color: #3B82F6; font-size: 15px; font-weight: 600; font-style: italic; margin-bottom: 10px; }
    .info-texto { color: #475569; font-size: 14px; display: flex; align-items: center; gap: 8px; margin-top: 5px;}
    
    /* Botões */
    div.stButton > button {
        background: #1E3A8A !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE UTILIDADE ---
def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    return texto

@st.cache_data
def carregar_dados():
    try:
        # Tenta ler o arquivo Excel
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        # Padronização de colunas
        mapeamento = {
            'NOME FANTASIA': 'Fantasia',
            'NOME': 'Nome Real',
            'CIDADE DO CENTRO ESPIRITA': 'Cidade',
            'ENDERECO': 'Endereco',
            'PALESTRA PUBLICA': 'Palestras',
            'CELULAR': 'Celular'
        }
        df = df.rename(columns=mapeamento)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar guia.xlsx: {e}")
        return pd.DataFrame()

# --- ESTADO DA SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_nome" not in st.session_state:
    st.session_state.usuario_nome = ""

# --- FLUXO DE ACESSO (LOGIN / CADASTRO) ---
if not st.session_state.logado:
    st.markdown("<h1 class='titulo-premium'>🕊️ Guia Espírita</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Entrar", "📝 Cadastrar"])
        
        with tab1:
            with st.form("login"):
                email_l = st.text_input("E-mail")
                senha_l = st.text_input("Senha", type="password")
                if st.form_submit_button("ACESSAR", use_container_width=True):
                    # Futura integração com Supabase aqui
                    if email_l and senha_l:
                        st.session_state.logado = True
                        st.session_state.usuario_nome = email_l.split('@')[0]
                        st.rerun()
                    else:
                        st.error("Preencha todos os campos")
        
        with tab2:
            with st.form("cadastro"):
                nome_c = st.text_input("Nome Completo")
                email_c = st.text_input("E-mail")
                senha_c = st.text_input("Crie uma Senha", type="password")
                if st.form_submit_button("CADASTRAR", use_container_width=True):
                    st.success("Cadastro realizado! Agora faça login.")

# --- ÁREA DO APP (APÓS LOGIN) ---
else:
    # MENU LATERAL (HAMBÚRGUER)
    with st.sidebar:
        st.markdown(f"### Bem-vindo,\n## {st.session_state.usuario_nome} 🕊️")
        st.divider()
        menu = st.radio("Navegação", ["🔍 Buscar Centros", "📍 Por Cidades", "⚙️ Perfil", "🚪 Sair"])
        
        if menu == "🚪 Sair":
            st.session_state.logado = False
            st.rerun()

    df = carregar_dados()

    # PÁGINA: BUSCAR POR CIDADES (MODERNA)
    if menu == "📍 Por Cidades":
        st.markdown("<h1 class='titulo-premium'>Centros por Cidade</h1>", unsafe_allow_html=True)
        
        if not df.empty:
            cidades = sorted(df['Cidade'].dropna().unique())
            cidade_selecionada = st.selectbox(
                "Selecione a cidade desejada no menu abaixo:",
                options=["Ver Todas"] + cidades,
                index=0
            )

            # Filtragem
            if cidade_selecionada == "Ver Todas":
                df_filtrado = df
            else:
                df_filtrado = df[df['Cidade'] == cidade_selecionada]

            st.write(f"Exibindo **{len(df_filtrado)}** centros encontrados.")

            # Exibição dos Cards
            for idx, row in df_filtrado.iterrows():
                st.markdown(f"""
                <div class="card-centro">
                    <div class="nome-grande">{row['Nome Real']}</div>
                    <div class="nome-fantasia">{row.get('Fantasia', 'Centro Espírita')}</div>
                    <div class="info-texto">📍 <b>Endereço:</b> {row['Endereco']}</div>
                    <div class="info-texto">🏙️ <b>Cidade:</b> {row['Cidade']}</div>
                    <div class="info-texto">🗣️ <b>Palestras:</b> {row.get('Palestras', 'Não informado')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    query = urllib.parse.quote(f"{row['Endereco']}, {row['Cidade']}")
                    st.link_button("🗺️ Ver no Google Maps", f"https://www.google.com/maps/search/?api=1&query={query}", use_container_width=True)
                with col_btn2:
                    celular = str(row.get('Celular', ''))
                    num = ''.join(filter(str.isdigit, celular))
                    if len(num) >= 10:
                        st.link_button("💬 WhatsApp", f"https://wa.me/55{num}", use_container_width=True)
        else:
            st.warning("Nenhum dado encontrado no Excel.")

    # PÁGINA: BUSCA GERAL
    elif menu == "🔍 Buscar Centros":
        st.markdown("<h1 class='titulo-premium'>Busca Geral</h1>", unsafe_allow_html=True)
        termo = st.text_input("Digite o nome, rua ou qualquer detalhe:")
        if termo:
            termo_l = limpar_busca(termo)
            # Lógica de busca rápida
            mask = df.apply(lambda r: termo_l in limpar_busca(str(r.values)), axis=1)
            resultados = df[mask]
            st.write(f"Resultados: {len(resultados)}")
            # (Repetir loop de cards aqui se desejar exibir)

# BOTÃO VOLTAR AO TOPO (Injetado via HTML)
st.markdown("""
    <button onclick="window.scrollTo({top: 0, behavior: 'smooth'})" 
    style="position: fixed; bottom: 20px; right: 20px; background: #1E3A8A; color: white; 
    border: none; border-radius: 50%; width: 50px; height: 50px; cursor: pointer; z-index: 99;">↑</button>
""", unsafe_allow_html=True)
