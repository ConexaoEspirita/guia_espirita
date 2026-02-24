import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="centered")
st.cache_data.clear()

# ==============================
# ESTILO VISUAL
# ==============================
st.markdown("""
<style>
.stApp { background-color: #F8F9FA; }

.card-centro {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    border-left: 8px solid #0047AB;
    margin-bottom: 15px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.nome-grande {
    color: #0047AB;
    font-size: 26px;
    font-weight: bold;
    line-height: 1.1;
}

.nome-fantasia {
    color: #5CACE2 !important;
    font-size: 17px !important;
    font-weight: 500;
    font-style: italic;
    margin-bottom: 12px;
    display: block;
}

.info-texto {
    color: #444;
    font-size: 14px;
    margin-bottom: 4px;
}

div.stLinkButton > a {
    width: 100% !important;
    font-weight: bold !important;
    height: 45px !important;
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
# FUNÇÕES AUXILIARES
# ==============================
def limpar_busca(texto):
    texto = unicodedata.normalize('NFD', str(texto))
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto.lower()

# ==============================
# CONTROLE DE LOGIN
# ==============================
if "logado" not in st.session_state:
    st.session_state.logado = False

# ==============================
# TELA DE LOGIN
# ==============================
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
        try:
            df = pd.read_excel("guia.xlsx").astype(str).replace("nan", "")
            termo = limpar_busca(busca)
            mascara = df.apply(lambda linha: linha.apply(limpar_busca).str.contains(termo)).any(axis=1)
            resultados = df[mascara]

            if not resultados.empty:
                for _, row in resultados.iterrows():
                    # Ordem das colunas: A=Fantasia, B=Nome Real, C=Cidade, D=Endereço, E=Palestra Pública, F=Responsável, G=Celular
                    v_fantasia = row.iloc[0]
                    v_nome_real = row.iloc[1]
                    v_cidade = row.iloc[2]
                    v_endereco = row.iloc[3]
                    v_palestra = row.iloc[4]
                    v_resp = row.iloc[5]
                    v_celular = row.iloc[6]

                    # CARD VISUAL
                    st.markdown(f"""
                    <div class="card-centro">
                        <div class="nome-grande">{v_nome_real}</div>
                        <div class="nome-fantasia">{v_fantasia}</div>
                        <div class="info-texto">👤 <b>Responsável:</b> {v_resp}</div>
                        <div class="info-texto">📍 <b>Endereço:</b> {v_endereco}</div>
                        <div class="info-texto">🏙️ <b>Cidade:</b> {v_cidade}</div>
                        {f'<div class="info-texto">🗓️ <b>Palestra Pública:</b> {v_palestra}</div>' if v_palestra else ''}
                    </div>
                    """, unsafe_allow_html=True)

                    # BOTÕES MAPS E WHATSAPP
                    col1, col2 = st.columns(2)

                    with col1:
                        if v_endereco:
                            query = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                            st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}")

                    with col2:
                        if v_celular and v_celular.strip() != "":
                            numero = ''.join(filter(str.isdigit, v_celular))
                            if len(numero) >= 10:
                                st.link_button("💬 WHATSAPP", f"https://wa.me/55{numero}")

                    st.write("")

            else:
                st.warning("Nenhum resultado encontrado.")
        except Exception as erro:
            st.error(f"Erro: {erro}")
