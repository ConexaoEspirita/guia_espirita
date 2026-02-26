import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# ==============================
# INICIALIZAÇÃO SEGURA
# ==============================
if "pagina" not in st.session_state:
    st.session_state["pagina"] = None

if "logado" not in st.session_state:
    st.session_state["logado"] = False


# ==============================
# CSS
# ==============================
st.markdown("""
<style>
.stApp { background: #f4f7f9; }

.titulo-profissional {
    color:#1E3A8A;
    font-weight:700;
    font-size:26px;
    margin-top:10px;
}

.card-centro { 
    background:white;
    padding:20px;
    border-radius:15px;
    margin-bottom:20px;
    box-shadow:0 6px 18px rgba(0,0,0,0.1);
    border-left:8px solid #0047AB;
}
</style>
""", unsafe_allow_html=True)


# ==============================
# FUNÇÕES
# ==============================
def renderizar_card(row, index):
    nome = str(row.get("NOME", "Centro Espírita"))
    cidade = str(row.get("CIDADE DO CENTRO ESPIRITA", ""))
    endereco = str(row.get("ENDERECO", ""))

    query = urllib.parse.quote(f"{endereco}, {cidade}")
    link_maps = f"https://www.google.com/maps/search/?api=1&query={query}"

    st.markdown(f"""
    <div class="card-centro">
        <b>{index}. {nome}</b><br>
        📍 {cidade}<br>
        🏠 {endereco}<br><br>
        <a href="{link_maps}" target="_blank">Ver no Mapa</a>
    </div>
    """, unsafe_allow_html=True)


# ==============================
# LOGIN
# ==============================
if not st.session_state["logado"]:

    st.markdown("<div class='titulo-profissional'>🕊️ Guia Espírita</div>", unsafe_allow_html=True)

    with st.form("login"):
        st.text_input("E-mail")
        st.text_input("Senha", type="password")

        if st.form_submit_button("Entrar", use_container_width=True):
            st.session_state["logado"] = True
            st.rerun()

else:

    @st.cache_data
    def carregar():
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        return df

    df = carregar()

    pagina = st.session_state["pagina"]

    # ==============================
    # MENU PRINCIPAL
    # ==============================
    if pagina is None:

        st.markdown("<div class='titulo-profissional'>🕊️ Guia Espírita</div>", unsafe_allow_html=True)
        st.write("")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔎 Busca Avançada", use_container_width=True):
                st.session_state["pagina"] = "pesquisar"
                st.rerun()

            if st.button("📍 Localizar por Cidade", use_container_width=True):
                st.session_state["pagina"] = "cidade"
                st.rerun()

        with col2:
            if st.button("📊 Painel Administrativo", use_container_width=True):
                st.session_state["pagina"] = "admin"
                st.rerun()

            if st.button("🕊️ Mensagens Espíritas", use_container_width=True):
                st.session_state["pagina"] = "frases"
                st.rerun()

        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear()
            st.cache_data.clear()
            st.rerun()

    # ==============================
    # PÁGINAS INTERNAS
    # ==============================
    else:

        col1, col2 = st.columns([1, 10])

        with col1:
            if st.button("⬅️"):
                st.session_state["pagina"] = None
                st.rerun()

        with col2:
            titulos = {
                "pesquisar": "🔎 Busca Avançada",
                "cidade": "📍 Localizar por Cidade",
                "admin": "📊 Painel Administrativo",
                "frases": "🕊️ Mensagens Espíritas"
            }

            st.markdown(
                f"<div class='titulo-profissional'>{titulos[pagina]}</div>",
                unsafe_allow_html=True
            )

        # BUSCA
        if pagina == "pesquisar":

            termo = st.text_input("Digite pelo menos 3 letras:")

            if termo and len(termo) >= 3:

                termo = termo.lower()
                resultado = df[df.apply(
                    lambda row: termo in " ".join(row.astype(str)).lower(),
                    axis=1
                )]

                if not resultado.empty:
                    for i, (_, row) in enumerate(resultado.iterrows(), 1):
                        renderizar_card(row, i)
                else:
                    st.warning("Nenhum resultado encontrado.")

        # CIDADE (abre limpa)
        elif pagina == "cidade":

            cidades = sorted(df["CIDADE DO CENTRO ESPIRITA"].dropna().unique())

            escolha = st.selectbox(
                "Selecione uma cidade:",
                ["-- Selecione --"] + list(cidades)
            )

            if escolha != "-- Selecione --":

                resultado = df[df["CIDADE DO CENTRO ESPIRITA"] == escolha]

                for i, (_, row) in enumerate(resultado.iterrows(), 1):
                    renderizar_card(row, i)

        # ADMIN
        elif pagina == "admin":

            st.metric("Total de Centros", len(df))
            st.metric("Cidades Únicas", df["CIDADE DO CENTRO ESPIRITA"].nunique())

        # FRASES
        elif pagina == "frases":

            st.markdown("""
            > Fora da caridade não há salvação. — Allan Kardec  
            > Amai-vos uns aos outros. — Jesus  
            > Ninguém é perfeito, mas todos podem melhorar. — Emmanuel  
            """)
