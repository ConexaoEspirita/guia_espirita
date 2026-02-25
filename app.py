import streamlit as st
import pandas as pd
import unicodedata
import re
import urllib.parse
from supabase import create_client

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Guia Espírita",
    page_icon="🕊️",
    layout="wide"
)

# ---------------- CSS PREMIUM ----------------
st.markdown("""
<style>

/* Remove espaço estranho do topo */
.block-container {
    padding-top: 2rem !important;
}

/* Fundo suave */
.stApp {
    background: linear-gradient(135deg,#f5f9ff 0%, #e8f2ff 100%);
}

/* Título principal */
.titulo-app {
    text-align:center;
    font-size:38px;
    font-weight:800;
    color:#0f2c59;
    margin-bottom:20px;
}

/* Login container */
.login-box {
    max-width:480px;
    margin:auto;
    padding:40px;
    background:white;
    border-radius:20px;
    box-shadow:0 15px 40px rgba(0,0,0,0.1);
}

/* Barra Google */
.search-box {
    background:white;
    padding:15px;
    border-radius:40px;
    box-shadow:0 8px 25px rgba(0,0,0,0.08);
    margin-bottom:30px;
}

/* Card */
.card {
    background:white;
    padding:22px;
    border-radius:18px;
    box-shadow:0 10px 30px rgba(0,0,0,0.08);
    margin-bottom:18px;
    position:relative;
}

/* Número discreto */
.card-number {
    position:absolute;
    top:10px;
    right:15px;
    font-size:12px;
    opacity:0.4;
}

/* Nome principal */
.nome-principal {
    font-size:22px;
    font-weight:800;
    color:#0f2c59;
}

/* Nome fantasia */
.nome-fantasia {
    font-style:italic;
    color:#3a6ea5;
}

/* Botões */
.stButton>button {
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- FUNÇÕES ----------------

def limpar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    return texto

# ---------------- SUPABASE ----------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ---------------- SESSION ----------------
if "logado" not in st.session_state:
    st.session_state.logado = False

if "modo" not in st.session_state:
    st.session_state.modo = "pesquisa"

if "cidade_aberta" not in st.session_state:
    st.session_state.cidade_aberta = None

# ---------------- LOGIN ----------------
if not st.session_state.logado:

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="titulo-app">🕊️ Guia Espírita</div>', unsafe_allow_html=True)

    aba = st.radio("", ["Login", "Cadastro"], horizontal=True)

    if aba == "Login":
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            resposta = supabase.table("acessos").select("*").eq("email", email).eq("senha", senha).execute()
            if resposta.data:
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos")

    else:
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Cadastrar"):
            supabase.table("acessos").insert({
                "nome": nome,
                "email": email,
                "senha": senha
            }).execute()
            st.success("Cadastro realizado!")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- APP PRINCIPAL ----------------
else:

    st.markdown('<div class="titulo-app">🕊️ Guia Espírita</div>', unsafe_allow_html=True)

    # -------- MENU HAMBURGER --------
    with st.expander("☰ Menu", expanded=False):

        if st.button("Cidades"):
            st.session_state.modo = "cidades"
            st.rerun()

        # Admin escondido automaticamente quando clicar em cidades
        if st.session_state.modo != "cidades":
            if st.button("Admin"):
                st.info("Área administrativa futura")

    # -------- CARREGA PLANILHA --------
    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()

    # -------- MODO PESQUISA GOOGLE --------
    if st.session_state.modo == "pesquisa":

        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        col1, col2 = st.columns([8,2])
        with col1:
            termo = st.text_input("", placeholder="🔎 Pesquise nome, cidade, responsável...")
        with col2:
            buscar = st.button("Buscar")
        st.markdown('</div>', unsafe_allow_html=True)

        if buscar and termo:
            termo_limpo = limpar_texto(termo)

            resultados = []
            for _, row in df.iterrows():
                texto_total = " ".join([
                    limpar_texto(row.get("NOME","")),
                    limpar_texto(row.get("NOME FANTASIA","")),
                    limpar_texto(row.get("CIDADE DO CENTRO ESPIRITA","")),
                    limpar_texto(row.get("RESPONSAVEL",""))
                ])

                if termo_limpo in texto_total:
                    resultados.append(row)

            for i, row in enumerate(resultados, start=1):

                numero = ''.join(filter(str.isdigit, str(row.get("CELULAR",""))))
                query = urllib.parse.quote(f"{row.get('ENDERECO','')} {row.get('CIDADE DO CENTRO ESPIRITA','')}")

                st.markdown(f"""
                <div class="card">
                    <div class="card-number">{i}</div>
                    <div class="nome-principal">{row.get('NOME','')} 🕊️</div>
                    <div class="nome-fantasia">{row.get('NOME FANTASIA','')}</div>
                    <p><b>Responsável:</b> {row.get('RESPONSAVEL','')}</p>
                    <p><b>Endereço:</b> {row.get('ENDERECO','')}</p>
                    <p><b>Cidade:</b> {row.get('CIDADE DO CENTRO ESPIRITA','')}</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}")
                with col2:
                    if numero:
                        st.link_button("💬 WhatsApp", f"https://wa.me/55{numero}")

    # -------- MODO CIDADES --------
    if st.session_state.modo == "cidades":

        cidades = sorted(df["CIDADE DO CENTRO ESPIRITA"].dropna().unique())

        for cidade in cidades:
            total = len(df[df["CIDADE DO CENTRO ESPIRITA"] == cidade])

            if st.button(f"{cidade} ({total})"):
                st.session_state.cidade_aberta = cidade
                st.rerun()

        if st.session_state.cidade_aberta:

            cidade = st.session_state.cidade_aberta
            centros = df[df["CIDADE DO CENTRO ESPIRITA"] == cidade]

            st.markdown(f"## {cidade}")

            for i, row in enumerate(centros.iterrows(), start=1):
                row = row[1]

                numero = ''.join(filter(str.isdigit, str(row.get("CELULAR",""))))
                query = urllib.parse.quote(f"{row.get('ENDERECO','')} {cidade}")

                st.markdown(f"""
                <div class="card">
                    <div class="card-number">{i}</div>
                    <div class="nome-principal">{row.get('NOME','')} 🕊️</div>
                    <div class="nome-fantasia">{row.get('NOME FANTASIA','')}</div>
                    <p><b>Responsável:</b> {row.get('RESPONSAVEL','')}</p>
                    <p><b>Endereço:</b> {row.get('ENDERECO','')}</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}")
                with col2:
                    if numero:
                        st.link_button("💬 WhatsApp", f"https://wa.me/55{numero}")

            if st.button("− Recolher cidade"):
                st.session_state.cidade_aberta = None
                st.rerun()
