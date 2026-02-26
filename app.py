import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    /* Remove seta/voltar superior */
    [data-testid="stArrowBack"] { display: none !important; }
    
    /* Remove COMPLETAMENTE sidebar */
    section[data-testid="stSidebar"] > div { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    
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
    
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    link_wa = f"https://wa.me/+55{whats_num}" if len(whats_num) >= 10 else "#"
    
    nome_google = ajustar_texto(row.get('NOME_GOOGLE_MAPS', ''))
    if nome_google:
        query_limpo = urllib.parse.quote(nome_google)
    else:
        endereco_limpo = re.sub(r'[,\\s]+', ', ', end)[:100]
        query_limpo = urllib.parse.quote(f"{endereco_limpo}, {cid}")
    link_maps = f"https://www.google.com/maps/search/?api=1&query={query_limpo}"

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

# --- Inicializar session state ---
if "pagina" not in st.session_state:
    st.session_state.pagina = None

# --- LOGIN ---
if "logado" not in st.session_state: 
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🕊️ Guia Espírita")
    st.markdown("### Bem-vindo!")
    with st.form("login_guia"):
        u = st.text_input("👤 E-mail")
        p = st.text_input("🔒 Senha", type="password")
        if st.form_submit_button("🚀 ACESSAR", use_container_width=True):
            st.session_state.logado = True
            st.rerun()
else:
    @st.cache_data
    def carregar_dados():
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        return df
    df = carregar_dados()

    # ✅ MENU SEMPRE NO TOPO
    with st.expander("📋 MENU PRINCIPAL", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔎 Pesquisar Geral", use_container_width=True):
                st.session_state.pagina = "pesquisar"
                st.rerun()
            
            if st.button("📍 Por Cidade", use_container_width=True):
                st.session_state.pagina = "cidade"
                st.rerun()
        
        with col2:
            if st.button("📊 Admin", use_container_width=True):
                st.session_state.pagina = "admin"
                st.rerun()
            
            if st.button("🕊️ Frases", use_container_width=True):
                st.session_state.pagina = "frases"
                st.rerun()
        
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logado = False
            st.session_state.pagina = None
            st.cache_data.clear()
            st.rerun()

    # ✅ BOTÃO VOLTAR COM SETA (SE TEM PÁGINA ABERTA)
    pagina = st.session_state.get('pagina', None)
    if pagina:
        col1, col2, col3 = st.columns([1, 1, 8])
        with col1:
            if st.button("⬅️ VOLTAR"):
                st.session_state.pagina = None
                st.rerun()
        with col2:
            st.markdown(f"### {pagina.replace('pesquisar', '🔎 Pesquisar').replace('cidade', '📍 Cidades').replace('admin', '📊 Admin').replace('frases', '🕊️ Frases').title()}")

    # ✅ CONTEÚDO DAS PÁGINAS
    if pagina == "pesquisar":
        termo = st.text_input("🔍 Digite pelo menos 3 letras:", placeholder="Ex: Meimei, Euripedes, Catanduva...")
        if termo and len(termo) >= 3:
            palavras = termo.lower().split()
            def normalizar(t): 
                return "" if pd.isna(t) else " ".join(str(t).lower().split())
            def checar(row):
                texto_completo = " ".join([normalizar(row[col]) for col in df.columns])
                return any(palavra in texto_completo for palavra in palavras)
            res = df[df.apply(checar, axis=1)]
            if len(res) > 0:
                st.success(f"✅ Encontrados {len(res)} centro(s)")
                for i, (_, row) in enumerate(res.iterrows(), 1):
                    renderizar_card(row, i)
            else: 
                st.warning("❌ Nenhum resultado encontrado.")
        elif termo: 
            st.warning("⚠️ Mínimo 3 letras!")

    elif pagina == "cidade":
        st.markdown("### 📍 Escolha a Cidade")
        cidades = df['CIDADE DO CENTRO ESPIRITA'].dropna().unique()
        cidades_com_contagem = []
        for cidade in sorted(cidades):
            cidade_limpa = str(cidade).strip()
            if (cidade_limpa.lower() not in ['nome da cidade do centro espirit a', 'nome da cidade do centro espírita', 'nome', 'cidade', '']
                and len(cidade_limpa) > 2):
                count = len(df[df['CIDADE DO CENTRO ESPIRITA'] == cidade])
                cidades_com_contagem.append(f"{cidade_limpa} ({count})")
        
        sel = st.selectbox("🌆 Selecione:", ["-- Todas as cidades --"] + cidades_com_contagem)
        if sel != "-- Todas as cidades --":
            cidade_selecionada = sel.split(' (')[0].strip()
            res = df[df['CIDADE DO CENTRO ESPIRITA'] == cidade_selecionada]
            st.success(f"✅ {len(res)} centro(s) em **{cidade_selecionada}**")
            for i, (_, row) in enumerate(res.iterrows(), 1):
                renderizar_card(row, i)

    elif pagina == "admin":
        st.markdown("### 📊 Painel Admin")
        col1, col2 = st.columns(2)
        col1.metric("🏠 Total Centros", len(df))
        col2.metric("📍 Cidades Únicas", len(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique()))

    elif pagina == "frases":
        st.markdown("### 🕊️ Frases Espíritas")
        frases = [
            "> **Fora da caridade não há salvação.** — Allan Kardec",
            "> **Amai-vos uns aos outros.** — Jesus",
            "> **Ninguém é perfeito, mas todos podem melhorar.** — Emmanuel"
        ]
        for frase in frases:
            st.markdown(frase)
