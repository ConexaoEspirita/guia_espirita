import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Guia Espírita", layout="wide")

# =========================
# SESSION STATE
# =========================
if "pagina" not in st.session_state:
    st.session_state["pagina"] = None
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# =========================
# CSS PROFISSIONAL
# =========================
st.markdown("""
<style>
.titulo-profissional {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 15px;
}

.card-centro { 
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.numero-badge { 
    position: absolute;
    top: 15px;
    right: 20px;
    background: #f0f4f8;
    color: #7f8c8d;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 800;
}

.nome-centro {
    color: #1E3A8A;
    font-size: 20px;
    font-weight: 700;
}

.nome-fantasia {
    color: #3B82F6;
    font-style: italic;
    font-size: 16px;
}

.palestras-verde {
    color: #065F46;
    font-weight: 700;
    background: #D1FAE5;
    padding: 10px;
    border-radius: 10px;
    margin: 10px 0;
    border: 1px solid #10B981;
}

.info-linha { margin: 6px 0; }

.btn-row { display:flex; gap:10px; margin-top:10px; }

.btn-link {
    text-decoration:none;
    color:white;
    padding:10px;
    border-radius:8px;
    font-weight:700;
    text-align:center;
    flex:1;
}

.bg-wa { background:#25D366; }
.bg-maps { background:#4285F4; }
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÃO CARD
# =========================
def ajustar(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def renderizar_card(row, index):
    nome = ajustar(row.get('NOME', 'Centro Espírita'))
    fantasia = ajustar(row.get('NOME FANTASIA'))
    endereco = ajustar(row.get('ENDERECO'))
    cidade = ajustar(row.get('CIDADE DO CENTRO ESPIRITA'))
    palestra = ajustar(row.get('PALESTRA PUBLICA'))
    responsavel = ajustar(row.get('RESPONSAVEL'))

    # WhatsApp
    numero = "".join(filter(str.isdigit, str(row.get('CELULAR'))))
    link_wa = f"https://wa.me/+55{numero}" if len(numero) >= 10 else "#"

    # Google Maps
    query = urllib.parse.quote(f"{endereco}, {cidade}")
    link_maps = f"https://www.google.com/maps/search/?api=1&query={query}"

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
            <a href="{link_maps}" target="_blank" class="btn-link bg-maps">📍 Ver Mapa</a>
            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WhatsApp</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# LOGIN SIMPLES
# =========================
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
    def carregar_dados():
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        return df

    df = carregar_dados()
    pagina = st.session_state["pagina"]

    # =========================
    # MENU PRINCIPAL
    # =========================
    if pagina is None:
        st.markdown("<div class='titulo-profissional'>🕊️ Guia Espírita</div>", unsafe_allow_html=True)

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

    # =========================
    # PÁGINAS INTERNAS
    # =========================
    else:

        col1, col2 = st.columns([10,1])
        with col1:
            titulos = {
                "pesquisar": "🔎 Busca Avançada",
                "cidade": "📍 Localizar por Cidade",
                "admin": "📊 Painel Administrativo",
                "frases": "🕊️ Mensagens Espíritas"
            }
            st.markdown(f"<div class='titulo-profissional'>{titulos[pagina]}</div>", unsafe_allow_html=True)
        with col2:
            if st.button("⬅️"):
                st.session_state["pagina"] = None
                st.rerun()

        st.divider()

        # =========================
        # BUSCA AVANÇADA
        # =========================
        if pagina == "pesquisar":
            termo = st.text_input("Digite pelo menos 3 letras:")
            if termo and len(termo.strip()) >= 3:
                termo = termo.strip().lower()
                resultado = df[df.apply(lambda row: termo in " ".join(row.astype(str)).lower(), axis=1)]
                if not resultado.empty:
                    st.success(f"{len(resultado)} centro(s) encontrado(s)")
                    for i, (_, row) in enumerate(resultado.iterrows(), 1):
                        renderizar_card(row, i)
                else:
                    st.warning("Nenhum resultado encontrado.")
            elif termo:
                st.warning("Digite pelo menos 3 letras.")

        # =========================
        # CIDADES COM CONTAGEM
        # =========================
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

        # =========================
        # ADMIN
        # =========================
        elif pagina == "admin":
            st.metric("Total de Centros", len(df))
            st.metric("Cidades Únicas", df["CIDADE DO CENTRO ESPIRITA"].nunique())

        # =========================
        # FRASES ESPÍRITAS
        # =========================
        elif pagina == "frases":
            st.markdown("""
            > Fora da caridade não há salvação. — Allan Kardec  
            > Amai-vos uns aos outros. — Jesus  
            > Ninguém é perfeito, mas todos podem melhorar. — Emmanuel  
            """)
