import streamlit as st
import pandas as pd
import urllib.parse
import re
import os
import hashlib
from datetime import datetime

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# =========================
# CONFIG ADMIN
# =========================
ADMIN_EMAIL = "admin@guia.com"
ADMIN_SENHA = hashlib.sha256("123456".encode()).hexdigest()

# =========================
# FUNÇÕES USUÁRIO
# =========================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_arquivo_usuarios():
    if not os.path.exists("usuarios.csv"):
        df_users = pd.DataFrame(columns=["nome", "email", "senha", "data_cadastro"])
        df_users.to_csv("usuarios.csv", index=False)

criar_arquivo_usuarios()

# =========================
# CSS ORIGINAL
# =========================
st.markdown("""
<style>
[data-testid="stArrowBack"] { display: none !important; }
section[data-testid="stSidebar"] > div { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.stApp { background: #f4f7f9; }

.card-centro { 
    background: white !important; padding: 25px; border-radius: 20px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.12); 
    margin-bottom: 25px; border-left: 12px solid #0047AB; position: relative;
}
.numero-badge { position: absolute; top: 15px; right: 20px; background: #f0f4f8; color: #7f8c8d; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 800; }
.nome-centro { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800; display: block; }
.nome-fantasia { color: #3B82F6 !important; font-size: 16px !important; font-style: italic; font-weight: 500; margin-top: 2px; display: block; }
.palestras-verde { color: #065F46 !important; font-weight: 700; background: #D1FAE5; padding: 10px; border-radius: 10px; margin: 12px 0; border: 1px solid #10B981; }
.info-linha { margin: 8px 0; font-size: 15px; color: #333 !important; }
.label-bold { font-weight: 800; color: #0047AB; text-transform: uppercase; font-size: 13px; }
.btn-row { display: flex; gap: 12px; margin-top: 20px; }
.btn-link { text-decoration: none !important; color: white !important; padding: 14px; border-radius: 12px; font-weight: 800; text-align: center; flex: 1; display: inline-block; }
.bg-wa { background-color: #25D366; }
.bg-maps { background-color: #4285F4; }
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES DOS CARDS
# =========================
def ajustar_texto(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def renderizar_card(row, index):
    nome = ajustar_texto(row.get('NOME', 'Centro Espírita'))
    fantasia = ajustar_texto(row.get('NOME FANTASIA', ''))
    end = ajustar_texto(row.get('ENDERECO', ''))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', ''))
    palestras = ajustar_texto(row.get('PALESTRA PUBLICA', 'Consulte'))
    resp = ajustar_texto(row.get('RESPONSAVEL', 'N/I'))

    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    link_wa = f"https://wa.me/+55{whats_num}" if len(whats_num) >= 10 else "#"

    nome_google = ajustar_texto(row.get('NOME_GOOGLE_MAPS', ''))
    if nome_google:
        query_maps = urllib.parse.quote(nome_google)
    else:
        endereco_limpo = re.sub(r'[,\\s]+', ', ', end)[:100]
        query_maps = urllib.parse.quote(f"{endereco_limpo}, {cid}")
    link_maps = f"https://www.google.com/maps/search/?api=1&query={query_maps}"

    st.markdown(f"""
    <div class="card-centro">
        <div class="numero-badge">#{index}</div>
        <span class="nome-centro">{nome} 🕊️</span>
        {f'<span class="nome-fantasia">{fantasia}</span>' if fantasia else ''}
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

# =========================
# SESSION STATE
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "admin" not in st.session_state:
    st.session_state.admin = False
if "pagina" not in st.session_state:
    st.session_state.pagina = None
if "menu_aberto" not in st.session_state:
    st.session_state.menu_aberto = False

# =========================
# LOGIN / CADASTRO / RESET
# =========================
if not st.session_state.logado:

    st.title("🕊️ Guia Espírita")

    aba = st.radio("Escolha:", ["Login", "Cadastrar", "Esqueci a senha"], horizontal=True)

    if aba == "Cadastrar":
        with st.form("cadastro_form"):
            nome = st.text_input("Nome")
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")

            if st.form_submit_button("Cadastrar"):

                if not nome.strip() or not email.strip() or not senha.strip():
                    st.error("Nome, email e senha são obrigatórios.")

                elif email.strip().lower() == ADMIN_EMAIL.lower():
                    st.error("Não é permitido cadastrar com o email do administrador.")

                else:
                    df_users = pd.read_csv("usuarios.csv")

                    if email.strip().lower() in df_users["email"].str.lower().values:
                        st.warning("Email já cadastrado.")
                    else:
                        nova_linha = pd.DataFrame([{
                            "nome": nome.strip(),
                            "email": email.strip().lower(),
                            "senha": hash_senha(senha),
                            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        }])
                        df_users = pd.concat([df_users, nova_linha], ignore_index=True)
                        df_users.to_csv("usuarios.csv", index=False)
                        st.success("Cadastro realizado com sucesso!")

    elif aba == "Login":
        with st.form("login_form"):
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")

            if st.form_submit_button("Entrar"):

                if email.strip().lower() == ADMIN_EMAIL.lower() and hash_senha(senha) == ADMIN_SENHA:
                    st.session_state.logado = True
                    st.session_state.admin = True
                    st.rerun()

                df_users = pd.read_csv("usuarios.csv")

                usuario = df_users[
                    (df_users["email"].str.lower() == email.strip().lower()) &
                    (df_users["senha"] == hash_senha(senha))
                ]

                if not usuario.empty:
                    st.session_state.logado = True
                    st.session_state.admin = False
                    st.rerun()
                else:
                    st.error("Email ou senha incorretos.")

    elif aba == "Esqueci a senha":

        df_users = pd.read_csv("usuarios.csv")

        if df_users.empty:
            st.warning("Nenhum usuário cadastrado ainda.")
        else:
            with st.form("reset_form"):
                email_reset = st.text_input("Digite seu email cadastrado")
                nova_senha = st.text_input("Nova senha", type="password")

                if st.form_submit_button("Redefinir senha"):

                    if email_reset.strip().lower() not in df_users["email"].str.lower().values:
                        st.error("Email não encontrado.")
                    else:
                        df_users.loc[
                            df_users["email"].str.lower() == email_reset.strip().lower(),
                            "senha"
                        ] = hash_senha(nova_senha)

                        df_users.to_csv("usuarios.csv", index=False)
                        st.success("Senha redefinida com sucesso!")

# =========================
# SISTEMA PRINCIPAL
# =========================
else:

    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()

    st.title("🕊️ Bem-vindo ao Guia Espírita")

    if st.button("📋 " + ("Fechar Menu" if st.session_state.menu_aberto else "Abrir Menu"), use_container_width=True):
        st.session_state.menu_aberto = not st.session_state.menu_aberto
        st.rerun()

    if st.session_state.menu_aberto:

        if st.button("🔎 Pesquisar Geral"):
            st.session_state.pagina = "pesquisar"

        if st.button("📍 Por Cidade"):
            st.session_state.pagina = "cidade"

        if st.session_state.admin:
            if st.button("📊 Admin"):
                st.session_state.pagina = "admin"

        if st.button("🕊️ Frases"):
            st.session_state.pagina = "frases"

        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.session_state.admin = False
            st.rerun()

    pagina = st.session_state.get("pagina")

    if pagina == "frases":
        st.markdown("### 🕊️ Frases Espíritas")
        st.markdown("> **Fora da caridade não há salvação.** — Allan Kardec")

    elif pagina == "admin" and st.session_state.admin:

        st.markdown("## 📊 Painel Administrativo")

        df_users = pd.read_csv("usuarios.csv")

        total_unicos = df_users["email"].nunique()
        st.metric("👥 Total de Participantes", total_unicos)

        if not df_users.empty:
            df_users["data_convertida"] = pd.to_datetime(
                df_users["data_cadastro"], format="%d/%m/%Y %H:%M:%S"
            )
            df_users["dia"] = df_users["data_convertida"].dt.date
            crescimento = df_users.groupby("dia")["email"].nunique()
            st.line_chart(crescimento)

        st.markdown("---")

        for i, row in df_users.iterrows():
            col1, col2 = st.columns([5,1])

            with col1:
                st.markdown(f"""
                **Nome:** {row['nome']}  
                **Email:** {row['email']}  
                **Cadastro:** {row['data_cadastro']}
                """)

            with col2:
                if st.button("🗑", key=f"del_{i}"):
                    df_users = df_users.drop(i)
                    df_users.to_csv("usuarios.csv", index=False)
                    st.success("Usuário removido.")
                    st.rerun()

            st.markdown("---")
