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

# =========================
# CSS NUCLEAR - ESMAGA STREAMLIT
# =========================
st.markdown("""
<style>
/* HACK DEFINITIVO - DESATIVA HEADER DO STREAMLIT */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.st-emotion-cache-1r6h1kh {display: none !important;}
.st-emotion-cache-1e90bb7 {display: none !important;}

/* BOTÃO FLUTUANTE INVENCÍVEL */
.botao-fluatante {
    all: initial !important;
    position: fixed !important;
    top: 12px !important;
    right: 12px !important;
    z-index: 2147483647 !important; /* MÁXIMO POSSÍVEL */
    width: 56px !important;
    height: 56px !important;
    background: #25D366 !important;
    color: white !important;
    border: 3px solid white !important;
    border-radius: 50% !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.5) !important;
    cursor: pointer !important;
    font-size: 26px !important;
    font-weight: bold !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8) !important;
    line-height: 1 !important;
    padding: 0 !important;
    margin: 0 !important;
}
.botao-fluatante:hover {
    background: #128C7E !important;
    transform: scale(1.15) !important;
    box-shadow: 0 12px 35px rgba(0,0,0,0.7) !important;
}

/* RESTO DO CSS */
.stApp { background: #f4f7f9; }
.titulo-grande { font-size: 32px; font-weight: 800; margin-bottom: 8px; }
.card-centro { 
    background: white; padding: 25px; border-radius: 20px; 
    margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.12); 
    border-left: 12px solid #0060D0; position: relative;
}
.numero-badge { 
    position: absolute; top: 12px; right: 15px; background: #f0f4f8;
    color: #7f8c8d; padding: 3px 10px; border-radius: 20px;
    font-size: 13px; font-weight: 700;
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
# BOTÃO INVENCÍVEL - PRIMEIRA TENTATIVA
# =========================
st.markdown("""
<div style='position:fixed;top:12px;right:12px;z-index:2147483647'>
<button class="botao-fluatante" onclick="if(confirm('🏠 Voltar ao menu?')){window.location.href='?'}">
🏠
</button>
</div>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES (igual)
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
# LOGIN E RESTO (igual)
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

    else:
        if pagina == "pesquisar":
            termo = st.text_input("Digite pelo menos 3 letras:")
            if termo and len(termo.strip()) >= 3:
                termo_normal = normalize_text(termo.strip())
                resultado = df[df.apply(lambda row: termo_normal in normalize_text(" ".join(row.astype(str))), axis=1)]
                if not resultado.empty:
                    st.success(f"{len(resultado)} centro(s) encontrado(s)")
                    for i, (_, row) in enumerate(resultado.iterrows(),1):
                        renderizar_card(row,i)
                    if len(resultado) >= 5:
                        if st.button("⬅️ Voltar"):
                            st.session_state.pagina = None
                            st.rerun()
                else:
                    st.warning("Nenhum resultado encontrado.")
            elif termo:
                st.warning("Digite pelo menos 3 letras.")

        elif pagina == "cidade":
            cidades = df["CIDADE DO CENTRO ESPIRITA"].dropna().value_counts().sort_index()
            lista_cidades = ["-- Selecione --"] + [f"{c} ({q})" for c,q in cidades.items()]
            escolha = st.selectbox("Selecione uma cidade:", lista_cidades)
            if escolha != "-- Selecione --":
                cidade_selecionada = escolha.split(" (")[0]
                resultado = df[df["CIDADE DO CENTRO ESPIRITA"]==cidade_selecionada]
                st.success(f"{len(resultado)} centro(s) encontrado(s)")
                for i, (_, row) in enumerate(resultado.iterrows(),1):
                    renderizar_card(row,i)
                if len(resultado) >= 5:
                    if st.button("⬅️ Voltar"):
                        st.session_state.pagina = None
                        st.rerun()

        elif pagina == "admin":
            st.metric("Total de Centros", len(df))
            st.metric("Cidades Únicas", df["CIDADE DO CENTRO ESPIRITA"].nunique())

        elif pagina == "frases":
            st.markdown("""
            > Fora da caridade não há salvação. — Allan Kardec  
            > Amai-vos uns aos outros. — Jesus  
            > Ninguém é perfeito, mas todos podem melhorar. — Emmanuel  
            """)
