import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(
    page_title="Guia Espírita",
    page_icon="🕊️",
    layout="centered"
)

st.cache_data.clear()

# ==============================
# ESTILO PREMIUM
# ==============================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(to bottom, #F8F9FA, #E9F2FF);
}

.card-centro {
    background-color: white;
    padding: 25px;
    border-radius: 18px;
    border-left: 10px solid #0047AB;
    margin-bottom: 20px;
    box-shadow: 0 8px 18px rgba(0,0,0,0.08);
    transition: 0.3s;
}

.card-centro:hover {
    transform: scale(1.01);
    box-shadow: 0 12px 22px rgba(0,0,0,0.12);
}

.nome-grande {
    color: #003366;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

.nome-fantasia {
    color: #5CACE2;
    font-size: 18px;
    font-style: italic;
    margin-top: -5px;
    margin-bottom: 15px;
}

.info-texto {
    color: #444;
    font-size: 14px;
    margin-bottom: 6px;
}

div.stLinkButton > a {
    width: 100% !important;
    font-weight: bold !important;
    height: 48px !important;
    border-radius: 10px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# CONEXÃO SUPABASE
# ==============================
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ==============================
# FUNÇÕES
# ==============================
def limpar_busca(texto):
    texto = unicodedata.normalize('NFD', str(texto))
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto.lower()

# ==============================
# LOGIN
# ==============================
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:

    st.title("🕊️ Guia Espírita 🕊️")

    email = st.text_input("E-mail").strip().lower()
    senha = st.text_input("Senha", type="password")

    if st.button("ACESSAR GUIA"):
        resposta = (
            supabase
            .table("acessos")
            .select("*")
            .eq("email", email)
            .eq("senha", senha)
            .execute()
        )

        if resposta.data:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Dados incorretos!")

# ==============================
# ÁREA PRINCIPAL
# ==============================
else:

    st.title("🕊️ Guia Espírita")

    busca = st.text_input("🔍 O que você procura?", placeholder="Digite aqui...")

    if busca:

        df = pd.read_excel("guia.xlsx").astype(str).replace("nan", "")
        termo = limpar_busca(busca)

        mascara = df.apply(
            lambda linha: linha.apply(limpar_busca).str.contains(termo)
        ).any(axis=1)

        resultados = df[mascara]

        if not resultados.empty:

            for _, row in resultados.iterrows():

                v_fantasia = row.iloc[0]
                v_nome_real = row.iloc[1]
                v_cidade = row.iloc[2]
                v_endereco = row.iloc[3]
                v_palestra = row.iloc[4]
                v_resp = row.iloc[5]
                v_celular = row.iloc[6]

                # CARD
                st.markdown(f"""
                <div class="card-centro">

                    <div style="text-align:center;">
                        <div class="nome-grande">{v_nome_real}</div>
                        <div class="nome-fantasia">{v_fantasia}</div>
                    </div>

                    <div class="info-texto">👤 <b>Responsável:</b> {v_resp}</div>
                    <div class="info-texto">📍 <b>Endereço:</b> {v_endereco}</div>
                    <div class="info-texto">🏙️ <b>Cidade:</b> {v_cidade}</div>
                    {f'<div class="info-texto">🗓️ <b>Palestra:</b> {v_palestra}</div>' if v_palestra else ''}

                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                # MAPS
                with col1:
                    if v_endereco:
                        query = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                        link_maps = f"https://www.google.com/maps/search/?api=1&query={query}"
                        st.link_button("🗺️ GOOGLE MAPS", link_maps)

                # WHATSAPP
                with col2:
                    if v_celular and v_celular.strip() != "":
                        numero = ''.join(filter(str.isdigit, v_celular))

                        if len(numero) >= 10:
                            if not numero.startswith("55"):
                                numero = "55" + numero

                            link_whats = f"https://wa.me/{numero}"
                            st.link_button("💬 WHATSAPP", link_whats)

                st.write("")

        else:
            st.warning("Nenhum resultado encontrado.")
