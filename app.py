import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS PREMIUM: MENU GRANDE, SOMBRA E NÚMERO DISCRETO ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { padding-top: 35px; }
    div[data-testid="stMarkdownContainer"] p { font-size: 20px !important; font-weight: 700 !important; color: #1E3A8A; }
    .stApp { background: #f4f7f9; }
    
    .card-centro { 
        background: white !important; padding: 25px; border-radius: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.15); 
        margin-bottom: 25px; border-left: 12px solid #0047AB;
        position: relative;
    }
    .numero-discreto {
        position: absolute; top: 15px; right: 20px;
        color: #BDC3C7; font-size: 14px; font-weight: 700;
    }
    .header-card { border-bottom: 2px solid #f0f2f6; padding-bottom: 12px; margin-bottom: 15px; }
    .tag-cidade { 
        background: #0047AB; color: white !important; padding: 4px 10px; 
        border-radius: 6px; font-weight: 800; font-size: 12px; text-transform: uppercase;
        margin-bottom: 8px; display: inline-block;
    }
    .nome-centro { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800; display: block; }
    .nome-fantasia { color: #3B82F6 !important; font-size: 16px !important; font-style: italic; font-weight: 500; margin-top: 2px; display: block; }
    .palestras-verde { 
        color: #065F46 !important; font-weight: 700; background: #D1FAE5; 
        padding: 10px; border-radius: 10px; margin: 12px 0; border: 1px solid #10B981;
    }
    .info-linha { margin: 8px 0; font-size: 15px; color: #333 !important; }
    .label-bold { font-weight: 800; color: #0047AB; }
    .btn-row { display: flex; gap: 12px; margin-top: 20px; }
    .btn-link { 
        text-decoration: none !important; color: white !important; 
        padding: 14px; border-radius: 12px; font-weight: 800; 
        text-align: center; flex: 1; display: inline-block;
    }
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
    
    # WHATSAPP: Limpeza de caracteres não numéricos
    whats_raw = str(row.get('CELULAR', ''))
    whats_num = re.sub(r'\D', '', whats_raw)
    link_wa = f"https://wa.me{whats_num}" if len(whats_num) >= 10 else "#"
    
    # MAPS: Encode para garantir que funcione no celular
    query_maps = urllib.parse.quote(f"{nome}, {end}, {cid}")
    link_maps = f"https://www.google.com{query_maps}"

    st.markdown(f"""
    <div class="card-centro">
        <div class="numero-discreto">#{index}</div>
        <div class="header-card">
            <span class="tag-cidade">🏙️ {cid}</span>
            <span class="nome-centro">{nome} 🕊️</span>
            {f'<span class="nome-fantasia">{fantasia}</span>' if fantasia else ''}
        </div>
        <div class="palestras-verde">🗣️ PALESTRAS: {palestras}</div>
        <div class="info-linha"><span class="label-bold">📍 ENDEREÇO:</span> {end}</div>
        <div class="info-linha"><span class="label-bold">👤 RESPONSÁVEL:</span> {resp}</div>
        <div class="btn-row">
            <a href="{link_maps}" target="_blank" class="btn-link bg-maps">📍 VER MAPA</a>
            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WHATSAPP</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- LOGIN E NAVEGAÇÃO ---
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

    try:
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"Erro ao ler guia.xlsx: {e}"); st.stop()

    if opcao == "🏠 Início":
        st.title("🕊️ Bem-vindo ao Guia Espírita")
        st.info("Abra o menu lateral para começar sua busca.")

    elif opcao == "🔎 Pesquisar Geral":
        st.subheader("Busca Inteligente")
        termo = st.text_input("Digite o nome, cidade ou qualquer palavra-chave:", key="busca_geral")
        
        if termo:
            # Lógica de busca corrigida: converte tudo para string antes de procurar
            termo_lower = termo.lower().strip()
            df_busca = df.fillna("").astype(str)
            mask = df_busca.apply(lambda x: x.str.contains(termo_lower, case=False, na=False)).any(axis=1)
            resultados = df[mask]
            
            if not resultados.empty:
                st.success(f"Encontramos {len(resultados)} centro(s):")
                for i, (_, row) in enumerate(resultados.iterrows(), 1):
                    renderizar_card(row, i)
            else:
                st.warning("Nenhum centro encontrado com esse termo.")

    elif opcao == "📍 Por Cidade":
        col_cid = 'CIDADE DO CENTRO ESPIRITA'
        cidades = sorted(df[col_cid].dropna().unique())
        sel = st.selectbox("Selecione a cidade:", ["-- Selecione --"] + cidades)
        
        if sel != "-- Selecione --":
            dados_cid = df[df[col_cid] == sel]
            for i, (_, row) in enumerate(dados_cid.iterrows(), 1):
                renderizar_card(row, i)
