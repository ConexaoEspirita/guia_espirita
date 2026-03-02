import streamlit as st
import pandas as pd

# ======================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================
st.set_page_config(
    page_title="Guia Espírita",
    layout="wide"
)

# ======================================
# CARREGAR PLANILHA
# ======================================
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel("guia.xlsx")
        df.columns = df.columns.str.strip()
        df = df.fillna("")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar guia.xlsx: {e}")
        st.stop()

df = carregar_dados()

# ======================================
# MENU LATERAL
# ======================================
menu = st.sidebar.radio(
    "Menu",
    ["🔎 Pesquisa", "🏙 Por Cidade"]
)

# ======================================
# PESQUISA LIVRE
# ======================================
if menu == "🔎 Pesquisa":

    st.title("🔎 Buscar Casa Espírita")

    busca = st.text_input("Digite nome, bairro ou cidade")

    if busca:
        busca = busca.lower()

        resultado = df[
            df.apply(
                lambda row: busca in str(row).lower(),
                axis=1
            )
        ]

        st.write(f"Encontrado(s): {len(resultado)}")

        for _, row in resultado.iterrows():
            st.markdown("---")
            st.subheader(row["Nome"])
            st.write("📍 Cidade:", row["Cidade"])
            st.write("📌 Endereço:", row["Endereço"])
            st.write("📞 Telefone:", row["Telefone"])
            st.write("🗓 Dias:", row["Dias"])

# ======================================
# FILTRO POR CIDADE
# ======================================
elif menu == "🏙 Por Cidade":

    st.title("🏙 Casas por Cidade")

    cidades = sorted(df["Cidade"].unique())

    cidade_selecionada = st.selectbox(
        "Escolha a cidade",
        cidades
    )

    resultado = df[df["Cidade"] == cidade_selecionada]

    st.write(f"Encontrado(s): {len(resultado)}")

    for _, row in resultado.iterrows():
        st.markdown("---")
        st.subheader(row["Nome"])
        st.write("📌 Endereço:", row["Endereço"])
        st.write("📞 Telefone:", row["Telefone"])
        st.write("🗓 Dias:", row["Dias"])

# ======================================
# FRASE FINAL
# ======================================
st.markdown("---")
st.markdown(
    "<center><i>“Fora da caridade não há salvação.” – Allan Kardec</i></center>",
    unsafe_allow_html=True
)
