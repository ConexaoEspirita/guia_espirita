import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CONEXÃO SUPABASE (CORRIGIDA) ---
# Aqui ele tenta ler do segredo do Streamlit. Certifique-se que no site do Streamlit 
# as chaves estão como: supabase_url e supabase_key
try:
    URL_SUPABASE = st.secrets["supabase_url"]
    KEY_SUPABASE = st.secrets["supabase_key"]
    # Verifica se a URL é válida antes de tentar conectar
    if not URL_SUPABASE or "https" not in URL_SUPABASE:
        st.error("❌ A URL do Supabase no 'Secrets' está inválida ou vazia.")
        st.stop()
    supabase: Client = create_client(URL_SUPABASE, KEY_SUPABASE)
except Exception as e:
    st.error(f"❌ Erro de Conexão: Verifique se as chaves 'supabase_url' e 'supabase_key' estão configuradas no Streamlit Cloud.")
    st.stop()

# --- CSS PROFISSIONAL (AZUL NAVY + PAZ) ---
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);}
    .login-box {
        background: white; 
        padding: 40px; 
        border-radius: 20px; 
        box-shadow: 0 15px 35px rgba(0,71,171,0.2); 
        border: 1px solid #1E3A8A;
    }
    [data-testid="stSidebar"] {background-color: #1E3A8A !important;}
    [data-testid="stSidebar"] * {color: white !important;}
    .card-centro {
        background: rgba(255,255,255,0.95);
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #1E3A8A;
        box-shadow: 0 8px 32px rgba(0,71,171,0.1);
        margin-bottom: 16px;
    }
    .nome-grande {color: #1E3A8A !important; font-size: 22px !important; font-weight: 800 !important;}
    .palestras-verde {color: #10B981 !important; font-weight: 700; background: rgba(16,185,129,0.1); padding: 5px 10px; border-radius: 10px; display: inline-block; margin-top: 10px;}
    div.stButton > button {
        background: linear-gradient(135deg, #0047AB, #1E40AF) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES ---
def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    return re.sub(r'[^a-z0-9\s]', '', texto)

def verificar_login(email, senha):
    try:
        res = supabase.table("usuarios").select("*").eq("email", email).eq("senha", senha).execute()
        return res.data
    except Exception as e:
        return []

# --- LÓGICA DE SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False

# --- 1. TELA DE ACESSO ---
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#1E3A8A;'>🕊️ Portal Espírita</h2>", unsafe_allow_html=True)
        
        tab_log, tab_cad = st.tabs(["🔑 Entrar", "📝 Novo Cadastro"])
        
        with tab_log:
            e_log = st.text_input("E-mail")
            s_log = st.text_input("Senha", type="password")
            if st.button("ACESSAR GUIA"):
                user_db = verificar_login(e_log, s_log)
                if user_db:
                    st.session_state.logado = True
                    st.session_state.usuario_nome = user_db[0]['nome']
                    st.rerun()
                else:
                    st.error("❌ E-mail ou senha incorretos.")
        
        with tab_cad:
            n_nome = st.text_input("Nome Completo")
            n_email = st.text_input("Seu E-mail")
            n_senha = st.text_input("Crie uma Senha", type="password")
            if st.button("CADASTRAR CONTA"):
                if n_nome and n_email and n_senha:
                    supabase.table("usuarios").insert({"nome": n_nome, "email": n_email, "senha": n_senha}).execute()
                    st.success("✅ Cadastro feito! Use a aba 'Entrar'.")
                else:
                    st.warning("Preencha todos os campos.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 2. APP PRINCIPAL ---
else:
    with st.sidebar:
        st.markdown(f"### Olá, {st.session_state.usuario_nome}! 🕊️")
        st.divider()
        menu = st.radio("Menu Principal:", ["🔍 Busca Geral", "🏙️ Por Cidades", "🚪 Sair"])
        if menu == "🚪 Sair":
            st.session_state.logado = False
            st.rerun()

    st.markdown("<h1 style='color:#1E3A8A; text-align:center;'>🕊️ Guia de Centros Espíritas</h1>", unsafe_allow_html=True)

    try:
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        df = df.rename(columns={
            'NOME FANTASIA': 'Fantasia', 'NOME': 'Nome',
            'CIDADE DO CENTRO ESPIRITA': 'Cidade', 'ENDERECO': 'Endereco',
            'PALESTRA PUBLICA': 'Palestra', 'CELULAR': 'Celular'
        })

        if menu == "🏙️ Por Cidades":
            lista_cidades = sorted(df['Cidade'].dropna().unique())
            cid_sel = st.selectbox("Selecione a cidade:", ["Todas as Cidades"] + lista_cidades)
            resultados = df if cid_sel == "Todas as Cidades" else df[df['Cidade'] == cid_sel]
        else:
            txt_busca = st.text_input("🔍 Digite nome, cidade ou rua...")
            termo = limpar_busca(txt_busca)
            if termo:
                mask = df.apply(lambda r: termo in limpar_busca(' '.join(map(str, r.values))), axis=1)
                resultados = df[mask]
            else:
                resultados = pd.DataFrame()

        if not resultados.empty:
            for _, row in resultados.iterrows():
                st.markdown(f"""
                <div class="card-centro">
                    <div class="nome-grande">{row['Nome']}</div>
                    <div class="palestras-verde">🗣️ PALESTRAS: {row['Palestra']}</div>
                    <div style="font-size:14px; margin-top:10px; color:#4B5563;">
                        📍 <b>Endereço:</b> {row['Endereco']}<br>
                        🏙️ <b>Cidade:</b> {row['Cidade']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    q = urllib.parse.quote(f"{row['Endereco']}, {row['Cidade']}")
                    st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={q}", use_container_width=True)
                with c2:
                    num = ''.join(filter(str.isdigit, str(row['Celular'])))
                    if len(num) >= 10:
                        st.link_button("💬 WHATSAPP", f"https://wa.me/55{num}", use_container_width=True)
                st.divider()

    except Exception as e:
        st.error(f"Erro ao carregar o Excel: {e}")

st.markdown('<button onclick="window.scrollTo({top: 0, behavior: \'smooth\'})" style="position: fixed; bottom: 30px; right: 30px; background: #1E3A8A; color: white; border: none; border-radius: 50%; width: 50px; height: 50px; cursor: pointer; z-index: 9999;">↑</button>', unsafe_allow_html=True)
