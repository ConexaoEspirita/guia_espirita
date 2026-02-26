import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# -------- CONTROLE DE PÁGINA (resolve botão voltar) --------
if "page" in st.query_params:
    pagina = st.query_params["page"]
else:
    pagina = "🏠 Início"

# -------- CSS --------
st.markdown("""
<style>
    .stApp { background: #f4f7f9; }

    .card-centro { 
        background: white; 
        padding: 25px; 
        border-radius: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.12); 
        margin-bottom: 25px; 
        border-left: 10px solid #1E3A8A;
    }

    .nome-centro {
        font-size: 22px;
        font-weight: 800;
        color: #1E3A8A;
    }

    .nome-fantasia {
        font-size: 15px;
        font-style: italic;
        color: #3B82F6;
    }

    .palestras-verde {
        background: #D1FAE5;
        padding: 10px;
        border-radius: 10px;
        margin: 12px 0;
        font-weight: 600;
        color: #065F46;
    }

    .btn-row {
        display: flex;
        gap: 12px;
        margin-top: 15px;
    }

    .btn-link {
        text-decoration: none;
        color: white;
        padding: 12px;
        border-radius: 10px;
        font-weight: 700;
        text-align: center;
        flex: 1;
        display: inline-block;
    }

    .bg-wa { background-color: #25D366; }
    .bg-maps { background-color: #4285F4; }
</style>
""", unsafe_allow_html=True)

# -------- SIDEBAR --------
with st.sidebar:
    st.markdown("## 🕊️ Guia Espírita")

    paginas = ["🏠 Início", "🔎 Pesquisar Geral", "📍 Por Cidade", "📊 Admin", "🕊️ Frases"]

    pagina = st.radio("Navegação", paginas, index=paginas.index(pagina))

st.query_params["page"] = pagina
st.divider()

# -------- CARREGAR DADOS --------
df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
df.columns = df.columns.str.strip()

# -------- FUNÇÃO LIMPAR TEXTO (resolve AMEL / acentos) --------
def limpar_texto(txt):
    if pd.isna(txt):
        return ""
    txt = str(txt).strip().lower()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    return txt

# -------- FUNÇÃO CARD --------
def renderizar_card(row):
    nome = str(row.get('NOME', 'Centro Espírita')).strip()
    fantasia = str(row.get('NOME FANTASIA', '')).strip()
    end = str(row.get('ENDERECO', '')).strip()
    cid = str(row.get('CIDADE DO CENTRO ESPIRITA', '')).strip()
    palestras = str(row.get('PALESTRA PUBLICA', 'Consulte')).strip()
    resp = str(row.get('RESPONSAVEL', 'N/I')).strip()

    # WhatsApp
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    if len(whats_num) >= 10:
        link_wa = f"https://wa.me/55{whats_num}?text=Olá,%20vim%20pelo%20Guia%20Espírita"
    else:
        link_wa = "#"

    # MAPS COM GRAMPO (PIN)
    endereco_completo = f"{end}, {cid}"
    link_maps = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(endereco_completo)}"

    st.markdown(f"""
    <div class="card-centro">
        <div class="nome-centro">{nome} 🕊️</div>
        {f'<div class="nome-fantasia">{fantasia}</div>' if fantasia else ''}
        <div class="palestras-verde">🗣️ PALESTRAS: {palestras}</div>
        <div><b>🏙️ Cidade:</b> {cid}</div>
        <div><b>📍 Endereço:</b> {end}</div>
        <div><b>👤 Responsável:</b> {resp}</div>
        <div class="btn-row">
            <a href="{link_maps}" target="_blank" class="btn-link bg-maps">📍 VER MAPA</a>
            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WHATSAPP</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------- PÁGINAS --------

if pagina == "🏠 Início":
    st.info("👈 Utilize o menu lateral para navegar.")

elif pagina == "🔎 Pesquisar Geral":
    st.header("🔎 Pesquisar Geral")

    termo = st.text_input("Digite pelo menos 4 letras para buscar:")

    if termo and len(termo) >= 4:
        termo_limpo = limpar_texto(termo)

        mask = df.apply(
            lambda row: termo_limpo in limpar_texto(" ".join(row.astype(str))),
            axis=1
        )

        res = df[mask]

        if len(res) > 0:
            st.success(f"✅ Encontrados {len(res)} centro(s)")
            for _, row in res.iterrows():
                renderizar_card(row)
        else:
            st.warning("❌ Nenhum resultado encontrado.")

    elif termo:
        st.warning("⚠️ Digite pelo menos 4 letras.")

elif pagina == "📍 Por Cidade":
    st.header("📍 Buscar por Cidade")

    cidades = sorted(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique())

    sel = st.selectbox("Selecione a cidade:", ["-- Selecione --"] + cidades)

    if sel != "-- Selecione --":
        res = df[df['CIDADE DO CENTRO ESPIRITA'] == sel]
        st.success(f"✅ Encontrados {len(res)} centro(s) em {sel}")
        for _, row in res.iterrows():
            renderizar_card(row)

elif pagina == "📊 Admin":
    st.header("📊 Painel Administrativo")
    st.metric("🏠 Total Centros", len(df))
    st.metric("📍 Cidades Únicas", len(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique()))

elif pagina == "🕊️ Frases":
    st.header("🕊️ Frases Espíritas")
    st.markdown("> Fora da caridade não há salvação. — Allan Kardec")
