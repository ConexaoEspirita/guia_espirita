import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import datetime
from supabase import create_client, Client

# =========================
# SUPABASE
# =========================
SUPABASE_URL = "COLE_SUA_URL_AQUI"
SUPABASE_KEY = "COLE_SUA_ANON_KEY_AQUI"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="🕊️ Guia Espírita", layout="wide")

# =========================
# SESSION STATE
# =========================
if "pagina" not in st.session_state:
    st.session_state["pagina"] = None
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "termo_pesquisa" not in st.session_state:
    st.session_state["termo_pesquisa"] = ""
if "admin_logado" not in st.session_state:
    st.session_state["admin_logado"] = False

# =========================
# FUNÇÕES
# =========================
def ajustar(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def normalize_text(text):
    if pd.isna(text): return ""
    return unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8').lower()

def renderizar_card(row, index):
    nome = ajustar(row.get('NOME', 'Centro Espírita'))
    fantasia = ajustar(row.get('NOME FANTASIA'))
    endereco = ajustar(row.get('ENDERECO'))
    cidade = ajustar(row.get('CIDADE DO CENTRO ESPIRITA'))
    palestra = ajustar(row.get('PALESTRA PUBLICA'))
    responsavel = ajustar(row.get('RESPONSAVEL'))
    numero = "".join(filter(str.isdigit, str(row.get('CELULAR'))))

    query = urllib.parse.quote(f"{endereco}, {cidade}")
    link_maps = f"https://www.google.com/maps/search/?api=1&query={query}"
    link_wa = f"https://wa.me/55{numero}" if len(numero)>=10 else "#"

    st.markdown(f"""
    ---
    ### {index}. {nome} 🕊️
    {"*" + fantasia + "*" if fantasia else ""}
    **🗣️ Palestra:** {palestra}  
    **👤 Responsável:** {responsavel}  
    **🏙️ Cidade:** {cidade}  
    **📍 Endereço:** {endereco}  

    [📍 Maps]({link_maps}) | [📱 WhatsApp]({link_wa})
    ---
    """)

# =========================
# LOGIN
# =========================
if not st.session_state["logado"]:

    st.title("🕊️ Guia Espírita")

    tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])

    with tab1:
        with st.form("login"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                st.session_state["logado"] = True
                st.rerun()

    with tab2:
        with st.form("cadastro"):
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")

            if st.form_submit_button("Cadastrar"):
                try:
                    supabase.table("participantes").insert({
                        "nome": nome,
                        "email": email,
                        "status": "ativo"
                    }).execute()

                    st.success("Cadastrado com sucesso!")
                    st.session_state["logado"] = True
                    st.rerun()

                except Exception as e:
                    st.error(f"Erro Supabase: {e}")

# =========================
# SISTEMA PRINCIPAL
# =========================
else:

    st.title("🕊️ Guia Espírita")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🔎 Busca Avançada"):
            st.session_state["pagina"] = "pesquisar"
            st.rerun()

        if st.button("📍 Por Cidade"):
            st.session_state["pagina"] = "cidade"
            st.rerun()

    with c2:
        if st.button("📊 Admin"):
            st.session_state["pagina"] = "admin"
            st.session_state["admin_logado"] = False
            st.rerun()

        if st.button("🚪 Sair"):
            st.session_state.clear()
            st.rerun()

    pagina = st.session_state["pagina"]

    # =========================
    # BUSCA
    # =========================
    if pagina == "pesquisar":
        st.header("🔎 Busca Avançada")

        termo = st.text_input("Digite o que busca:")
        if termo and len(termo.strip()) >= 3:

            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            df.columns = df.columns.str.strip()

            t_norm = normalize_text(termo.strip())

            res = df[df.apply(
                lambda r: t_norm in normalize_text(" ".join(r.astype(str))), axis=1)]

            if not res.empty:
                st.success(f"{len(res)} centro(s) encontrado(s)")
                for i, (_, row) in enumerate(res.iterrows(), 1):
                    renderizar_card(row, i)
            else:
                st.warning("Nada encontrado.")

    # =========================
    # POR CIDADE
    # =========================
    elif pagina == "cidade":

        st.header("📍 Por Cidade")

        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()

        cidades = sorted(df["CIDADE DO CENTRO ESPIRITA"].dropna().unique())

        escolha = st.selectbox("Selecione:", ["-- Selecione --"] + cidades)

        if escolha != "-- Selecione --":
            res = df[df["CIDADE DO CENTRO ESPIRITA"] == escolha]
            for i, (_, row) in enumerate(res.iterrows(), 1):
                renderizar_card(row, i)

    # =========================
    # ADMIN
    # =========================
    elif pagina == "admin":

        if not st.session_state["admin_logado"]:

            st.header("🔐 Login Admin")

            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")

            if st.button("Entrar Admin"):
                if usuario == "estudantesabio" and senha == "2026":
                    st.session_state["admin_logado"] = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos")

        else:

            st.header("📊 Participantes")

            try:
                res = supabase.table("participantes") \
                    .select("*") \
                    .order("created_at", desc=True) \
                    .execute()

                dados = res.data

                if dados:

                    st.info(f"Total: {len(dados)} participantes")

                    for i, p in enumerate(dados, 1):

                        created_at = p.get("created_at")

                        if created_at:
                            try:
                                dt = datetime.datetime.fromisoformat(
                                    created_at.replace("Z", "+00:00")
                                )
                                data_fmt = dt.strftime("%d/%m/%Y - %H:%M:%S")
                            except:
                                data_fmt = created_at
                        else:
                            data_fmt = "-"

                        st.markdown(f"""
                        **{i}. {p.get('nome','N/D')}**  
                        {p.get('email','N/D')}  
                        📅 {data_fmt}
                        ---
                        """)

                else:
                    st.info("Nenhum participante cadastrado.")

                if st.button("🔐 Sair Admin"):
                    st.session_state["admin_logado"] = False
                    st.rerun()

            except Exception as e:
                st.error(f"Erro Supabase: {e}")
