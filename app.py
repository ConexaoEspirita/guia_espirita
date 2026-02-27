import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata

st.set_page_config(page_title="Guia Espírita", layout="wide")

# =========================
# SESSION STATE
# =========================
if "pagina" not in st.session_state:
    st.session_state["pagina"] = None
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "termo_pesquisa" not in st.session_state:
    st.session_state["termo_pesquisa"] = ""

# =========================
# CSS COMPLETO
# =========================
st.markdown("""
<style>
.stApp { background: #f4f7f9; }
.titulo-grande { font-size: 32px; font-weight: 800; margin-bottom: 8px; }

/* CONTORNO NO CAMPO DE PESQUISA */
div.stTextInput > div > div > input {
    border: 3px solid #4285F4 !important;
    border-radius: 15px !important;
    padding: 12px 15px !important;
    box-shadow: 0 4px 12px rgba(66,133,244,0.2) !important;
    background-color: white !important;
    font-size: 16px !important;
}
div.stTextInput > div > div > input:focus {
    border-color: #1E40AF !important;
    box-shadow: 0 0 0 3px rgba(66,133,244,0.3) !important;
}

/* SELECTBOX */
div.stSelectbox > div > div > select {
    border: 3px solid #10B981 !important;
    border-radius: 15px !important;
    padding: 12px 15px !important;
    box-shadow: 0 4px 12px rgba(16,185,129,0.2) !important;
}

.card-centro { 
    background: white;
    padding: 25px;
    border-radius: 20px; 
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.12); 
    border-left: 12px solid #0060D0;  
    position: relative;
}

.numero-badge { 
    position: absolute;
    top: 12px;
    right: 15px;
    background: #f0f4f8;
    color: #7f8c8d;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
}

.nome-centro { color: #1E3A8A; font-size: 22px; font-weight: 800; }
.nome-fantasia { color: #3B82F6; font-size: 16px; font-style: italic; }
.palestras-verde { color:#065F46; font-weight:700; background:#D1FAE5; padding:8px; border-radius:8px; margin:10px 0; border:1px solid #10B981; }
.info-linha { margin:5px 0; font-size:15px; }
.btn-row { display:flex; gap:8px; margin-top:10px; }
.btn-link { text-decoration:none; color:white; padding:8px 12px; border-radius:8px; font-weight:700; text-align:center; font-size:13px; flex:1; }
.bg-maps { background:#4285F4; }
.bg-wa { background:#25D366; }
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES
# =========================
def ajustar(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def normalize_text(text):
    if pd.isna(text):
        return ""
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
    link_wa = f"https://wa.me/+55{numero}" if len(numero)>=10 else "#"

    st.markdown(f"""
    <div class="card-centro">
        <div class="numero-badge">#{index}</div>
        <div class="nome-centro">{nome} 🕊️</div>
        {"<div class='nome-fantasia'>" + fantasia + "</div>" if fantasia else ""}
        <div class="palestras-verde">🗣️ PALESTRA: {palestra}</div>
        <div class="info-linha">🏙️ <b>Cidade:</b> {cidade}</div>
        <div class="info-linha">📍 <b>Endereço:</b> {endereco}</div>
        <div class="info-linha">👤 <b>Responsável:</b> {responsavel}</div>
        <div class="btn-row">
            <a href="{link_maps}" target="_blank" class="btn-link bg-maps">📍 Maps</a>
            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">WhatsApp</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# LOGIN
# =========================
if not st.session_state.get("logado", False):
    st.markdown("<div class='titulo-grande'>🕊️ Guia Espírita</div>", unsafe_allow_html=True)
    with st.form("login"):
        st.text_input("E-mail")
        st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar", use_container_width=True):
            st.session_state["logado"] = True
            st.rerun()
else:
    @st.cache_data
    def carregar_dados():
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        return df

    df = carregar_dados()
    pagina = st.session_state.get("pagina")

    # =========================
    # MENU PRINCIPAL
    # =========================
    if pagina is None:
        st.markdown("<div class='titulo-grande'>🕊️ Guia Espírita</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔎 Busca Avançada", use_container_width=True):
                st.session_state["pagina"] = "pesquisar"
                st.rerun()
            if st.button("📍 Por Cidade", use_container_width=True):
                st.session_state["pagina"] = "cidade"
                st.rerun()
        with col2:
            if st.button("📊 Admin", use_container_width=True):
                st.session_state["pagina"] = "admin"
                st.rerun()
            if st.button("🕊️ Frases", use_container_width=True):
                st.session_state["pagina"] = "frases"
                st.rerun()
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear()
            st.cache_data.clear()
            st.rerun()

    # =========================
    # PÁGINAS INTERNAS
    # =========================
    else:

        # Função que mostra Voltar/Limpar lado a lado horizontal
        def botoes_lado_a_lado():
            col1, col2 = st.columns([1,1])
            with col1:
                if st.button("⬅️ VOLTAR"):
                    st.session_state["pagina"] = None
                    st.session_state["termo_pesquisa"] = ""
                    st.rerun()
            with col2:
                if st.button("🔄 LIMPAR"):
                    st.session_state["termo_pesquisa"] = ""
                    st.rerun()

        # =========================
        # BUSCA AVANÇADA
        if pagina == "pesquisar":
            botoes_lado_a_lado()
            termo = st.text_input("Digite pelo menos 3 letras:", key="termo_pesquisa", value=st.session_state["termo_pesquisa"])
            if termo and len(termo.strip()) >= 3:
                st.session_state["termo_pesquisa"] = termo
                termo_normal = normalize_text(termo.strip())
                resultado = df[df.apply(lambda row: termo_normal in normalize_text(" ".join(row.astype(str))), axis=1)]
                if not resultado.empty:
                    st.success(f"{len(resultado)} centro(s) encontrado(s)")
                    for i, (_, row) in enumerate(resultado.iterrows(),1):
                        renderizar_card(row,i)
                else:
                    st.warning("Nenhum resultado encontrado.")
            elif termo:
                st.warning("Digite pelo menos 3 letras.")

        # =========================
        # POR CIDADE
        elif pagina == "cidade":
            botoes_lado_a_lado()
            cidades = df["CIDADE DO CENTRO ESPIRITA"].dropna().value_counts().sort_index()
            lista_cidades = ["-- Selecione --"] + [f"{c} ({q})" for c,q in cidades.items()]
            escolha = st.selectbox("Selecione uma cidade:", lista_cidades)
            if escolha != "-- Selecione --":
                cidade_selecionada = escolha.split(" (")[0]
                resultado = df[df["CIDADE DO CENTRO ESPIRITA"]==cidade_selecionada]
                st.success(f"{len(resultado)} centro(s) encontrado(s)")
                for i, (_, row) in enumerate(resultado.iterrows(),1):
                    renderizar_card(row,i)

        # =========================
        # ADMIN
        elif pagina == "admin":
            st.metric("Total de Centros", len(df))
            st.metric("Cidades Únicas", df["CIDADE DO CENTRO ESPIRITA"].nunique())

        # =========================
        # FRASES
        elif pagina == "frases":
            st.markdown("""
            > Fora da caridade não há salvação. — Allan Kardec  
            > Amai-vos uns aos outros. — Jesus  
            > Ninguém é perfeito, mas todos podem melhorar. — Emmanuel  
            """)
