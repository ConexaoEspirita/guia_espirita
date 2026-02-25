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
    .stTextInput input { border-radius: 12px !important; border: 2px solid #D4E8F7 !important; padding: 10px 15px !important; }
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
    
    # WhatsApp (Lógica Consertada +55)
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    link_wa = f"https://wa.me{whats_num}" if len(whats_num) >= 10 else "#"
    
    # Maps (Lógica Consertada Quote)
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
    with st.form("login"):
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

    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()

    if opcao == "🏠 Início":
        st.title("🕊️ Bem-vindo")
        st.info("Abra o menu lateral para pesquisar.")

    elif opcao == "🔎 Pesquisar Geral":
        termo = st.text_input("Busca por nome, cidade ou palavra-chave:", placeholder="Ex: Kardec")
        if termo:
            # --- ✅ LÓGICA DE SUPER BUSCA FLEXÍVEL ---
            def normalizar_texto(texto):
                if pd.isna(texto): return ""
                texto = str(texto).lower()
                return (texto.replace('ç','c').replace('ã','a').replace('õ','o')
                       .replace('á','a').replace('é','e').replace('í','i')
                       .replace('ó','o').replace('ú','u').replace('â','a')
                       .replace('ê','e').replace('ô','o').replace('û','u'))
            
            def busca_super_flexivel(texto_celula):
                texto_norm = normalizar_texto(texto_celula)
                termo_norm = normalizar_texto(termo)
                if not texto_norm or not termo_norm: return False
                # Batida direta, Sequência de letras ou 70% de similaridade
                if termo_norm in texto_norm: return True
                if all(letra in texto_norm for letra in termo_norm): return True
                if sum(1 for letra in termo_norm if letra in texto_norm) / len(termo_norm) > 0.7: return True
                return False

            mask = df.apply(lambda row: row.astype(str).apply(busca_super_flexivel).any(), axis=1)
            resultados = df[mask]
            
            st.write(f"Encontrados **{len(resultados)}** resultados:")
            for i, (_, row) in enumerate(resultados.iterrows(), 1):
                renderizar_card(row, i)

    elif opcao == "📍 Por Cidade":
        cidades = sorted(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique())
        sel = st.selectbox("Selecione a cidade:", ["-- Selecione --"] + cidades)
        if sel != "-- Selecione --":
            dados = df[df['CIDADE DO CENTRO ESPIRITA'] == sel]
            for i, (_, row) in enumerate(dados.iterrows(), 1):
                renderizar_card(row, i)
