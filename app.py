import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS Limpo e Responsivo ---
st.markdown("""
<style>
.block-container { padding-top: 0rem !important; }
[data-testid="stDecoration"] { display: none !important; }
.stApp { background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%); }
.titulo-premium { background: linear-gradient(90deg, #0047AB, #1976D2);
-webkit-background-clip: text; -webkit-text-fill-color: transparent;
text-shadow: 0 4px 12px rgba(0,71,171,0.3);
font-size: 2.5rem !important; font-weight: 800 !important; margin: 0; }
.card-centro { background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
padding: 20px; border-radius: 20px; border: 1px solid rgba(0,71,171,0.1);
box-shadow: 0 8px 32px rgba(0,71,171,0.15); margin-bottom: 16px; }
.nome-grande { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800 !important; }
.nome-fantasia { color: #3B82F6 !important; font-size: 15px !important; font-weight: 600 !important; font-style: italic; }
.info-texto { color: #374151 !important; font-size: 13px !important; display: flex; align-items: center; gap: 6px; }
.palestras-verde { color: #10B981 !important; font-weight: 700 !important; font-size: 14px !important; background: rgba(16,185,129,0.15) !important;
padding: 8px 14px !important; border-radius: 12px !important; border-left: 4px solid #10B981 !important; box-shadow: 0 2px 8px rgba(16,185,129,0.2) !important; }
div.stButton > button { background: linear-gradient(135deg, #0047AB, #1E40AF) !important; color: white !important;
border-radius: 12px !important; height: 50px !important; font-size: 16px !important; font-weight: 700 !important;
box-shadow: 0 4px 12px rgba(0,71,171,0.4) !important; transition: all 0.2s !important; }
div.stButton > button:hover { box-shadow: 0 6px 20px rgba(0,71,171,0.6) !important; transform: translateY(-2px) !important; }
div.stButton > button:active { transform: translateY(0px) !important; box-shadow: 0 2px 8px rgba(0,71,171,0.3) !important; }
.login-title { font-size: 2rem !important; font-weight: 800 !important; color: #1E3A8A !important; text-align: center; margin-bottom: 20px; }
.login-container { max-width: 450px; margin: 20px auto; padding: 30px; background: rgba(255,255,255,0.95);
backdrop-filter: blur(10px); border-radius: 20px; border: 1px solid rgba(0,71,171,0.1);
box-shadow: 0 8px 32px rgba(0,71,171,0.15); }
input[type="text"], input[type="password"] { height: 45px !important; font-size: 15px !important; }
</style>
""", unsafe_allow_html=True)

# --- Supabase ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- Sessão ---
if "logado" not in st.session_state: st.session_state.logado = False
if "usuario" not in st.session_state: st.session_state.usuario = None
if "tem_busca" not in st.session_state: st.session_state.tem_busca = ""

# --- Função auxiliar ---
def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    texto = re.sub(r'[^a-zA-Z0-9\s]', '', texto)
    return texto

# --- Login / Cadastro ---
if not st.session_state.logado:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🕊️ Guia Espírita</div>', unsafe_allow_html=True)
    aba = st.radio("", ["Login", "Cadastro"], horizontal=True)

    if aba == "Login":
        email = st.text_input("", placeholder="📧 Digite seu e-mail", label_visibility="collapsed")
        senha = st.text_input("", placeholder="🔒 Digite sua senha", type="password", label_visibility="collapsed")
        if st.button("🚀 ACESSAR", use_container_width=True):
            if email.strip() and senha.strip():
                try:
                    resposta = supabase.table("acessos").select("*").eq("email", email.strip().lower()).eq("senha", senha.strip()).execute()
                    if resposta.data and len(resposta.data) > 0:
                        st.session_state.logado = True
                        st.session_state.usuario = email.strip().lower()
                    else:
                        st.error("❌ E-mail ou senha incorretos!")
                except Exception as e:
                    st.error(f"❌ Erro ao conectar: {str(e)}")
            else:
                st.error("❌ Preencha e-mail e senha!")
    else:  # Cadastro
        nome = st.text_input("", placeholder="👤 Digite seu nome completo", label_visibility="collapsed")
        email = st.text_input("", placeholder="📧 Digite seu e-mail", label_visibility="collapsed")
        senha = st.text_input("", placeholder="🔒 Crie uma senha", type="password", label_visibility="collapsed")
        senha_conf = st.text_input("", placeholder="🔒 Confirme a senha", type="password", label_visibility="collapsed")
        if st.button("📝 CADASTRAR", use_container_width=True):
            if not nome.strip() or not email.strip() or not senha.strip() or not senha_conf.strip():
                st.error("❌ Todos os campos são obrigatórios!")
            elif senha != senha_conf:
                st.error("❌ Senhas não conferem!")
            else:
                try:
                    email_limpo = email.strip().lower()
                    existe = supabase.table("acessos").select("*").eq("email", email_limpo).execute()
                    if existe.data and len(existe.data) > 0:
                        st.error("❌ E-mail já cadastrado!")
                    else:
                        supabase.table("acessos").insert({"nome": nome.strip(), "email": email_limpo, "senha": senha}).execute()
                        st.success("✅ Cadastro realizado! Agora faça login.")
                except Exception as e:
                    st.error(f"❌ Erro ao conectar: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Tela principal ---
else:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)

    # --- Menu Hamburger Recolhível ---
    with st.expander("☰ Menu", expanded=False):
        st.markdown("### Admin")
        st.markdown("### Cidades")

        # --- Carregar cidades únicas ---
        try:
            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            df.columns = df.columns.str.strip()
            col_cidade = 'CIDADE DO CENTRO ESPIRITA'  # <--- nome exato da sua planilha
            cidades_unicas = sorted(df[col_cidade].dropna().unique())
            for cidade in cidades_unicas:
                with st.expander(cidade):
                    # Mostrar os centros daquela cidade
                    centros = df[df[col_cidade]==cidade]
                    for idx, row in centros.iterrows():
                        v_nome_real = row.get('NOME', 'Centro Espírita') + " 🕊️"
                        v_fantasia = row.get('NOME FANTASIA', 'N/I')
                        v_endereco = row.get('ENDERECO', 'N/I')
                        v_resp = row.get('RESPONSAVEL', 'N/I')
                        v_celular = str(row.get('CELULAR', ''))
                        v_palestras = row.get('PALESTRA PUBLICA', '')
                        st.markdown(f"""
                        <div class="card-centro" style="position: relative;">
                            <div class="nome-grande">{v_nome_real}</div>
                            <div class="nome-fantasia">{v_fantasia}</div>
                            <div class="palestras-verde">🗣️ PALESTRAS {v_palestras}</div>
                            <div class="info-texto">👤 <b>Responsável:</b> {v_resp}</div>
                            <div class="info-texto">📍 <b>Endereço:</b> {v_endereco}</div>
                        </div>
                        """, unsafe_allow_html=True)
        except Exception as e:
            st.error("Erro ao carregar cidades: " + str(e))

    # --- Busca tradicional continua aqui ---
    busca = st.text_input("🔍 Digite nome, cidade ou qualquer palavra...", label_visibility="collapsed")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔎 PESQUISAR", use_container_width=True):
            if busca.strip():
                st.session_state.tem_busca = busca.strip()
    with col2:
        if st.button("🗑️ LIMPAR", use_container_width=True):
            st.session_state.tem_busca = ""
