import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- SEU ESTILO ORIGINAL (RESTAURADO E COMPLETO) ---
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);}
.titulo-premium {background: linear-gradient(90deg, #0047AB, #1976D2);-webkit-background-clip: text;-webkit-text-fill-color: transparent;text-shadow: 0 4px 12px rgba(0,71,171,0.3);font-size: 2.5rem !important;font-weight: 800 !important; text-align: center; padding: 20px;}
.card-centro {background: rgba(255,255,255,0.95);backdrop-filter: blur(10px);padding: 20px;border-radius: 20px;border: 1px solid rgba(0,71,171,0.1);box-shadow: 0 8px 32px rgba(0,71,171,0.15);margin-bottom: 16px; position: relative;}
.nome-grande {color: #1E3A8A !important;font-size: 22px !important;font-weight: 800 !important;}
.nome-fantasia {color: #3B82F6 !important;font-size: 15px !important;font-weight: 600 !important;font-style: italic;}
.info-texto {color: #374151 !important;font-size: 13px !important;display: flex;align-items: center;gap: 6px;}
.palestras-verde {color: #10B981 !important; font-weight: 700 !important; font-size: 14px !important; background: rgba(16,185,129,0.15) !important; padding: 8px 14px !important; border-radius: 12px !important; border-left: 4px solid #10B981 !important; box-shadow: 0 2px 8px rgba(16,185,129,0.2) !important;}

/* Ajuste do Menu Lateral */
[data-testid="stSidebar"] {background-color: #1E3A8A !important;}
[data-testid="stSidebar"] * {color: white !important;}

div.stButton > button {background: linear-gradient(135deg, #0047AB, #1E40AF) !important;color: white !important;border-radius: 12px !important;height: 50px !important;font-size: 16px !important;font-weight: 700 !important; transition: 0.3s;}
div.stButton > button:hover {transform: scale(1.02); box-shadow: 0 5px 15px rgba(0,71,171,0.4);}
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE LIMPEZA ORIGINAL ---
def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    return texto

# --- INICIALIZAÇÃO DO ESTADO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# --- LOGICA DE TELA ---

# 1. SE NÃO ESTIVER LOGADO -> MOSTRA ÁREA DE CADASTRO/LOGIN
if not st.session_state.logado:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita - CADASTRO</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.write("### 📝 Bem-vindo! Faça seu acesso:")
            nome = st.text_input("👤 Nome Completo")
            email = st.text_input("📧 E-mail")
            st.write("")
            if st.button("📝 CADASTRAR E ENTRAR", use_container_width=True):
                if not nome.strip() or not email.strip():
                    st.error("❌ Preencha **NOME e EMAIL**!")
                elif "@" not in email:
                    st.error("❌ E-mail inválido!")
                else:
                    st.session_state.logado = True
                    st.session_state.usuario = nome.strip()
                    st.success(f"✅ Bem-vindo, {nome}!")
                    st.rerun()

# 2. SE ESTIVER LOGADO -> MOSTRA O APP COM MENU HAMBÚRGUER
else:
    # --- MENU LATERAL (HAMBÚRGUER) ---
    with st.sidebar:
        st.markdown(f"## Olá,\n### {st.session_state.usuario}! 🕊️")
        st.divider()
        menu = st.radio("Navegação", ["🔍 Buscar Centros", "📍 Por Cidades", "🚪 Sair"])
        if menu == "🚪 Sair":
            st.session_state.logado = False
            st.session_state.usuario = ""
            st.rerun()

    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)

    try:
        # Carregamento do Excel com suas colunas exatas
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        if 'Unnamed: 0' in df.columns:
            df = df.drop('Unnamed: 0', axis=1)
        
        df.columns = df.columns.str.strip()
        df = df.rename(columns={
            'NOME FANTASIA': 'Nome Fantasia',
            'NOME': 'Nome Real / Razão Social',
            'CIDADE DO CENTRO ESPIRITA': 'Cidade',
            'ENDERECO': 'Endereço',
            'PALESTRA PUBLICA': 'Palestra Pública',
            'RESPONSAVEL': 'Responsável',
            'CELULAR': 'Celular'
        })

        if menu == "📍 Por Cidades":
            st.markdown(f"<h2 style='color:#1E3A8A;'>📍 Filtro por Cidade</h2>", unsafe_allow_html=True)
            lista_cidades = sorted(df['Cidade'].dropna().unique())
            cidade_f = st.selectbox("Selecione a cidade no menu abaixo:", ["Ver Todas"] + lista_cidades)
            
            resultados = df if cidade_f == "Ver Todas" else df[df['Cidade'] == cidade_f]
        
        else:
            # Busca Geral
            busca = st.text_input("🔍 Digite nome, cidade ou qualquer palavra...")
            termo_limpo = limpar_busca(busca)
            
            if termo_limpo:
                # Lógica de busca em todas as colunas
                mask = df.apply(lambda r: termo_limpo in limpar_busca(' '.join(map(str, r.values))), axis=1)
                resultados = df[mask]
            else:
                resultados = pd.DataFrame() # Começa vazio na busca geral até digitar

        # EXIBIÇÃO DOS CARDS
        if not resultados.empty:
            st.info(f"✨ Encontrados {len(resultados)} centros.")
            for idx, row in resultados.iterrows():
                v_fantasia = str(row.get('Nome Fantasia', 'N/I'))
                v_nome_real = str(row.get('Nome Real / Razão Social', 'Centro Espírita')) + " 🕊️"
                v_cidade = str(row.get('Cidade', 'N/I'))
                v_endereco = str(row.get('Endereço', 'N/I'))
                v_resp = str(row.get('Responsável', 'N/I'))
                v_celular = str(row.get('Celular', ''))
                v_palestras = str(row.get('Palestra Pública', ''))

                st.markdown(f"""
                <div class="card-centro">
                    <div class="nome-grande">{v_nome_real}</div>
                    <div class="nome-fantasia">{v_fantasia}</div>
                    <div class="palestras-verde">🗣️ PALESTRAS {v_palestras}</div>
                    <div class="info-texto">👤 <b>Responsável:</b> {v_resp}</div>
                    <div class="info-texto">📍 <b>Endereço:</b> {row.get('Endereço', 'N/I')}</div>
                    <div class="info-texto">🏙️ <b>Cidade:</b> {v_cidade}</div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    query = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                    st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}", use_container_width=True)
                with col2:
                    numero = ''.join(filter(str.isdigit, v_celular))
                    if len(numero) >= 10:
                        st.link_button("💬 WhatsApp", f"https://wa.me/55{numero}", use_container_width=True)
                st.divider()
        elif menu == "📍 Por Cidades" and resultados.empty:
            st.warning("Nenhum centro encontrado para esta cidade.")

    except Exception as e:
        st.error(f"Erro ao carregar dados do Excel: {e}")

# Botão Voltar ao Topo
st.markdown("""
<button onclick="window.scrollTo({top: 0, behavior: 'smooth'})" 
        style="position: fixed; bottom: 30px; right: 30px; background: #10B981; color: white; 
        border: none; border-radius: 50px; width: 60px; height: 60px; font-size: 24px; cursor: pointer; 
        box-shadow: 0 6px 20px rgba(16,185,129,0.4); z-index: 9999;">⬆️</button>
""", unsafe_allow_html=True)
