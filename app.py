import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- SEU DESIGN PREMIUM MANTIDO ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { padding-top: 20px; }
    div[data-testid="stSidebar"] .st-emotion-cache-167909c { font-size: 1.2rem !important; font-weight: 600 !important; }
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
    
    # WhatsApp ✅ CONSERTADO
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    if len(whats_num) >= 10:
        whats_num_com_prefixo = "+55" + whats_num
        link_wa = f"https://wa.me/{whats_num_com_prefixo}"
    else:
        link_wa = "#"
    
    # Maps ✅ CONSERTADO
    endereco_completo = f"{nome} {end}, {cid}, São Paulo, Brasil"
query_maps = urllib.parse.quote(endereco_completo)


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

# --- LOGIN / NAVEGAÇÃO ---
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
        # SEU MENU PREMIUM MANTIDO
        st.markdown("""
        <div style='padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 20px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);'>
            <div style='text-align: center; color: white;'>
                <h2 style='margin: 0; font-size: 22px; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>
                    🕊️ GUIA ESPÍRITA
                </h2>
                <p style='margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;'>Encontre centros próximos</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        opcao = st.radio("Navegação:", ["🏠 Início", "🔎 Pesquisar Geral", "📍 Por Cidade", "🚪 Sair"], label_visibility="collapsed")
        
        if opcao == "🚪 Sair":
            st.session_state.logado = False
            st.cache_data.clear()
            st.rerun()

    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()

    if opcao == "🏠 Início":
        st.title("🕊️ Bem-vindo ao Guia")
        st.info("Utilize o menu lateral para iniciar sua busca.")

    elif opcao == "🔎 Pesquisar Geral":
        termo = st.text_input("🔍 Digite pelo menos 4 letras para buscar:")
        if termo and len(termo) >= 4:
            palavras_busca = termo.lower().split()
            
            def normalizar(t):
                if pd.isna(t): return ""
                t = str(t).lower()
                return (t.replace('ç','c').replace('ã','a').replace('õ','o').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u'))
            
            def checar_linha(row):
                texto_linha = normalizar(" ".join(row.astype(str)))
                return all(normalizar(p) in texto_linha for p in palavras_busca)

            mask = df.apply(checar_linha, axis=1)
            res = df[mask]
            
            if len(res) > 0:
                st.success(f"✅ Encontrados {len(res)} centro(s)")
                for i, (_, row) in enumerate(res.iterrows(), 1):
                    renderizar_card(row, i)
            else: st.warning("❌ Nenhum resultado.")
        elif termo: st.warning("⚠️ Mínimo de 4 letras!")

    elif opcao == "📍 Por Cidade":
        cidades = sorted(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique())
        sel = st.selectbox("Selecione a cidade:", ["-- Selecione --"] + cidades)
        if sel != "-- Selecione --":
            for i, (_, row) in enumerate(df[df['CIDADE DO CENTRO ESPIRITA'] == sel].iterrows(), 1):
                renderizar_card(row, i)


