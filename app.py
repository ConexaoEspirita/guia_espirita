import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import datetime
from supabase import create_client, Client

# =========================
# SUPABASE - CREDENCIAIS
# =========================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Guia Espírita", layout="wide")

# =========================
# SESSION STATE
# =========================
if "pagina" not in st.session_state:
    st.session_state["pagina"] = None
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "termo_pesquisa" not in st.session_state:
    st.session_state["termo_pesquisa"] = ""

# =========================
# CSS
# =========================
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    [data-testid="stStatusWidget"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
    }

    .stApp { background: #f4f7f9; }
    .titulo-grande { font-size: 32px; font-weight: 800; margin-bottom: 8px; }
    
    .card-centro { 
        background: white;
        padding: 25px;
        border-radius: 20px; 
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.12); 
        border-left: 12px solid #0060D0;
        position: relative;
    }
    
    .btn-link { 
        text-decoration:none; 
        color:white !important; 
        padding:10px; 
        border-radius:10px; 
        font-weight:700; 
        text-align:center; 
        display:inline-block; 
        width: 100%;
    }

    /* Estilo para os registros no Admin */
    .admin-registro {
        font-size: 13px;
        border-bottom: 1px solid #eee;
        padding: 8px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .admin-data {
        font-size: 11px;
        color: #6B7280;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# FUNÇÕES DE APOIO
# =========================
def ajustar(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def normalize_text(text):
    if pd.isna(text): return ""
    return unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8').lower()

def renderizar_card(row, index):
    nome = ajustar(row.get('NOME', 'Centro Espírita'))
    fantasia = ajustar(row.get('NOME FANTASIA'))
    endereco = ajustar(row.get('ENDERECO'))
    cidade = ajustar(row.get('CIDADE DO CENTRO ESPIRITA'))
    palestra = ajustar(row.get('PALESTRA PUBLICA'))
    responsavel = ajustar(row.get('RESPONSAVEL'))
    numero = "".join(filter(str.isdigit, str(row.get('CELULAR'))))

    query = urllib.parse.quote(f"{endereco}, {cidade}")
    link_maps = f"https://www.google.com{query}"
    link_wa = f"https://wa.me{numero}" if len(numero)>=10 else "#"

    st.markdown(f"""
    <div class="card-centro">
        <div style="position:absolute; top:10px; right:15px; font-size:12px; color:#6B7280; background:rgba(255,255,255,0.8); padding:2px 6px; border-radius:12px; font-weight:500;">#{index}</div>
        <div style="color: #1E3A8A; font-size: 22px; font-weight: 800;">{nome} 🕊️</div>
        {"<div style='color: #3B82F6; font-style: italic;'>" + fantasia + "</div>" if fantasia else ""}
        <div style="color:#065F46; font-weight:700; background:#D1FAE5; padding:8px; border-radius:8px; margin:10px 0;">🗣️ PALESTRA: {palestra}</div>
        <div style="margin:5px 0;">🏙️ <b>Cidade:</b> {cidade}</div>
        <div style="margin:5px 0;">📍 <b>Endereço:</b> {endereco}</div>
        <div style="margin-top:15px; display:flex; gap:10px;">
            <a href="{link_maps}" target="_blank" class="btn-link" style="background:#4285F4;">📍 Maps</a>
            <a href="{link_wa}" target="_blank" class="btn-link" style="background:#25D366;">WhatsApp</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# LOGIN E NAVEGAÇÃO
# =========================
if not st.session_state.get("logado", False):
    st.markdown("<div style='text-align: center; color: #60A5FA; font-size: 32px; font-weight: 800; margin-bottom: 30px;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🚪 Entrar", "✨ Cadastrar"])
    
    with tab1:
        with st.form("login"):
            email_log = st.text_input("E-mail")
            senha_log = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                st.session_state["logado"] = True
                st.rerun()
    
    with tab2:
        with st.form("cadastro"):
            nome_cad = st.text_input("Nome Completo")
            email_cad = st.text_input("E-mail")
            senha_cad = st.text_input("Senha", type="password")
            if st.form_submit_button("Cadastrar", use_container_width=True):
                # ENVIA PARA O SUPABASE
                agora_br = datetime.datetime.now() - datetime.timedelta(hours=3)
                data_hora_cad = agora_br.strftime('%d-%m-%Y %H:%M:%S')
                try:
                    supabase.table("participantes").insert({
                        "nome": nome_cad, 
                        "email": email_cad, 
                        "criado_em": data_hora_cad
                    }).execute()
                    st.session_state["logado"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar no banco: {e}")
else:
    # HORÁRIO, DATA E LINHA SUPERIOR
    agora_br = datetime.datetime.now() - datetime.timedelta(hours=3)
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
        <span style="font-weight: 800; color: #1E3A8A;">{agora_br.strftime('%H:%M')}</span>
        <span style="font-weight: 800; color: #1E3A8A;">{agora_br.strftime('%d/%m/%Y')}</span>
        <hr style="flex-grow: 1; border: none; border-top: 1px solid #ccc; margin: 0;">
    </div>
    """, unsafe_allow_html=True)

    @st.cache_data
    def carregar_dados():
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        return df

    df = carregar_dados()
    pagina = st.session_state.get("pagina")

    if pagina is None:
        st.markdown("<div class='titulo-grande' style='color: #60A5FA; text-align: center;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔎 Busca Avançada", use_container_width=True): st.session_state["pagina"] = "pesquisar"; st.rerun()
            if st.button("📍 Por Cidade", use_container_width=True): st.session_state["pagina"] = "cidade"; st.rerun()
        with c2:
            if st.button("📊 Admin", use_container_width=True): st.session_state["pagina"] = "admin"; st.rerun()
            if st.button("🕊️ Frases", use_container_width=True): st.session_state["pagina"] = "frases"; st.rerun()
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear(); st.cache_data.clear(); st.rerun()

    else:
        if st.button("⬅️ VOLTAR", use_container_width=True): st.session_state["pagina"] = None; st.rerun()

        if pagina == "pesquisar":
            termo = st.text_input("Digite o que busca:", value=st.session_state["termo_pesquisa"])
            if termo and len(termo.strip()) >= 3:
                t_norm = normalize_text(termo.strip())
                res = df[df.apply(lambda r: t_norm in normalize_text(" ".join(r.astype(str))), axis=1)]
                for i, (_, row) in enumerate(res.iterrows(), 1): renderizar_card(row, i)

        elif pagina == "cidade":
            contagem = df["CIDADE DO CENTRO ESPIRITA"].value_counts().to_dict()
            cids = sorted(df["CIDADE DO CENTRO ESPIRITA"].dropna().unique())
            opts = [f"{c} ({contagem.get(c, 0)})" for c in cids]
            sel = st.selectbox("Selecione:", ["-- Selecione --"] + opts)
            if sel != "-- Selecione --":
                c_real = sel.rsplit(" (", 1)[0]
                res = df[df["CIDADE DO CENTRO ESPIRITA"] == c_real]
                for i, (_, row) in enumerate(res.iterrows(), 1): renderizar_card(row, i)

        elif pagina == "admin":
            admin_senha = st.text_input("Senha Admin:", type="password")
            if admin_senha == "estudantesabio2026":
                st.write("### 👥 Usuários Cadastrados (Supabase)")
                
                try:
                    usuarios = supabase.table("participantes").select("*").execute()
                    for u in usuarios.data:
                        # DATA E HORA EM HORIZONTAL E MENOR
                        st.markdown(f"""
                        <div class="admin-registro">
                            <span><b>{u['nome']}</b> ({u['email']})</span>
                            <span class="admin-data">{u.get('criado_em', '---')}</span>
                        </div>
                        """, unsafe_allow_html=True)
                except:
                    st.error("Erro ao carregar dados do Supabase.")
            else:
                st.warning("❌ Senha Admin necessária")

        elif pagina == "frases":
            st.markdown("### 🕊️ Mensagem de Chico Xavier")
            st.info('"Embora ninguém possa voltar atrás e fazer um novo começo, qualquer um pode começar agora e fazer um novo fim." \n\n— **Chico Xavier**')
