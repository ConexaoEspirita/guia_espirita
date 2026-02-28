import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata

# 1. CONFIGURAÇÃO DA PÁGINA (Sempre o primeiro comando)
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
# CSS PARA REMOVER TUDO DO STREAMLIT
# =========================
st.markdown("""
    <style>
    /* Esconde o Menu, o Header e o Rodapé padrão */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Remove especificamente os ícones e selos do Streamlit Cloud embaixo */
    [data-testid="stStatusWidget"], 
    [data-testid="stToolbar"], 
    [data-testid="stDecoration"],
    .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_ {
        display: none !important;
    }

    /* Estilo do Fundo e Cards */
    .stApp { background: #f4f7f9; }
    .titulo-grande { font-size: 32px; font-weight: 800; margin-bottom: 8px; }
    
    .card-centro { 
        background: white;
        padding: 25px;
        border-radius: 20px; 
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.12); 
        border-left: 12px solid #0060D0;
        position: relative;
    }
    
    .btn-link { 
        text-decoration:none; 
        color:white !important; 
        padding:10px; 
        border-radius:10px; 
        font-weight:700; 
        text-align:center; 
        display:inline-block; 
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# FUNÇÕES DE APOIO
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
    <div class="card-centro">
        <div style="position:absolute; top:10px; right:15px; font-size:12px; color:#6B7280; background:rgba(255,255,255,0.8); padding:2px 6px; border-radius:12px; font-weight:500;">#{index}</div>
        <div style="color: #1E3A8A; font-size: 22px; font-weight: 800;">{nome} 🕊️</div>
        {"<div style='color: #3B82F6; font-style: italic;'>" + fantasia + "</div>" if fantasia else ""}
        <div style="color:#065F46; font-weight:700; background:#D1FAE5; padding:8px; border-radius:8px; margin:10px 0;">🗣️ PALESTRA: {palestra}</div>
        <div style="margin:5px 0;">👤 <b>Responsável:</b> {responsavel}</div>
        <div style="margin:5px 0;">🏙️ <b>Cidade:</b> {cidade}</div>
        <div style="margin:5px 0;">📍 <b>Endereço:</b> {endereco}</div>
        <div style="margin-top:15px; display:flex; gap:10px;">
            <a href="{link_maps}" target="_blank" class="btn-link" style="background:#4285F4;">📍 Maps</a>
            <a href="{link_wa}" target="_blank" class="btn-link" style="background:#25D366;">WhatsApp</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# LOGIN E NAVEGAÇÃO
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
        # Certifique-se que o arquivo chama guia.xlsx no seu GitHub
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        return df

    try:
        df = carregar_dados()
    except:
        st.error("Erro ao carregar guia.xlsx. Verifique o nome do arquivo no GitHub.")
        st.stop()

    pagina = st.session_state.get("pagina")

    if pagina is None:
        st.markdown("<div class='titulo-grande'>🕊️ Guia Espírita</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔎 Busca Avançada", use_container_width=True): st.session_state["pagina"] = "pesquisar"; st.rerun()
            if st.button("📍 Por Cidade", use_container_width=True): st.session_state["pagina"] = "cidade"; st.rerun()
        with c2:
            if st.button("📊 Admin", use_container_width=True): st.session_state["pagina"] = "admin"; st.rerun()
            if st.button("🕊️ Frases", use_container_width=True): st.session_state["pagina"] = "frases"; st.rerun()
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear(); st.cache_data.clear(); st.rerun()

    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ VOLTAR", use_container_width=True): st.session_state["pagina"] = None; st.rerun()
        with col2:
            if st.button("🔄 LIMPAR", use_container_width=True): st.session_state["termo_pesquisa"] = ""; st.rerun()

        if pagina == "pesquisar":
            termo = st.text_input("Digite o que busca:", value=st.session_state["termo_pesquisa"])
            if termo and len(termo.strip()) >= 3:
                st.session_state["termo_pesquisa"] = termo
                t_norm = normalize_text(termo.strip())
                res = df[df.apply(lambda r: t_norm in normalize_text(" ".join(r.astype(str))), axis=1)]
                if not res.empty:
                    st.success(f"{len(res)} centro(s) encontrado(s)")
                    for i, (_, row) in enumerate(res.iterrows(), 1): renderizar_card(row, i)
                else:
                    st.warning("Nada encontrado.")

        elif pagina == "cidade":
            cidades_com_contagem = []
            for cidade in sorted(df["CIDADE DO CENTRO ESPIRITA"].dropna().unique()):
                qtd = len(df[df["CIDADE DO CENTRO ESPIRITA"] == cidade])
                cidades_com_contagem.append(f"{cidade} ({qtd})")
            
            escolha = st.selectbox("Selecione uma cidade:", ["-- Selecione --"] + cidades_com_contagem)
            if escolha != "-- Selecione --":
                cidade_real = escolha.split(" (")[0]  # Remove "(2)" e pega só "Bady Bassit"
                res = df[df["CIDADE DO CENTRO ESPIRITA"] == cidade_real]
                for i, (_, row) in enumerate(res.iterrows(), 1): renderizar_card(row, i)

        elif pagina == "admin":
            st.metric("Total de Centros", len(df))
            st.metric("Cidades Únicas", df["CIDADE DO CENTRO ESPIRITA"].nunique())

        elif pagina == "frases":
            st.info("Fora da caridade não há salvação. — Allan Kardec")
