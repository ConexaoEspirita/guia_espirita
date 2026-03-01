import streamlit as st
import pandas as pd
import datetime
import unicodedata
from supabase import create_client, Client

# =========================
# CONFIGURAÇÃO DO STREAMLIT
# =========================
st.set_page_config(page_title="Guia Espírita", layout="wide")

# =========================
# CONFIGURAÇÃO SUPABASE
# =========================
SUPABASE_URL = "https://SEU_SUPABASE_URL.supabase.co"
SUPABASE_KEY = "SUA_SUPABASE_ANON_KEY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    link_maps = f"https://www.google.com/maps/search/?api=1&query={query}"
    link_wa = f"https://wa.me/55{numero}" if len(numero)>=10 else "#"

    st.markdown(f"""
    <div class="card-centro">
        <div style="position:absolute; top:10px; right:15px; font-size:12px; color:#6B7280;">#{index}</div>
        <div style="color: #1E3A8A; font-size: 22px; font-weight: 800;">{nome} 🕊️</div>
        {"<div style='color: #3B82F6; font-style: italic;'>" + fantasia + "</div>" if fantasia else ""}
        <div style="color:#065F46; font-weight:700; background:#D1FAE5; padding:8px; border-radius:8px; margin:10px 0;">🗣️ PALESTRA: {palestra}</div>
        <div style="margin:5px 0;">👤 <b>Responsável:</b> {responsavel}</div>
        <div style="margin:5px 0;">🏙️ <b>Cidade:</b> {cidade}</div>
        <div style="margin:5px 0;">📍 <b>Endereço:</b> {endereco}</div>
        <div style="margin-top:15px; display:flex; gap:10px;">
            <a href="{link_maps}" target="_blank" style="background:#4285F4;color:white;padding:10px;border-radius:10px;text-align:center;display:inline-block;width:100%;">📍 Maps</a>
            <a href="{link_wa}" target="_blank" style="background:#25D366;color:white;padding:10px;border-radius:10px;text-align:center;display:inline-block;width:100%;">WhatsApp</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# LOGIN E NAVEGAÇÃO
# =========================
if not st.session_state.get("logado", False):
    st.markdown("<div style='text-align: center; color: #60A5FA; font-size: 32px; font-weight: 800;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🚪 Entrar", "✨ Cadastrar"])
    
    with tab1:
        with st.form("login"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                # Aqui você deve validar com Supabase auth (não incluído neste exemplo)
                st.session_state["logado"] = True
                st.rerun()
    
    with tab2:
        with st.form("cadastro"):
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Cadastrar", use_container_width=True):
                # Inserir no Supabase tabela 'participantes'
                supabase.table("participantes").insert({
                    "nome": nome,
                    "email": email,
                    "status": "ativo",
                    "created_at": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
                }).execute()
                st.session_state["logado"] = True
                st.success("✅ Cadastrado com sucesso!")
                st.rerun()

else:
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
            st.session_state.clear(); st.rerun()

    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ VOLTAR", use_container_width=True): st.session_state["pagina"] = None; st.rerun()
        with col2:
            if st.button("🔄 LIMPAR", use_container_width=True): st.session_state["termo_pesquisa"] = ""; st.rerun()

        if pagina == "pesquisar":
            st.info("Busca Avançada ainda exibe centros do Excel (sem alteração).")

        elif pagina == "cidade":
            st.info("Busca por cidade ainda exibe centros do Excel (sem alteração).")

        elif pagina == "admin":
            # SENHA DO ADMIN
            admin_senha = st.text_input("Senha Admin:", type="password")
            if admin_senha == "estudantesabio2026":
                # Buscar participantes reais do Supabase
                res = supabase.table("participantes").select("*").execute()
                participantes = res.data
                if participantes:
                    # Transformar em DataFrame
                    df_p = pd.DataFrame(participantes)
                    # Formatar último acesso
                    if "ultimo_acesso" in df_p.columns:
                        df_p["ultimo_acesso"] = pd.to_datetime(df_p["ultimo_acesso"]).dt.strftime("%d/%m/%Y %H:%M")
                    else:
                        df_p["ultimo_acesso"] = "-"
                    
                    # Mostrar tabela compacta
                    st.subheader("📋 Participantes Cadastrados")
                    st.dataframe(df_p[["nome", "email", "status", "ultimo_acesso"]], use_container_width=True, height=300)
                    
                    # Botão atualizar último acesso
                    if st.button("Atualizar último acesso para todos"):
                        agora_br = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
                        for p in participantes:
                            supabase.table("participantes").update({"ultimo_acesso": agora_br}).eq("id", p["id"]).execute()
                        st.success("Último acesso atualizado para todos participantes!")
                        st.experimental_rerun()
                else:
                    st.info("Nenhum participante cadastrado.")
            else:
                st.warning("❌ Senha Admin necessária")

        elif pagina == "frases":
            st.info("Fora da caridade não há salvação. — Allan Kardec")
