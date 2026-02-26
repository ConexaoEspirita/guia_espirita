import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import os

st.set_page_config(layout="wide")

# =========================
# CONFIG ADMIN
# =========================
ADMIN_EMAIL = "admin@guia.com"
ADMIN_SENHA = hashlib.sha256("1234".encode()).hexdigest()

# =========================
# FUNÇÕES
# =========================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# =========================
# CRIAR ARQUIVO USUARIOS
# =========================
if not os.path.exists("usuarios.csv"):
    df_init = pd.DataFrame(columns=["nome", "email", "senha", "data_cadastro"])
    df_init.to_csv("usuarios.csv", index=False)

# =========================
# SESSION
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "admin" not in st.session_state:
    st.session_state.admin = False

# =========================
# LOGIN / CADASTRO / RESET
# =========================
if not st.session_state.logado:

    st.title("🕊️ Guia Espírita")

    aba = st.radio("", ["Login", "Cadastrar", "Esqueci a senha"], horizontal=True)

    if aba == "Cadastrar":

        with st.form("cadastro"):
            nome = st.text_input("Nome")
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")

            if st.form_submit_button("Cadastrar"):

                if not nome.strip() or not email.strip() or not senha.strip():
                    st.error("Preencha todos os campos.")
                elif email.strip().lower() == ADMIN_EMAIL.lower():
                    st.error("Email reservado.")
                else:
                    df_users = pd.read_csv("usuarios.csv")

                    if email.strip().lower() in df_users["email"].str.lower().values:
                        st.warning("Email já cadastrado.")
                    else:
                        novo = pd.DataFrame([{
                            "nome": nome.strip(),
                            "email": email.strip().lower(),
                            "senha": hash_senha(senha),
                            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        }])

                        df_users = pd.concat([df_users, novo], ignore_index=True)
                        df_users.to_csv("usuarios.csv", index=False)
                        st.success("Cadastro realizado!")

    elif aba == "Login":

        with st.form("login"):
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

        with st.form("reset"):
            email_reset = st.text_input("Email cadastrado")
            nova_senha = st.text_input("Nova senha", type="password")

            if st.form_submit_button("Redefinir"):

                if email_reset.strip().lower() not in df_users["email"].str.lower().values:
                    st.error("Email não encontrado.")
                else:
                    df_users.loc[
                        df_users["email"].str.lower() == email_reset.strip().lower(),
                        "senha"
                    ] = hash_senha(nova_senha)

                    df_users.to_csv("usuarios.csv", index=False)
                    st.success("Senha redefinida!")

# =========================
# AREA LOGADA
# =========================
else:

    # MENU HORIZONTAL
    if st.session_state.admin:
        pagina = st.radio("", ["Início", "Frases", "Admin", "Sair"], horizontal=True)
    else:
        pagina = st.radio("", ["Início", "Frases", "Sair"], horizontal=True)

    st.markdown("---")

    # =========================
    # INÍCIO
    # =========================
    if pagina == "Início":

        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()

        st.title("🕊️ Guia Espírita")

        # Detecta coluna nome
        col_nome = [c for c in df.columns if "nome" in c.lower()]
        col_cidade = [c for c in df.columns if "cidade" in c.lower()]

        if not col_nome or not col_cidade:
            st.error("Colunas 'nome' ou 'cidade' não encontradas na planilha.")
            st.write("Colunas encontradas:", df.columns)
            st.stop()

        col_nome = col_nome[0]
        col_cidade = col_cidade[0]

        busca = st.text_input("🔎 Pesquisa geral")

        cidades = sorted(df[col_cidade].dropna().unique())
        cidade_escolhida = st.selectbox("📍 Filtrar por cidade", ["Todas"] + list(cidades))

        df_filtrado = df.copy()

        if busca:
            df_filtrado = df_filtrado[
                df_filtrado.apply(lambda row: busca.lower() in str(row).lower(), axis=1)
            ]

        if cidade_escolhida != "Todas":
            df_filtrado = df_filtrado[df_filtrado[col_cidade] == cidade_escolhida]

        st.markdown(f"### 🔎 Resultados: {len(df_filtrado)} encontrados")

        for _, row in df_filtrado.iterrows():
            st.markdown(f"""
            ### {row[col_nome]}
            📍 {row[col_cidade]}
            ---
            """)

    # =========================
    # FRASES
    # =========================
    elif pagina == "Frases":

        st.title("🕊️ Frase Espírita")
        st.markdown("> **Fora da caridade não há salvação.** — Allan Kardec")

    # =========================
    # ADMIN
    # =========================
    elif pagina == "Admin" and st.session_state.admin:

        st.title("🔒 Área do Administrador")

        df_users = pd.read_csv("usuarios.csv")

        st.metric("👥 Usuários cadastrados", len(df_users))

        if st.button("Ver usuários cadastrados"):
            st.dataframe(df_users)

    # =========================
    # SAIR
    # =========================
    elif pagina == "Sair":
        st.session_state.logado = False
        st.session_state.admin = False
        st.rerun()
