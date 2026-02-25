import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS PROFISSIONAL: MENU, BUSCA E CARDS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { padding-top: 35px; }
    div[data-testid="stMarkdownContainer"] p { font-size: 20px !important; font-weight: 700 !important; color: #1E3A8A; }
    .stTextInput input { border-radius: 12px !important; border: 2px solid #D4E8F7 !important; padding: 12px !important; }
    .stApp { background: #f4f7f9; }
    .card-centro { 
        background: white !important; padding: 25px; border-radius: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.12); 
        margin-bottom: 25px; border-left: 12px solid #0047AB; position: relative;
    }
    .numero-badge { position: absolute; top: 15px; right: 20px; background: #f0f4f8; color: #7f8c8d; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 800; }
    .nome-centro { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800; display: block; }
    .nome-fantasia { color: #3B82F6 !important; font-size: 16px !important; font-style: italic; font-weight: 500; margin-top: 2px; display: block; }
    .palestras-verde { color: #065F46 !important; font-weight: 700; background: #D1FAE5; padding: 10px; border-radius: 10px; margin: 12px 0; border: 1px solid #10B981; }
    .info-linha { margin: 8px 0; font-size: 15px; color: #333 !important; }
    .label-bold { font-weight: 800; color: #0047AB; text-transform: uppercase; font-size: 13px; }
    .btn-row { display: flex; gap: 12px; margin-top: 20px; }
    .btn-link { text-decoration: none !important; color: white !important; padding: 14px; border-radius: 12px; font-weight: 800; text-align: center; flex: 1; display: inline-block; }
    .bg-wa { background-color: #25D366; }
    .bg-maps { background-color: #4285F4; }
</style>
""", unsafe_allow_html=True)

def ajustar_texto(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def renderizar_card(row, index):
    nome = ajustar_texto(row.get('NOME', 'Centro Espírita'))
    fantasia = ajustar_texto(row.get('NOME FANTASIA', ''))
    end = ajustar_texto(row.get('ENDERECO', ''))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', ''))
    palestras = ajustar_texto(row.get('PALESTRA PUBLICA', 'Consulte'))
    resp = ajustar_texto(row.get('RESPONSAVEL', 'N/I'))
    
    # WhatsApp CONSERTADO (Lógica Blindada +55)
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    if len(whats_num) >= 10:
        whats_num = "+55" + whats_num
        link_wa = f"https://wa.me{whats_num}"
    else: link_wa = "#"
    
    # Maps CONSERTADO (Lógica urllib quote)
    query_maps = urllib.parse.quote(f"{nome}, {end}, {cid}")
    link_maps = f"https://www.google.com{query_maps}"

    st.markdown(f"""
    <div class="card-centro">
        <div class="numero-badge">#{index}</div>
        <div style="border-bottom: 2px solid #f0f2f6; padding-bottom: 12px; margin-bottom: 15px;">
            <span class="nome-centro">{nome} 🕊️</span>
            {f'<span class="nome-fantasia">{fantasia}</span>' if fantasia else ''}
        </div>
        <div class="palestras-verde">🗣️ PALESTRAS: {palestras}</div>
        <div class="info-linha"><span class="label-bold">🏙️ Cidade:</span> {cid}</div>
        <div class="info-linha"><span class="label-bold">📍 Endereço:</span> {end}</div>
        <div class="info-linha"><span class="label-bold">👤 Responsável:</span> {resp}</div>
        <div class="btn-row">
            <a href="{link_maps}" target="_blank" class="btn-link bg-maps">📍 VER MAPA</a>
            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WHATSAPP</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- SISTEMA ---
if "logado" not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🕊️ Guia Espírita")
    with st.form("login_guia"):
        u = st.text_input("E-mail")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR"):
            st.session_state.logado = True
            st.rerun()
else:
    with st.sidebar:
        st.markdown("### ☰ MENU")
        opcao = st.radio("Escolha:", ["🏠 Início", "🔎 Pesquisar Geral", "📍 Por Cidade", "🚪 Sair"])
        if opcao == "🚪 Sair":
            st.session_state.logado = False
            st.rerun()

    # Carregamento dos dados
    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()

    if opcao == "🏠 Início":
        st.title("🕊️ Bem-vindo ao Guia")
        st.info("Abra o menu lateral para pesquisar centros espíritas.")

    elif opcao == "🔎 Pesquisar Geral":
        termo = st.text_input("🔍 Digite pelo menos 4 letras para buscar:")
        if termo and len(termo) >= 4:
            palavras_busca = termo.lower().split()
            
            def normalizar_texto(texto):
                if pd.isna(texto): return ""
                texto = str(texto).lower()
                return (texto.replace('ç','c').replace('ã','a').replace('õ','o')
                       .replace('á','a').replace('é','e').replace('í','i')
                       .replace('ó','o').replace('ú','u').replace('â','a')
                       .replace('ê','e').replace('ô','o').replace('û','u'))
            
            def busca_multiplas_palavras(texto_celula):
                texto_norm = normalizar_texto(texto_celula)
                if not texto_norm: return False
                # Deve achar TODAS as palavras da busca na célula
                for palavra in palavras_busca:
                    if normalizar_texto(palavra) not in texto_norm:
                        return False
                return True

            mask = df.apply(lambda row: row.astype(str).apply(busca_multiplas_palavras).any(), axis=1)
            resultados = df[mask]
            
            if len(resultados) == 0:
                st.warning("❌ Nenhum resultado encontrado. Tente outra combinação!")
            else:
                st.success(f"✅ Encontrados {len(resultados)} centro(s)")
                for i, (_, row) in enumerate(resultados.iterrows(), 1):
                    renderizar_card(row, i)
        elif termo:
            st.warning("⚠️ Digite pelo menos 4 letras para buscar!")

    elif opcao == "📍 Por Cidade":
        cidades = sorted(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique())
        sel = st.selectbox("Selecione a cidade:", ["-- Selecione --"] + cidades)
        if sel != "-- Selecione --":
            dados_cid = df[df['CIDADE DO CENTRO ESPIRITA'] == sel]
            for i, (_, row) in enumerate(dados_cid.iterrows(), 1):
                renderizar_card(row, i)
