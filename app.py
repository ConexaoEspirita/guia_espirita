import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import datetime
from supabase import create_client, Client

# =========================
# SUPABASE - COLE SUAS CREDENCIAIS AQUI
# =========================
SUPABASE_URL = "https://SEU_PROJETO.supabase.co"  # ← SUBSTITUA PELA SUA URL
SUPABASE_KEY = "SUA_ANON_KEY"                     # ← SUBSTITUA PELA SUA KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# CONFIGURAÇÃO DO STREAMLIT
# =========================
st.set_page_config(page_title="🕊️ Guia Espírita", layout="wide")

# =========================
# SESSION STATE
# =========================
if "pagina" not in st.session_state:
    st.session_state["pagina"] = None
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "termo_pesquisa" not in st.session_state:
    st.session_state["termo_pesquisa"] = ""
if "admin_logado" not in st.session_state:
    st.session_state["admin_logado"] = False

# =========================
# CSS PROFISSIONAL
# =========================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stApp { background: #f4f7f9; }
.titulo-grande { 
    font-size: 32px; 
    font-weight: 800; 
    text-align: center; 
    color: #60A5FA; 
    margin-bottom: 30px;
}
.card-centro { 
    background: white;
    padding: 25px;
    border-radius: 20px; 
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.12); 
    border-left: 12px solid #0060D0;
    position: relative;
}
.numero-canto {
    position: absolute;
    top: 10px;
    right: 15px;
    background: rgba(255,255,255,0.9);
    border-radius: 50%;
    width: 30px;
    height: 30px;
    font-size: 12px;
    font-weight: bold;
    color: #60A5FA;
    display: flex;
    align-items: center;
    justify-content: center;
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
.data-pequena {
    font-size: 11px !important;
    color: #6B7280 !important;
    font-style: italic !important;
}
.participante-linha {
    display: flex;
    align-items: center;
    gap: 15px;
    margin: 8px 0;
    padding: 12px;
    background: #f8fafc;
    border-radius: 8px;
    border-left: 4px solid #3B82F6;
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
        <div class="numero-canto">#{index}</div>
        <div style="color: #1E3A8A; font-size: 22px; font-weight: 800;">{nome} 🕊️</div>
        {"<div style='color: #3B82F6; font-style: italic;'>" + fantasia + "</div>" if fantasia else ""}
        <div style="color:#065F46; font-weight:700; background:#D1FAE5; padding:8px; border-radius:8px; margin:10px 0;">🗣️ PALESTRA: {palestra}</div>
        <div style="margin:5px 0;">👤 <b>Responsável:</b> {responsavel}</div>
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
    st.markdown("<div class='titulo-grande'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🚪 Entrar", "✨ Cadastrar"])
    
    with tab1:
        with st.form("login"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                st.session_state["logado"] = True
                st.rerun()
    
    with tab2:
        with st.form("cadastro"):
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Cadastrar", use_container_width=True):
                try:
                    # SALVA NA TABELA "participantes" DO SUPABASE
                    supabase.table("participantes").insert({
                        "nome": nome,
                        "email": email,
                        "status": "ativo",
                        "created_at": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
                    }).execute()
                    st.session_state["logado"] = True
                    st.success("✅ Cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro Supabase: {e}")

else:
    pagina = st.session_state.get("pagina")

    if pagina is None:
        st.markdown("<div class='titulo-grande'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔎 Busca Avançada", use_container_width=True): 
                st.session_state["pagina"] = "pesquisar"; st.rerun()
            if st.button("📍 Por Cidade", use_container_width=True): 
                st.session_state["pagina"] = "cidade"; st.rerun()
        with c2:
            if st.button("📊 Admin", use_container_width=True): 
                st.session_state["pagina"] = "admin"
                st.session_state["admin_logado"] = False
                st.rerun()
            if st.button("🕊️ Frases", use_container_width=True): 
                st.session_state["pagina"] = "frases"; st.rerun()
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear(); st.rerun()

    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ VOLTAR", use_container_width=True): 
                st.session_state["pagina"] = None; st.rerun()
        with col2:
            if st.button("🔄 LIMPAR", use_container_width=True): 
                st.session_state["termo_pesquisa"] = ""; st.rerun()

        if pagina == "pesquisar":
            st.header("🔎 Busca Avançada")
            termo = st.text_input("Digite o que busca:", value=st.session_state["termo_pesquisa"])
            if termo and len(termo.strip()) >= 3:
                st.session_state["termo_pesquisa"] = termo
                df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
                df.columns = df.columns.str.strip()
                t_norm = normalize_text(termo.strip())
                res = df[df.apply(lambda r: t_norm in normalize_text(" ".join(r.astype(str))), axis=1)]
                if not res.empty:
                    st.success(f"✅ {len(res)} centro(s) encontrado(s)")
                    for i, (_, row) in enumerate(res.iterrows(), 1):
                        renderizar_card(row, i)
                else:
                    st.warning("❌ Nada encontrado.")

        elif pagina == "cidade":
            st.header("📍 Por Cidade")
            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            df.columns = df.columns.str.strip()
            cidades_com_contagem = [f"{c} ({len(df[df['CIDADE DO CENTRO ESPIRITA']==c])})" for c in sorted(df["CIDADE DO CENTRO ESPIRITA"].dropna().unique())]
            escolha = st.selectbox("Selecione uma cidade:", ["-- Selecione --"] + cidades_com_contagem)
            if escolha != "-- Selecione --":
                cidade_real = escolha.split(" (")[0]
                res = df[df["CIDADE DO CENTRO ESPIRITA"] == cidade_real]
                for i, (_, row) in enumerate(res.iterrows(), 1):
                    renderizar_card(row, i)

        elif pagina == "admin":
            # ADMIN LOGIN
            if not st.session_state.get("admin_logado", False):
                st.header("🔐 Admin - Login")
                col_admin1, col_admin2 = st.columns(2)
                with col_admin1:
                    usuario_admin = st.text_input("Usuário", placeholder="estudantesabio")
                with col_admin2:
                    senha_admin = st.text_input("Senha", type="password", placeholder="2026")
                if st.button("🔑 Entrar Admin", use_container_width=True):
                    if usuario_admin == "estudantesabio" and senha_admin == "2026":
                        st.session_state["admin_logado"] = True
                        st.success("✅ Admin logado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos!")
            else:
                # DASHBOARD ADMIN - SUA TABELA "participantes"
                st.header("📊 Participantes Cadastrados")
                try:
                    res = supabase.table("participantes").select("*").order("created_at", desc=True).execute()
                    participantes = res.data
                    if participantes:
                        st.info(f"**Total: {len(participantes)} participantes**")
                        
                        # LISTA HORIZONTAL: 1. Nome, email (data/hora)
                        for i, p in enumerate(participantes, 1):
                            created_at = p.get("created_at", "")
                            if created_at:
                                # Converte timestamp Supabase para BR
                                data_br = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                data_br = data_br.astimezone(datetime.timezone(datetime.timedelta(hours=-3)))
                                data_fmt = data_br.strftime("%d/%m/%Y - %H:%M:%S")
                            else:
                                data_fmt = "-"
                            
                            st.markdown(f"""
                            <div class="participante-linha">
                                <span style="font-weight: bold; font-size: 14px;">{i}.</span>
                                <span style="font-weight: 500;">{p.get('nome', 'N/D')}</span>
                                <span>{p.get('email', 'N/D')}</span>
                                <span class="data-pequena">({data_fmt})</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if st.button("🔐 Sair Admin", use_container_width=True):
                            st.session_state["admin_logado"] = False
                            st.rerun()
                    else:
                        st.info("Nenhum participante cadastrado.")
                except Exception as e:
                    st.error(f"❌ Erro Supabase: {str(e)[:100]}")
                    st.info("🔧 Verifique: 1) Credenciais 2) Tabela 'participantes' existe")

        elif pagina == "frases":
            st.header("🕊️ Frases Inspiradoras")
            st.info("**Fora da caridade não há salvação. — Allan Kardec**")
