import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS Corrigido para evitar cortes e melhorar botões ---
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; }
    .stApp { background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%); }
    .titulo-premium { 
        background: linear-gradient(90deg, #0047AB, #1976D2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 2.2rem !important; font-weight: 800; text-align: center; margin-bottom: 20px;
    }
    .card-centro { 
        background: white; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px;
        border-left: 6px solid #0047AB;
    }
    .nome-grande { color: #1E3A8A; font-size: 20px; font-weight: 800; line-height: 1.2; }
    .nome-fantasia { color: #3B82F6; font-size: 14px; font-style: italic; margin-bottom: 8px; }
    .info-texto { color: #4B5563; font-size: 13px; margin: 4px 0; }
    .btn-container { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
    .btn-acao { 
        padding: 8px 16px; border-radius: 8px; text-decoration: none; 
        font-weight: bold; font-size: 13px; display: flex; align-items: center; gap: 5px;
    }
    .btn-whatsapp { background-color: #25D366; color: white !important; }
    .btn-maps { background-color: #4285F4; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- Funções Auxiliares ---
def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode("utf-8")
    return re.sub(r'[^a-zA-Z0-9\s]', '', texto)

# --- Supabase ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

if "logado" not in st.session_state: st.session_state.logado = False

# --- Lógica de Login (Simplificada para o exemplo) ---
if not st.session_state.logado:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    with st.container():
        aba = st.tabs(["Login", "Cadastro"])
        with aba[0]:
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.button("ACESSAR"):
                # Lógica de login aqui (conforme seu original)
                st.session_state.logado = True
                st.rerun()
else:
    # --- TELA PRINCIPAL ---
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)

    # --- Menu Flutuante (Sidebar como Menu) ---
    with st.sidebar:
        st.title("☰ Navegação")
        opcao = st.radio("Ir para:", ["Cidades", "Painel Admin", "Sair"])
        if opcao == "Sair":
            st.session_state.logado = False
            st.rerun()

    try:
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        col_cidade = 'CIDADE DO CENTRO ESPIRITA'

        if opcao == "Cidades":
            cidade_sel = st.selectbox("📍 Escolha uma Cidade", ["Todas"] + sorted(df[col_cidade].dropna().unique().tolist()))
            
            dados_filtrados = df if cidade_sel == "Todas" else df[df[col_cidade] == cidade_sel]

            for _, row in dados_filtrados.iterrows():
                nome = row.get('NOME', 'Centro Espírita')
                fantasia = row.get('NOME FANTASIA', '')
                endereco = row.get('ENDERECO', '')
                cidade = row.get(col_cidade, '')
                celular = str(row.get('CELULAR', '')).replace('.0', '').replace(' ', '').replace('-', '')
                
                # Links
                link_maps = f"https://www.google.com{urllib.parse.quote(f'{nome} {endereco} {cidade}')}"
                link_wa = f"https://wa.me{celular}" if celular != 'nan' else None

                st.markdown(f"""
                <div class="card-centro">
                    <div class="nome-grande">{nome}</div>
                    <div class="nome-fantasia">{fantasia}</div>
                    <div class="info-texto">📍 {endereco} - {cidade}</div>
                    <div class="info-texto">🗣️ Palestras: {row.get('PALESTRA PUBLICA', 'Consulte')}</div>
                    <div class="btn-container">
                        <a href="{link_maps}" target="_blank" class="btn-acao btn-maps">📍 Ver no Mapa</a>
                        {f'<a href="{link_wa}" target="_blank" class="btn-acao btn-whatsapp">💬 WhatsApp</a>' if link_wa else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        elif opcao == "Painel Admin":
            st.subheader("⚙️ Área Administrativa")
            st.info("Em breve: Gestão de usuários e cadastros.")

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
