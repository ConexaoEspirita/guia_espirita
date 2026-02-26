import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { padding-top: 20px; }
    div[data-testid="stSidebar"] .st-emotion-cache-167909c { font-size: 1.2rem !important; font-weight: 600 !important; }
    .stApp { background: #f4f7f9; }
    
    .stTextInput > div > div > input {
        border: 3px solid #3B82F6 !important; border-radius: 12px !important;
        padding: 15px 20px !important; font-size: 16px !important; font-weight: 600 !important;
        background: linear-gradient(145deg, #ffffff, #f8fafc) !important;
        box-shadow: 0 4px 15px rgba(59,130,246,0.2) !important;
    }
    .titulo-principal { font-size: 28px !important; color: #1E3A8A !important; }
    .titulo-secundario { font-size: 20px !important; color: #1E3A8A !important; }
    
    .card-centro { background: white !important; padding: 25px; border-radius: 20px; 
                   box-shadow: 0 10px 30px rgba(0,0,0,0.12); margin-bottom: 25px; 
                   border-left: 12px solid #0047AB; position: relative; }
    .numero-badge { position: absolute; top: 15px; right: 20px; background: #f0f4f8; 
                    color: #7f8c8d; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 800; }
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
    if len(whats_num) >= 10:
        whats_num_com_prefixo = "+55" + whats_num
        link_wa = f"https://wa.me/{whats_num_com_prefixo}"
    else:
        link_wa = "#"
    
    if end.strip():
        link_maps = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{end}, {cid}')}"
    else:
        link_maps = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{nome}, {cid}')}"
    
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

# --- LOGIN ---
if "logado" not in st.session_state: 
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🕊️ Guia Espírita")
    with st.form("login_guia"):
        u = st.text_input("E-mail")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("🔐 ACESSAR", use_container_width=True):
            st.session_state.logado = True
            st.rerun()
else:
    with st.sidebar:
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
        
        opcao = st.radio("Navegação:", 
                         ["🏠 Início", "🔎 Pesquisar Geral", "📍 Por Cidade", "📊 Admin", "🕊️ Frases", "🚪 Sair"], 
                         label_visibility="collapsed",
                         help="👆 Navegação principal do sistema")

    if opcao == "🚪 Sair":
        st.session_state.logado = False
        st.cache_data.clear()
        st.rerun()

    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()

    # --- MENU HAMBURGER CORRIGIDO ☰ ---
    if "menu_aberto" not in st.session_state:
        st.session_state.menu_aberto = False

    if opcao == "🔎 Pesquisar Geral":
        col1, col2 = st.columns([8,1])
        with col1:
            st.markdown('<h2 class="titulo-secundario">🔍 Pesquisar Geral</h2>', unsafe_allow_html=True)
        with col2:
            if st.button("☰", key="hamb_menu", help="Menu rápido"):
                st.session_state.menu_aberto = True  # ✅ CORRIGIDO: SEMPRE ABRE
        
        # TOOLTIP QUE SUMI AO CLICAR
        if st.session_state.menu_aberto:
            st.markdown("---")
            col_menu1, col_menu2, col_menu3, col_menu4 = st.columns(4)
            with col_menu1:
                if st.button("🔎 Pesq. Geral", key="menu1"):
                    st.session_state.opcao = "🔎 Pesquisar Geral"
                    st.session_state.menu_aberto = False  # ✅ FECHA
                    st.rerun()
            with col_menu2:
                if st.button("📍 Cidade", key="menu2"):
                    st.session_state.opcao = "📍 Por Cidade" 
                    st.session_state.menu_aberto = False  # ✅ FECHA
                    st.rerun()
            with col_menu3:
                if st.button("📊 Admin", key="menu3"):
                    st.session_state.opcao = "📊 Admin"
                    st.session_state.menu_aberto = False  # ✅ FECHA
                    st.rerun()
            with col_menu4:
                if st.button("🕊️ Frases", key="menu4"):
                    st.session_state.opcao = "🕊️ Frases"
                    st.session_state.menu_aberto = False  # ✅ FECHA
                    st.rerun()
            st.markdown("---")
        
        termo = st.text_input("🔍 Digite pelo menos 4 letras para buscar:", 
                             placeholder="Ex: Centro, João, São Paulo...",
                             help="Busca em nome, cidade e responsável")
        
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
            else: 
                st.warning("❌ Nenhum resultado encontrado.")
        elif termo: 
            st.warning("⚠️ Digite pelo menos 4 letras!")

    elif opcao == "🏠 Início":
        st.markdown('<h1 class="titulo-principal">🕊️ Bem-vindo ao Guia</h1>', unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; padding: 25px; background: white; border-radius: 15px; 
                    border: 2px solid #3B82F6; box-shadow: 0 8px 25px rgba(59,130,246,0.15); margin: 30px 0;'>
            <div style='font-size: 36px; margin: 15px 0; color: #3B82F6;'>👈 Menu Lateral</div>
            <p style='margin: 0; font-size: 16px; color: #1E3A8A; font-weight: 500;'>Selecione "Pesquisar Geral" ou "Por Cidade"</p>
        </div>
        """, unsafe_allow_html=True)

    elif opcao == "📍 Por Cidade":
        st.markdown('<h2 class="titulo-secundario">Buscar por Cidade</h2>', unsafe_allow_html=True)
        cidades = sorted(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique())
        sel = st.selectbox("Selecione a cidade:", 
                          ["-- Selecione uma cidade --"] + cidades, 
                          help="Escolha sua cidade para ver os centros espíritas")
        if sel != "-- Selecione uma cidade --":
            res_cidade = df[df['CIDADE DO CENTRO ESPIRITA'] == sel]
            st.success(f"✅ Encontrados {len(res_cidade)} centro(s) em {sel}")
            for i, (_, row) in enumerate(res_cidade.iterrows(), 1):
                renderizar_card(row, i)

    elif opcao == "📊 Admin":
        st.markdown('<h1 class="titulo-principal">📊 Painel Administrativo</h1>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏠 Total Centros", len(df))
        with col2:
            st.metric("📍 Cidades Únicas", len(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique()))
        with col3:
            st.metric("👥 Visitas Hoje", "127")
        st.info("🔧 **Painel Admin** - Estatísticas em tempo real")

    elif opcao == "🕊️ Frases":
        st.markdown('<h1 class="titulo-principal">🕊️ Frases Espíritas</h1>', unsafe_allow_html=True)
        st.info("📖 **Em desenvolvimento** - Frases inspiradoras do espiritismo")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            > "Fora da caridade não há salvação."  
            **Allan Kardec**
            """)
        with col2:
            st.markdown("""
            > "Amai-vos uns aos outros."  
            **Jesus**
            """)
