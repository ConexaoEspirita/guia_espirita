import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    [data-testid="stArrowBack"] { display: none !important; }
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

def remover_acentos(texto):
    """Remove acentos para busca flexível"""
    if pd.isna(texto):
        return ""
    texto = str(texto).lower()
    return re.sub(
        r'[àáâãäå]', 'a', re.sub(
        r'[èéêë]', 'e', re.sub(
        r'[ìíîï]', 'i', re.sub(
        r'[òóôõö]', 'o', re.sub(
        r'[ùúûü]', 'u', texto)))))

def criar_link_maps(row):
    nome_google = ajustar_texto(row.get('NOME_GOOGLE_MAPS', ''))
    end = ajustar_texto(row.get('ENDERECO', ''))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', ''))
    bairro = ajustar_texto(row.get('BAIRRO', ''))
    
    if nome_google and len(nome_google) > 3:
        return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(nome_google)}"
    
    if end and cid:
        endereco_limpo = re.sub(r'[,\s]+', ', ', end.strip())[:120]
        query = f"{endereco_limpo}, {bairro}, {cid}, SP" if bairro else f"{endereco_limpo}, {cid}, SP"
        return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"
    
    return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(cid or 'São Paulo')}"

def renderizar_card(row, index):
    nome = ajustar_texto(row.get('NOME', 'Centro Espírita'))
    fantasia = ajustar_texto(row.get('NOME FANTASIA', ''))
    end = ajustar_texto(row.get('ENDERECO', ''))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', ''))
    palestras = ajustar_texto(row.get('PALESTRA PUBLICA', 'Consulte'))
    resp = ajustar_texto(row.get('RESPONSAVEL', 'N/I'))
    
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    link_wa = f"https://wa.me/55{whats_num}" if len(whats_num) >= 10 else "#"
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

# --- Session state ---
if "logado" not in st.session_state: 
    st.session_state.logado = False
if "menu_aberto" not in st.session_state:
    st.session_state.menu_aberto = False
if "pagina" not in st.session_state:
    st.session_state.pagina = None

# --- LOGIN ---
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
        return df
    
    df = carregar_dados()
    st.title("🕊️ Guia Espírita")

    if st.button("📋 " + ("Fechar Menu" if st.session_state.menu_aberto else "Abrir Menu"), use_container_width=True):
        st.session_state.menu_aberto = not st.session_state.menu_aberto
        st.rerun()

    if st.session_state.menu_aberto:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔎 Pesquisar Geral", use_container_width=True): 
                st.session_state.pagina = "pesquisar"
                st.session_state.menu_aberto = False
                st.rerun()
            if st.button("📍 Por Cidade", use_container_width=True):
                st.session_state.pagina = "cidade"
                st.session_state.menu_aberto = False
                st.rerun()
        with col2:
            if st.button("📊 Admin", use_container_width=True):
                st.session_state.pagina = "admin"
                st.session_state.menu_aberto = False
                st.rerun()
            if st.button("🕊️ Frases", use_container_width=True):
                st.session_state.pagina = "frases"
                st.session_state.menu_aberto = False
                st.rerun()
        if st.button("🚪 Sair", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.markdown("---")

    pagina = st.session_state.get('pagina', None)
    
    if pagina == "pesquisar":
        st.markdown("### 🔎 Pesquisar Geral")
        termo = st.text_input("Digite pelo menos 3 letras para buscar:", placeholder="Ex: Meimei, Euripedes, Catanduva...")
        
        if termo and len(termo) >= 3:
            termo_sem_acento = remover_acentos(termo)
            palavras = termo.lower().split() + [termo_sem_acento]
            
            def checar(row):
                texto_completo = " ".join([str(row[col]).lower() for col in df.columns if pd.notna(row[col])])
                texto_sem_acento = remover_acentos(texto_completo)
                return any(palavra in texto_completo or palavra in texto_sem_acento for palavra in palavras)
            
            res = df[df.apply(checar, axis=1)]
            if len(res) > 0:
                st.success(f"✅ Encontrados {len(res)} centro(s)")
                for i, (_, row) in enumerate(res.iterrows(), 1):
                    renderizar_card(row, i)
            else: 
                st.warning("❌ Nenhum resultado encontrado.")
        elif termo: 
            st.warning("⚠️ Mínimo de 3 letras!")
    
    elif pagina == "cidade":
        st.markdown("### 📍 Por Cidade")
        cidades = df['CIDADE DO CENTRO ESPIRITA'].dropna().unique()
        cidades_com_contagem = []
        for cidade in sorted(cidades):
            cidade_limpa = str(cidade).strip()
            if (cidade_limpa.lower() not in ['nome da cidade do centro espirit a', 'nome da cidade do centro espírita', 'nome', 'cidade', ''] 
                and len(cidade_limpa) > 2):
                count = len(df[df['CIDADE DO CENTRO ESPIRITA'] == cidade])
                cidades_com_contagem.append(f"{cidade_limpa} ({count})")
        
        sel = st.selectbox("Selecione a cidade:", ["-- Selecione --"] + cidades_com_contagem)
        if sel != "-- Selecione --":
            cidade_selecionada = sel.split(' (')[0].strip()
            res = df[df['CIDADE DO CENTRO ESPIRITA'] == cidade_selecionada]
            st.success(f"✅ Encontrados {len(res)} centro(s) em {cidade_selecionada}")
            for i, (_, row) in enumerate(res.iterrows(), 1):
                renderizar_card(row, i)

    elif pagina == "admin":
        st.markdown("### 📊 Dashboard Admin")
        col1, col2, col3 = st.columns(3)
        col1.metric("🏠 Total Centros", len(df))
        col2.metric("📍 Cidades", len(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique()))
        col3.metric("📱 Com WhatsApp", len(df[df['CELULAR'].notna()]))

    elif pagina == "frases":
        st.markdown("### 🕊️ Frases Espíritas")
        st.markdown("> **Fora da caridade não há salvação.** — Allan Kardec")
        st.markdown("> **Nascer, sofrer, morrer, abençoados sejam os que assim sofrem!** — Emmanuel")
        st.markdown("> **Onde reina o amor, não há desejos de vingança.** — Chico Xavier")
