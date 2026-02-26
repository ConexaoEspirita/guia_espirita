import streamlit as st
import pandas as pd
import urllib.parse
import re
import random

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Guia Espírita", 
    page_icon="🕊️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS COMPLETO ---
st.markdown("""
<style>
header[data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
.block-container { padding-top: 1rem !important; }
.stApp { background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%) !important; }

.card-centro { 
    background: white !important; padding: 25px; border-radius: 20px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.12); margin-bottom: 25px; 
    border-left: 12px solid #0047AB; position: relative;
}
.numero-badge { 
    position: absolute; top: 15px; right: 20px; background: #f0f4f8; 
    color: #7f8c8d; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 800; 
}
.nome-centro { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800; display: block; }
.palestras-verde { 
    color: #065F46 !important; font-weight: 700; background: #D1FAE5; 
    padding: 10px; border-radius: 10px; margin: 12px 0; border: 1px solid #10B981; 
}
.btn-row { display: flex; gap: 12px; margin-top: 20px; }
.btn-link { 
    text-decoration: none !important; color: white !important; padding: 14px; 
    border-radius: 12px; font-weight: 800; text-align: center; flex: 1; 
}
.bg-wa { background-color: #25D366; }
.bg-maps { background-color: #4285F4; }
.frase-box {
    background: rgba(255,255,255,0.7); padding: 20px; border-radius: 15px;
    border-italic: italic; color: #1E3A8A; font-size: 18px; text-align: center;
    margin: 20px 0; border: 1px dashed #0047AB;
}
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES ---
def ajustar_texto(txt): return str(txt).strip() if pd.notna(txt) else ""

def remover_acentos(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower()
    return re.sub(r'[àáâãäå]', 'a', re.sub(r'[èéêë]', 'e', re.sub(r'[ìíîï]', 'i', re.sub(r'[òóôõö]', 'o', re.sub(r'[ùúûü]', 'u', texto)))))

def criar_link_maps(row):
    end = ajustar_texto(row.get('ENDERECO', ''))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', ''))
    query = f"{end}, {cid}, SP"
    return f"https://www.google.com{urllib.parse.quote(query)}"

def renderizar_card(row, index):
    nome = ajustar_texto(row.get('NOME', 'Centro Espírita'))
    end = ajustar_texto(row.get('ENDERECO', ''))
    cid = ajustar_texto(row.get('CIDADE DO CENTRO ESPIRITA', ''))
    palestras = ajustar_texto(row.get('PALESTRA PUBLICA', 'Consulte'))
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    link_wa = f"https://wa.me{whats_num}" if len(whats_num) >= 10 else "#"
    
    st.markdown(f"""
    <div class="card-centro">
        <div class="numero-badge">#{index}</div>
        <span class="nome-centro">{nome} 🕊️</span>
        <div class="palestras-verde">🗣️ PALESTRAS: {palestras}</div>
        <div style="color:#333; margin-bottom:10px;"><b>📍 Endereço:</b> {end}, {cid}</div>
        <div class="btn-row">
            <a href="{criar_link_maps(row)}" target="_blank" class="btn-link bg-maps">📍 MAPA</a>
            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WhatsApp</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- ESTADOS ---
if "logado" not in st.session_state: st.session_state.logado = False
if "menu_aberto" not in st.session_state: st.session_state.menu_aberto = False
if "pagina" not in st.session_state: st.session_state.pagina = None

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
        df['CIDADE DO CENTRO ESPIRITA'] = df['CIDADE DO CENTRO ESPIRITA'].fillna("Não Informada").str.strip()
        return df
    
    df = carregar_dados()

    # TOPO
    col1, col2 = st.columns([3,1])
    with col1: st.title("🕊️ Guia Espírita")
    with col2:
        if st.button("📋 MENU", use_container_width=True):
            st.session_state.menu_aberto = not st.session_state.menu_aberto
            if not st.session_state.menu_aberto:
                st.session_state.pagina = None
            st.rerun()

    # MENU
    if st.session_state.menu_aberto:
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔎 Pesquisar", use_container_width=True): 
                st.session_state.pagina = "pesquisar"; st.session_state.menu_aberto = False; st.rerun()
            if st.button("📍 Cidades", use_container_width=True):
                st.session_state.pagina = "cidade"; st.session_state.menu_aberto = False; st.rerun()
        with c2:
            if st.button("🕊️ Frases", use_container_width=True):
                st.session_state.pagina = "frases"; st.session_state.menu_aberto = False; st.rerun()
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.clear(); st.rerun()
        st.markdown("---")

    # PÁGINAS
    p = st.session_state.pagina
    
    if p == "pesquisar":
        st.subheader("🔎 Busca Geral")
        t = st.text_input("Digite o nome ou cidade (mín. 3 letras):")
        if len(t) >= 3:
            t_limpo = remover_acentos(t)
            def checar(row):
                texto = " ".join([str(v) for v in row.values]).lower()
                return t.lower() in texto or t_limpo in remover_acentos(texto)
            res = df[df.apply(checar, axis=1)]
            st.write(f"Exibindo {len(res)} resultados:")
            for i, (_, r) in enumerate(res.iterrows(), 1): renderizar_card(r, i)

    elif p == "cidade":
        st.subheader("📍 Por Cidade")
        # Contagem correta usando value_counts()
        counts = df['CIDADE DO CENTRO ESPIRITA'].value_counts().to_dict()
        opcoes = [f"{c} ({q})" for c, q in sorted(counts.items())]
        sel = st.selectbox("Escolha uma cidade:", ["-- Selecione --"] + opcoes)
        if sel != "-- Selecione --":
            nome_cid = re.sub(r'\s\(\d+\)$', '', sel)
            res = df[df['CIDADE DO CENTRO ESPIRITA'] == nome_cid]
            for i, (_, r) in enumerate(res.iterrows(), 1): renderizar_card(r, i)

    elif p == "frases":
        st.subheader("🕊️ Mensagens de Luz")
        frases = [
            ("Fora da caridade não há salvação.", "Allan Kardec"),
            ("A felicidade não é deste mundo.", "Allan Kardec"),
            ("O Cristo não pediu muita coisa... Ele só pediu que nos amássemos uns aos outros.", "Chico Xavier"),
            ("Tudo o que é teu virá ter contigo.", "Chico Xavier"),
            ("Nascer, viver, morrer, renascer ainda e progredir sempre, tal é a lei.", "Allan Kardec"),
            ("A caridade é o processo de somar alegrias, diminuir males, multiplicar esperanças e dividir a felicidade.", "Emmanuel")
        ]
        for f, autor in frases:
            st.markdown(f'<div class="frase-box">"{f}"<br><small>— <b>{autor}</b></small></div>', unsafe_allow_html=True)

    elif not st.session_state.menu_aberto:
        st.info("Toque no MENU para pesquisar centros ou ler frases! 🕊️")
