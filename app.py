import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# ==============================
# CSS PROFISSIONAL
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
    background: white !important;
    padding: 25px;
    border-radius: 20px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.12); 
    margin-bottom: 25px;
    border-left: 12px solid #0047AB;
    position: relative;
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
    font-weight: 800;
}

.palestras-verde {
    color: #065F46;
    font-weight: 700;
    background: #D1FAE5;
    padding: 10px;
    border-radius: 10px;
    margin: 12px 0;
    border: 1px solid #10B981;
}

.btn-row { display:flex; gap:10px; margin-top:15px; }

.btn-link {
    text-decoration:none;
    color:white;
    padding:12px;
    border-radius:10px;
    font-weight:700;
    text-align:center;
    flex:1;
}

.bg-wa { background:#25D366; }
.bg-maps { background:#4285F4; }
</style>
""", unsafe_allow_html=True)

# ==============================
# FUNÇÕES
# ==============================
def ajustar_texto(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def renderizar_card(row, index):
    nome = ajustar_texto(row.get('NOME', 'Centro Espírita'))
    end = ajustar_texto(row.get('ENDERECO', ''))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', ''))
    palestras = ajustar_texto(row.get('PALESTRA PUBLICA', 'Consulte'))

    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    link_wa = f"https://wa.me/+55{whats_num}" if len(whats_num) >= 10 else "#"

    query_maps = urllib.parse.quote(f"{end}, {cid}")
    link_maps = f"https://www.google.com/maps/search/?api=1&query={query_maps}"

    st.markdown(f"""
    <div class="card-centro">
        <div class="numero-badge">#{index}</div>
        <div class="nome-centro">{nome} 🕊️</div>
        <div class="palestras-verde">🗣️ PALESTRAS: {palestras}</div>
        <div>🏙️ {cid}</div>
        <div>📍 {end}</div>
        <div class="btn-row">
            <a href="{link_maps}" target="_blank" class="btn-link bg-maps">📍 Ver Mapa</a>
            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WhatsApp</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# SESSION STATE
# ==============================
if "pagina" not in st.session_state:
    st.session_state.pagina = None

if "logado" not in st.session_state:
    st.session_state.logado = False

# ==============================
# LOGIN
# ==============================
if not st.session_state.logado:
    st.title("🕊️ Guia Espírita")

    with st.form("login"):
        st.text_input("E-mail")
        st.text_input("Senha", type="password")

        if st.form_submit_button("Entrar", use_container_width=True):
            st.session_state.logado = True
            st.rerun()

else:

    @st.cache_data
    def carregar_dados():
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        return df

    df = carregar_dados()

    pagina = st.session_state.pagina

    # ==============================
    # MENU PRINCIPAL LIMPO
    # ==============================
    if pagina is None:

        st.markdown("<div class='titulo-profissional'>🕊️ Guia Espírita</div>", unsafe_allow_html=True)
        st.write("")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔎 Busca Avançada", use_container_width=True):
                st.session_state.pagina = "pesquisar"
                st.rerun()

            if st.button("📍 Localizar por Cidade", use_container_width=True):
                st.session_state.pagina = "cidade"
                st.rerun()

        with col2:
            if st.button("📊 Painel Administrativo", use_container_width=True):
                st.session_state.pagina = "admin"
                st.rerun()

            if st.button("🕊️ Mensagens Espíritas", use_container_width=True):
                st.session_state.pagina = "frases"
                st.rerun()

        if st.button("🚪 Sair", use_container_width=True):
            st.session_state = {"logado": False}
            st.cache_data.clear()
            st.rerun()

    # ==============================
    # PÁGINAS INTERNAS
    # ==============================
    else:

        col1, col2 = st.columns([1, 10])

        with col1:
            if st.button("⬅️"):
                st.session_state.pagina = None
                st.rerun()

        with col2:
            titulos = {
                "pesquisar": "🔎 Busca Avançada",
                "cidade": "📍 Localizar por Cidade",
                "admin": "📊 Painel Administrativo",
                "frases": "🕊️ Mensagens Espíritas"
            }

            st.markdown(f"<div class='titulo-profissional'>{titulos[pagina]}</div>", unsafe_allow_html=True)
            st.write("")

        # ------------------
        # BUSCA
        # ------------------
        if pagina == "pesquisar":

            termo = st.text_input("Digite pelo menos 3 letras:")

            if termo and len(termo) >= 3:

                palavras = termo.lower().split()

                def normalizar(t):
                    return "" if pd.isna(t) else str(t).lower()

                def checar(row):
                    texto = " ".join([normalizar(row[col]) for col in df.columns])
                    return any(p in texto for p in palavras)

                res = df[df.apply(checar, axis=1)]

                if len(res) > 0:
                    st.success(f"{len(res)} centro(s) encontrado(s)")
                    for i, (_, row) in enumerate(res.iterrows(), 1):
                        renderizar_card(row, i)
                else:
                    st.warning("Nenhum resultado encontrado.")

        # ------------------
        # CIDADE (AGORA ABRE LIMPA)
        # ------------------
        elif pagina == "cidade":

            cidades = sorted(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique())

            sel = st.selectbox(
                "Selecione uma cidade:",
                ["-- Selecione --"] + list(cidades)
            )

            if sel != "-- Selecione --":

                res = df[df['CIDADE DO CENTRO ESPIRITA'] == sel]

                st.success(f"{len(res)} centro(s) encontrado(s) em {sel}")

                for i, (_, row) in enumerate(res.iterrows(), 1):
                    renderizar_card(row, i)

        # ------------------
        # ADMIN
        # ------------------
        elif pagina == "admin":

            col1, col2 = st.columns(2)
            col1.metric("Total de Centros", len(df))
            col2.metric("Cidades Únicas", len(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique()))

        # ------------------
        # FRASES
        # ------------------
        elif pagina == "frases":

            st.markdown("""
            > Fora da caridade não há salvação. — Allan Kardec  
            > Amai-vos uns aos outros. — Jesus  
            > Ninguém é perfeito, mas todos podem melhorar. — Emmanuel  
            """)
