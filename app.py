import streamlit as st
import pandas as pd
import urllib.parse
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Guia Espírita", 
    page_icon="🕊️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS COMPLETO (PROTEÇÃO MOBILE + LOGIN VISÍVEL) ---
st.markdown("""
<style>
header[data-testid="stHeader"], [data-testid="stSidebar"] {
    display: none !important;
}
.block-container { padding-top: 1rem !important; }
* { -webkit-touch-callout: none !important; }

.stApp { 
    background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%) !important; 
}

.card-centro { 
    background: white !important; padding: 25px; border-radius: 20px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.12); 
    margin-bottom: 25px; border-left: 12px solid #0047AB; position: relative;
}
.numero-badge { 
    position: absolute; top: 15px; right: 20px; background: #f0f4f8; 
    color: #7f8c8d; padding: 2px 10px; border-radius: 20px; 
    font-size: 12px; font-weight: 800; 
}
.nome-centro { 
    color: #1E3A8A !important; font-size: 22px !important; 
    font-weight: 800; display: block; 
}
.nome-fantasia { 
    color: #3B82F6 !important; font-size: 16px !important; 
    font-style: italic; font-weight: 500; margin-top: 2px; display: block; 
}
.palestras-verde { 
    color: #065F46 !important; font-weight: 700; 
    background: #D1FAE5; padding: 10px; border-radius: 10px; 
    margin: 12px 0; border: 1px solid #10B981; 
}
.info-linha { margin: 8px 0; font-size: 15px; color: #333 !important; }
.label-bold { font-weight: 800; color: #0047AB; text-transform: uppercase; font-size: 13px; }
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

# --- FUNÇÕES AUXILIARES ---
def ajustar_texto(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def remover_acentos(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower()
    return re.sub(r'[àáâãäå]', 'a', re.sub(r'[èéêë]', 'e', re.sub(r'[ìíîï]', 'i', re.sub(r'[òóôõö]', 'o', re.sub(r'[ùúûü]', 'u', texto)))))

def criar_link_maps(row):
    nome_google = ajustar_texto(row.get('NOME_GOOGLE_MAPS', ''))
    end = ajustar_texto(row.get('ENDERECO', ''))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', ''))
    if nome_google and len(nome_google) > 5:
        return f"https://www.google.com{urllib.parse.quote(nome_google)}"
    if end and cid:
        query = f"{end}, {cid}, SP"
        return f"https://www.google.com{urllib.parse.quote(query)}"
    return f"https://www.google.com{urllib.parse.quote(cid or 'São Paulo')}"

def renderizar_card(row, index):
    nome = ajustar_texto(row.get('NOME', 'Centro Espírita'))
    fantasia = ajustar_texto(row.get('NOME FANTASIA', ''))
    end = ajustar_texto(row.get('ENDERECO', ''))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', ''))
    palestras = ajustar_texto(row.get('PALESTRA PUBLICA', 'Consulte'))
    resp = ajustar_texto(row.get('RESPONSAVEL', 'N/I'))
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    link_wa = f"https://wa.me{whats_num}" if len(whats_num) >= 10 else "#"
    link_maps = criar_link_maps(row)

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
            <a href="{link_maps}" target="_blank" class="btn-link bg-maps">📍 MAPA</a>
            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WhatsApp</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ESTADO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "menu_aberto" not in st.session_state: st.session_state.menu_aberto = False
if "pagina" not in st.session_state: st.session_state.pagina = None

# --- FLUXO DE LOGIN ---
if not st.session_state.logado:
    st.title("🕊️ Guia Espírita - Login")
    with st.form("login_guia"):
        st.text_input("👤 E-mail")
        st.text_input("🔒 Senha", type="password")
        if st.form_submit_button("🚀 ACESSAR", use_container_width=True):
            st.session_state.logado = True
            st.rerun()
else:
    @st.cache_data
    def carregar_dados():
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        # Limpeza básica das cidades para evitar nomes vazios
        df['CIDADE DO CENTRO ESPIRITA'] = df['CIDADE DO CENTRO ESPIRITA'].fillna("Não Informada").str.strip()
        return df
    
    df = carregar_dados()

    # TOPO COM BOTÃO MENU
    col1, col2 = st.columns([3,1])
    with col1:
        st.title("🕊️ Guia Espírita")
    with col2:
        if st.button("📋 MENU", use_container_width=True):
            st.session_state.menu_aberto = not st.session_state.menu_aberto
            st.rerun()

    # MENU EXPANSÍVEL
    if st.session_state.menu_aberto:
        st.markdown("---")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if st.button("🔎 Pesquisar Geral", use_container_width=True): 
                st.session_state.pagina = "pesquisar"
                st.session_state.menu_aberto = False
                st.rerun()
            if st.button("📍 Por Cidade", use_container_width=True):
                st.session_state.pagina = "cidade"
                st.session_state.menu_aberto = False
                st.rerun()
        with col_m2:
            if st.button("📊 Admin", use_container_width=True):
                st.session_state.pagina = "admin"
                st.session_state.menu_aberto = False
                st.rerun()
            if st.button("🕊️ Frases", use_container_width=True):
                st.session_state.pagina = "frases"
                st.session_state.menu_aberto = False
                st.rerun()
        if st.button("🚪 Sair", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
        st.markdown("---")

    # CONTEÚDO DAS PÁGINAS
    pagina = st.session_state.get('pagina', None)
    
    if pagina == "pesquisar":
        st.markdown("### 🔎 Pesquisar Geral")
        termo = st.text_input("Digite para buscar:", placeholder="Ex: Meimei, Catanduva...")
        if termo and len(termo) >= 3:
            termo_limpo = remover_acentos(termo)
            def checar(row):
                texto = " ".join([str(v) for v in row.values]).lower()
                return termo.lower() in texto or termo_limpo in remover_acentos(texto)
            res = df[df.apply(checar, axis=1)]
            st.info(f"Encontrados {len(res)} resultados")
            for i, (_, row) in enumerate(res.iterrows(), 1): renderizar_card(row, i)
    
    elif pagina == "cidade":
        st.markdown("### 📍 Por Cidade")
        
        # --- LÓGICA DE CONTAGEM POR CIDADE ---
        contagem_cidades = df['CIDADE DO CENTRO ESPIRITA'].value_count().to_dict()
        lista_cidades_formatada = [f"{cid} ({qtd})" for cid, qtd in sorted(contagem_cidades.items())]
        
        sel_formatado = st.selectbox("Selecione a cidade:", ["-- Selecione --"] + lista_cidades_formatada)
        
        if sel_formatado != "-- Selecione --":
            # Extrair apenas o nome da cidade removendo o (59)
            cidade_real = re.sub(r'\s\(\d+\)$', '', sel_formatado)
            res = df[df['CIDADE DO CENTRO ESPIRITA'] == cidade_real]
            st.success(f"✅ {len(res)} centro(s) em {cidade_real}")
            for i, (_, row) in enumerate(res.iterrows(), 1): renderizar_card(row, i)

    elif pagina == "admin":
        st.markdown("### 📊 Dashboard")
        st.metric("🏠 Total Centros", len(df))

    elif pagina == "frases":
        st.markdown("### 🕊️ Frases")
        st.info("Fora da caridade não há salvação. — Allan Kardec")
