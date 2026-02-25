import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CONEXÃO SUPABASE (COM LIMPEZA DE ESPAÇOS) ---
@st.cache_resource
def conectar_supabase():
    try:
        # Puxa os segredos e remove espaços em branco acidentais
        url = st.secrets["supabase_url"].strip()
        key = st.secrets["supabase_key"].strip()
        
        # Validação básica de formato
        if not url.startswith("https"):
            st.error("⚠️ A URL do Supabase precisa começar com https://")
            st.stop()
            
        return create_client(url, key)
    except KeyError:
        st.error("❌ Chaves não encontradas! Verifique se os nomes nos Secrets são 'supabase_url' e 'supabase_key'.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Erro inesperado na conexão: {e}")
        st.stop()

supabase = conectar_supabase()

# --- ESTILO CSS ---
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);}
    .login-box {background: white; padding: 40px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,71,171,0.1); border: 1px solid #1E3A8A;}
    [data-testid="stSidebar"] {background-color: #1E3A8A !important;}
    [data-testid="stSidebar"] * {color: white !important;}
    .card-centro {background: white; padding: 20px; border-radius: 15px; border-left: 8px solid #1E3A8A; margin-bottom: 15px;}
    .nome-grande {color: #1E3A8A !important; font-size: 22px !important; font-weight: 800 !important;}
    .palestras-verde {color: #10B981 !important; font-weight: 700; background: #E6F9F1; padding: 5px 10px; border-radius: 8px;}
    div.stButton > button {background: #1E3A8A !important; color: white !important; border-radius: 10px !important; font-weight: 700 !important;}
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES ---
def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode("utf-8")
    return re.sub(r'[^a-z0-9\s]', '', texto)

# --- LÓGICA DE SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False

# --- TELA DE ACESSO ---
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#1E3A8A;'>🕊️ Área de Acesso</h2>", unsafe_allow_html=True)
        
        tab_login, tab_cadastro = st.tabs(["🔑 Login", "📝 Cadastro"])
        
        with tab_login:
            e_log = st.text_input("E-mail")
            s_log = st.text_input("Senha", type="password")
            if st.button("ENTRAR NO GUIA"):
                try:
                    res = supabase.table("usuarios").select("*").eq("email", e_log).eq("senha", s_log).execute()
                    if res.data:
                        st.session_state.logado = True
                        st.session_state.usuario_nome = res.data[0]['nome']
                        st.rerun()
                    else:
                        st.error("E-mail ou senha incorretos!")
                except Exception as e:
                    st.error(f"Erro ao consultar banco: {e}")
        
        with tab_cadastro:
            n_cad = st.text_input("Nome Completo")
            e_cad = st.text_input("E-mail para cadastro")
            s_cad = st.text_input("Defina uma senha", type="password")
            if st.button("FINALIZAR CADASTRO"):
                if n_cad and e_cad and s_cad:
                    try:
                        supabase.table("usuarios").insert({"nome": n_cad, "email": e_cad, "senha": s_cad}).execute()
                        st.success("Cadastro realizado! Use a aba Login.")
                    except Exception as e:
                        st.error(f"Erro: {e}")
                else:
                    st.warning("Preencha todos os campos.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- ÁREA LOGADA ---
    with st.sidebar:
        st.markdown(f"### Olá, {st.session_state.usuario_nome}! 🕊️")
        st.divider()
        menu = st.radio("Menu", ["🔍 Busca", "🏙️ Cidades", "🚪 Sair"])
        if menu == "🚪 Sair":
            st.session_state.logado = False
            st.rerun()

    st.markdown("<h1 style='color:#1E3A8A; text-align:center;'>Guia de Centros Espíritas</h1>", unsafe_allow_html=True)

    try:
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        df = df.rename(columns={
            'NOME FANTASIA': 'Fantasia', 'NOME': 'Nome',
            'CIDADE DO CENTRO ESPIRITA': 'Cidade', 'ENDERECO': 'Endereco',
            'PALESTRA PUBLICA': 'Palestra', 'CELULAR': 'Celular'
        })

        if menu == "🏙️ Cidades":
            cidades = sorted(df['Cidade'].dropna().unique())
            cid_sel = st.selectbox("Escolha uma cidade:", ["Ver Todas"] + cidades)
            res_df = df if cid_sel == "Ver Todas" else df[df['Cidade'] == cid_sel]
        else:
            busca = st.text_input("O que você procura?")
            termo = limpar_busca(busca)
            if termo:
                mask = df.apply(lambda r: termo in limpar_busca(' '.join(map(str, r.values))), axis=1)
                res_df = df[mask]
            else:
                res_df = pd.DataFrame()

        for _, row in res_df.iterrows():
            st.markdown(f"""
                <div class="card-centro">
                    <div class="nome-grande">{row['Nome']}</div>
                    <div style="color:#3B82F6; font-weight:600;">{row['Fantasia']}</div>
                    <div style="margin-top:10px;">📍 {row['Endereco']} | 🏙️ {row['Cidade']}</div>
                    <div class="palestras-verde" style="margin-top:10px;">🗣️ {row['Palestra']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                q = urllib.parse.quote(f"{row['Endereco']}, {row['Cidade']}")
                st.link_button("🗺️ MAPA", f"https://www.google.com/maps/search/?api=1&query={q}", use_container_width=True)
            with c2:
                num = ''.join(filter(str.isdigit, str(row['Celular'])))
                if len(num) >= 10:
                    st.link_button("💬 WHATSAPP", f"https://wa.me/55{num}", use_container_width=True)
            st.divider()

    except Exception as e:
        st.error(f"Erro ao carregar Excel: {e}")

st.markdown('<button onclick="window.scrollTo({top: 0, behavior: \'smooth\'})" style="position: fixed; bottom: 20px; right: 20px; background: #1E3A8A; color: white; border: none; border-radius: 50%; width: 50px; height: 50px; cursor: pointer; z-index: 999;">↑</button>', unsafe_allow_html=True)
