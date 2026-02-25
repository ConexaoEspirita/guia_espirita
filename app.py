import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CONEXÃO SUPABASE (VERSÃO DETETIVE) ---
@st.cache_resource
def conectar_supabase():
    # Tenta buscar de várias formas comuns (minúsculas, maiúsculas, prefixos)
    url = st.secrets.get("supabase_url") or st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("supabase_key") or st.secrets.get("SUPABASE_KEY")

    if not url or not key:
        st.error("❌ ERRO DE CONFIGURAÇÃO NOS SECRETS")
        st.write("O código procurou por 'supabase_url' e 'supabase_key' mas não achou.")
        st.write("Nomes encontrados nos seus Secrets atualmente:", list(st.secrets.keys()))
        st.info("💡 Vá em Settings > Secrets e certifique-se de usar nomes minúsculos.")
        st.stop()
    
    try:
        # Limpa espaços em branco acidentais
        url_clean = url.strip()
        key_clean = key.strip()
        return create_client(url_clean, key_clean)
    except Exception as e:
        st.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
        st.stop()

supabase = conectar_supabase()

# --- ESTILO CSS ---
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);}
    .login-box {background: white; padding: 35px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border: 1px solid #1E3A8A;}
    [data-testid="stSidebar"] {background-color: #1E3A8A !important;}
    [data-testid="stSidebar"] * {color: white !important;}
    .card-centro {background: white; padding: 20px; border-radius: 15px; border-left: 8px solid #1E3A8A; margin-bottom: 15px;}
    .nome-grande {color: #1E3A8A !important; font-size: 22px !important; font-weight: 800 !important;}
    div.stButton > button {background: #1E3A8A !important; color: white !important; font-weight: 700 !important; width: 100%; border-radius: 10px !important;}
</style>
""", unsafe_allow_html=True)

# --- SISTEMA DE ACESSO ---
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#1E3A8A;'>🕊️ Guia Espírita</h2>", unsafe_allow_html=True)
        
        tab_l, tab_c = st.tabs(["🔑 Login", "📝 Cadastro"])
        
        with tab_l:
            e = st.text_input("E-mail")
            s = st.text_input("Senha", type="password")
            if st.button("ACESSAR"):
                # Validação real
                res = supabase.table("usuarios").select("*").eq("email", e).eq("senha", s).execute()
                if res.data:
                    st.session_state.logado = True
                    st.session_state.usuario_nome = res.data[0]['nome']
                    st.rerun()
                else:
                    st.error("❌ Dados incorretos. Verifique e-mail e senha.")
        
        with tab_c:
            n_c = st.text_input("Nome Completo")
            e_c = st.text_input("E-mail de Cadastro")
            s_c = st.text_input("Senha de Cadastro", type="password")
            if st.button("CADASTRAR"):
                if n_c and e_c and s_c:
                    supabase.table("usuarios").insert({"nome": n_c, "email": e_c, "senha": s_c}).execute()
                    st.success("✅ Sucesso! Agora faça login na aba ao lado.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- APP PRINCIPAL ---
    with st.sidebar:
        st.markdown(f"### Olá, {st.session_state.usuario_nome}! 👋")
        st.divider()
        menu = st.radio("Navegação", ["🔍 Buscar", "🏙️ Cidades", "🚪 Sair"])
        if menu == "🚪 Sair":
            st.session_state.logado = False
            st.rerun()

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
            c_sel = st.selectbox("Cidade:", ["Todas"] + cidades)
            dados = df if c_sel == "Todas" else df[df['Cidade'] == c_sel]
        else:
            busca = st.text_input("Pesquisar...")
            dados = df[df.apply(lambda r: busca.lower() in str(r.values).lower(), axis=1)] if busca else pd.DataFrame()

        for _, row in dados.iterrows():
            st.markdown(f"""
                <div class="card-centro">
                    <div class="nome-grande">{row['Nome']}</div>
                    <div style="color:#3B82F6; font-style:italic;">{row['Fantasia']}</div>
                    <p>📍 {row['Endereco']} | 🏙️ {row['Cidade']}</p>
                    <p style="color:#10B981; font-weight:bold;">🗣️ {row['Palestra']}</p>
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
        st.error(f"Erro no Excel: {e}")
