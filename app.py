import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(
    page_title="Guia Espírita", 
    page_icon="🕊️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS: APENAS O AJUSTE PARA O BOTÃO DE LOGIN APARECER ---
st.markdown("""
<style>
* {
    -webkit-touch-callout: none !important;
    -webkit-user-select: none !important;
    touch-action: manipulation !important;
    overscroll-behavior: none !important;
}

/* REMOVIDO 'button' DAQUI PARA O LOGIN FUNCIONAR */
[data-testid*="back"], [data-testid*="header"], 
button[kind="header"], button[aria-label*="voltar"],
button[title*="voltar"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
    height: 0 !important;
    width: 0 !important;
}

section[data-testid="stSidebar"] { display: none !important; }

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

def ajustar_texto(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def remover_acentos(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower()
    return re.sub(r'[àáâãäå]', 'a', re.sub(r'[èéêë]', 'e', re.sub(r'[ìíîï]', 'i', re.sub(r'[òóôõö]', 'o', re.sub(r'[ùúûü]', 'u', texto)))))

def criar_link_maps(row):
    nome_google = ajustar_texto(row.get('NOME_GOOGLE_MAPS', ''))
    end = ajustar_texto(row.get('ENDERECO', ''))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', ''))
    
    # Tanabi ESPECÍFICO
    if 'tanabi' in cid.lower():
        if nome_google and len(nome_google) > 3:
            return f"https://www.google.com{urllib.parse.quote(nome_google + ', Tanabi SP')}"
        if end:
            return f"https://www.google.com{urllib.parse.quote(end + ', Tanabi SP')}"
        return "https://www.google.com"
    
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

# --- SESSÃO E LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False
if "menu_aberto" not in st.session_state: st.session_state.menu_aberto = False
if "pagina" not in st.session_state: st.session_state.pagina = None

if not st.session_state.logado:
    st.title("🕊️ Guia Espírita - Login")
    with st.form("login"):
        st.text_input("E-mail")
        st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR", use_container_width=True):
            st.session_state.logado = True
            st.rerun()
else:
    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()

    col1, col2 = st.columns([3,1])
    with col1: st.title("🕊️ Guia Espírita")
    with col2:
        if st.button("📋 MENU", use_container_width=True):
            st.session_state.menu_aberto = not st.session_state.menu_aberto
            if not st.session_state.menu_aberto: st.session_state.pagina = None
            st.rerun()

    if st.session_state.menu_aberto:
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔎 Pesquisar", use_container_width=True): 
                st.session_state.pagina = "pesquisar"; st.session_state.menu_aberto = False; st.rerun()
            if st.button("📍 Cidade", use_container_width=True): 
                st.session_state.pagina = "cidade"; st.session_state.menu_aberto = False; st.rerun()
        with c2:
            if st.button("🕊️ Frases", use_container_width=True): 
                st.session_state.pagina = "frases"; st.session_state.menu_aberto = False; st.rerun()
            if st.button("🚪 Sair", use_container_width=True): 
                st.session_state.clear(); st.rerun()
        st.markdown("---")

    p = st.session_state.pagina
    if p == "pesquisar":
        t = st.text_input("Busca:")
        if len(t) >= 3:
            res = df[df.apply(lambda r: t.lower() in str(r.values).lower(), axis=1)]
            for i, (_, r) in enumerate(res.iterrows(), 1): renderizar_card(r, i)

    elif p == "cidade":
        counts = df['CIDADE DO CENTRO ESPIRITA'].value_counts().to_dict()
        ops = [f"{c} ({q})" for c, q in sorted(counts.items())]
        sel = st.selectbox("Cidade:", ["-- Selecione --"] + ops)
        if sel != "-- Selecione --":
            cid_real = re.sub(r'\s\(\d+\)$', '', sel)
            res = df[df['CIDADE DO CENTRO ESPIRITA'] == cid_real]
            for i, (_, r) in enumerate(res.iterrows(), 1): renderizar_card(r, i)

    elif p == "frases":
        st.info("Fora da caridade não há salvação. - Allan Kardec")
