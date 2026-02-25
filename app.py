import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

st.set_page_config(page_title="Guia Espirita", page_icon="🕊️", layout="wide")

st.markdown("""
<style>
.block-container {padding-top:0rem!important;padding-right:0!important;padding-left:0!important;margin:0!important;}
[data-testid="stDecoration"] {display:none!important;}
.stApp>div>div {background:transparent!important;}
.stApp {background:linear-gradient(135deg,#EBF4FA 0%,#D4E8F7 100%);}
.titulo-premium {background:linear-gradient(90deg,#0047AB,#1976D2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-shadow:0 4px 12px rgba(0,71,171,0.3);font-size:2.8rem!important;font-weight:800!important;margin:0;line-height:1.1!important;text-align:center;}
.login-title {font-size:2.8rem!important;font-weight:800!important;color:#1E3A8A!important;text-align:center;margin-bottom:20px;line-height:1.1!important;}
.card-centro {background:rgba(255,255,255,0.95);backdrop-filter:blur(10px);padding:20px;border-radius:20px;border:1px solid rgba(0,71,171,0.1);box-shadow:0 8px 32px rgba(0,71,171,0.15);margin-bottom:16px;}
.nome-grande {color:#1E3A8A!important;font-size:22px!important;font-weight:800!important;}
.nome-fantasia {color:#3B82F6!important;font-size:15px!important;font-weight:600!important;font-style:italic;}
.info-texto {color:#374151!important;font-size:13px!important;display:flex;align-items:center;gap:6px;}
.palestras-verde {color:#10B981!important;font-weight:700!important;font-size:14px!important;background:rgba(16,185,129,0.15)!important;padding:8px 14px!important;border-radius:12px!important;border-left:4px solid #10B981!important;box-shadow:0 2px 8px rgba(16,185,129,0.2)!important;}
div.stButton>button {background:linear-gradient(135deg,#0047AB,#1E40AF)!important;color:white!important;border-radius:12px!important;height:50px!important;font-size:16px!important;font-weight:700!important;box-shadow:0 4px 12px rgba(0,71,171,0.4)!important;transition:all 0.2s!important;}
div.stButton>button:hover {box-shadow:0 6px 20px rgba(0,71,171,0.6)!important;transform:translateY(-2px)!important;}
div.stButton>button:active {transform:translateY(0px)!important;box-shadow:0 2px 8px rgba(0,71,171,0.3)!important;}
.login-container {max-width:450px;margin:20px auto;padding:30px;background:rgba(255,255,255,0.95);backdrop-filter:blur(10px);border-radius:20px;border:1px solid rgba(0,71,171,0.1);box-shadow:0 8px 32px rgba(0,71,171,0.15);}
input[type="text"], input[type="password"] {height:45px!important;font-size:15px!important;}
</style>
""", unsafe_allow_html=True)

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

if "logado" not in st.session_state: st.session_state.logado = False
if "usuario" not in st.session_state: st.session_state.usuario = None
if "modo" not in st.session_state: st.session_state.modo = "principal"
if "cidade_aberta" not in st.session_state: st.session_state.cidade_aberta = None

def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\\u0300-\\u036f]', '', texto)
    texto = re.sub(r'[^a-zA-Z0-9\\s]', '', texto)
    return texto

if not st.session_state.logado:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🕊️<br>Guia Espirita</div>', unsafe_allow_html=True)
    aba = st.radio("", ["Login", "Cadastro"], horizontal=True)
    if aba == "Login":
        email = st.text_input("", placeholder="📧 Digite seu e-mail", label_visibility="collapsed")
        senha = st.text_input("", placeholder="🔒 Digite sua senha", type="password", label_visibility="collapsed")
        if st.button("🚀 ACESSAR", use_container_width=True):
            if email.strip() and senha.strip():
                resposta = supabase.table("acessos").select("*").eq("email", email.strip().lower()).eq("senha", senha.strip()).execute()
                if resposta.data and len(resposta.data) > 0:
                    st.session_state.logado = True
                    st.session_state.usuario = email.strip().lower()
                    st.rerun()
                else:
                    st.error("❌ E-mail ou senha incorretos!")
            else:
                st.error("❌ Preencha e-mail e senha!")
    else:
        nome = st.text_input("", placeholder="👤 Digite seu nome completo", label_visibility="collapsed")
        email = st.text_input("", placeholder="📧 Digite seu e-mail", label_visibility="collapsed")
        senha = st.text_input("", placeholder="🔒 Crie uma senha", type="password", label_visibility="collapsed")
        senha_conf = st.text_input("", placeholder="🔒 Confirme a senha", type="password", label_visibility="collapsed")
        if st.button("📝 CADASTRAR", use_container_width=True):
            if not nome.strip() or not email.strip() or not senha.strip() or not senha_conf.strip():
                st.error("❌ Todos os campos são obrigatórios!")
            elif senha != senha_conf:
                st.error("❌ Senhas não conferem!")
            else:
                email_limpo = email.strip().lower()
                existe = supabase.table("acessos").select("*").eq("email", email_limpo).execute()
                if existe.data and len(existe.data) > 0:
                    st.error("❌ E-mail já cadastrado!")
                else:
                    supabase.table("acessos").insert({"nome": nome.strip(), "email": email_limpo, "senha": senha}).execute()
                    st.success("✅ Cadastro realizado! Agora faça login.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<h1 class="titulo-premium">🕊️<br>Guia Espirita</h1>', unsafe_allow_html=True)
    
    # MENU ☰ COM 3 OPCOES
    if st.session_state.modo == "principal":
        col1, col2 = st.columns([3,1])
        with col2:
            if st.button("☰ MENU", use_container_width=True):
                st.session_state.modo = "menu"
                st.rerun()
        
        # BUSCA PRINCIPAL
        busca = st.text_input("🔍 Pesquise nome, cidade ou responsável...", label_visibility="collapsed")
        if busca:
            try:
                df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
                df.columns = df.columns.str.strip()
                resultados = []
                for _, row in df.iterrows():
                    texto_total = " ".join([
                        limpar_busca(row.get('NOME','')),
                        limpar_busca(row.get('NOME FANTASIA','')),
                        limpar_busca(row.get('CIDADE DO CENTRO ESPIRITA','')),
                        limpar_busca(row.get('RESPONSAVEL',''))
                    ])
                    if limpar_busca(busca) in texto_total:
                        resultados.append(row)
                
                for i, row in enumerate(resultados, 1):
                    numero = ''.join(filter(str.isdigit, str(row.get('CELULAR',''))))
                    query = urllib.parse.quote(f"{row.get('ENDERECO','')} {row.get('CIDADE DO CENTRO ESPIRITA','')}")
                    st.markdown(f"""
                    <div class="card-centro">
                        <div style="font-size:12px;opacity:0.6;position:absolute;top:10px;right:15px;">{i}</div>
                        <div class="nome-grande">{row.get('NOME','')} 🕊️</div>
                        <div class="nome-fantasia">{row.get('NOME FANTASIA','')}</div>
                        <div class="palestras-verde">🗣️ PALESTRAS {row.get('PALESTRA PUBLICA','')}</div>
                        <div class="info-texto">👤 <b>Responsável:</b> {row.get('RESPONSAVEL','')}</div>
                        <div class="info-texto">📍 <b>Endereço:</b> {row.get('ENDERECO','')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}", use_container_width=True)
                    with col2:
                        if numero:
                            st.link_button("💬 WhatsApp", f"https://wa.me/55{numero}", use_container_width=True)
            except:
                st.error("Erro na busca")
    
    # MENU ☰
    elif st.session_state.modo == "menu":
        st.button("← VOLTAR", use_container_width=True, on_click=lambda: setattr(st.session_state, 'modo', 'principal') or st.rerun())
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🏙️ CIDADES", use_container_width=True):
                st.session_state.modo = "cidades"
                st.rerun()
        with col2:
            if st.button("🔎 BUSCA", use_container_width=True):
                st.session_state.modo = "principal"
                st.rerun()
        with col3:
            if st.button("👨‍💼 ADMIN", use_container_width=True):
                st.info("Área administrativa em desenvolvimento")
    
    # MODO CIDADES
    elif st.session_state.modo == "cidades":
        st.button("← VOLTAR", use_container_width=True, on_click=lambda: setattr(st.session_state, 'modo', 'menu') or st.rerun())
        try:
            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            df.columns = df.columns.str.strip()
            col_cidade = 'CIDADE DO CENTRO ESPIRITA'
            cidades_unicas = sorted(df[col_cidade].dropna().unique())
            for cidade in cidades_unicas:
                total = len(df[df[col_cidade]==cidade])
                if st.button(f"📍 {cidade} ({total})", use_container_width=True):
                    st.session_state.cidade_aberta = cidade
                    st.rerun()
            
            if st.session_state.cidade_aberta:
                st.markdown(f"<h2 style='color:#1E3A8A;text-align:center;'>📍 {st.session_state.cidade_aberta}</h2>", unsafe_allow_html=True)
                centros = df[df[col_cidade]==st.session_state.cidade_aberta]
                for i, row in enumerate(centros.iterrows(), 1):
                    row = row[1]
                    numero = ''.join(filter(str.isdigit, str(row.get('CELULAR',''))))
                    query = urllib.parse.quote(f"{row.get('ENDERECO','')} {st.session_state.cidade_aberta}")
                    st.markdown(f"""
                    <div class="card-centro">
                        <div style="font-size:12px;opacity:0.6;position:absolute;top:10px;right:15px;">{i}</div>
                        <div class="nome-grande">{row.get('NOME','')} 🕊️</div>
                        <div class="nome-fantasia">{row.get('NOME FANTASIA','')}</div>
                        <div class="palestras-verde">🗣️ PALESTRAS {row.get('PALESTRA PUBLICA','')}</div>
                        <div class="info-texto">👤 <b>Responsável:</b> {row.get('RESPONSAVEL','')}</div>
                        <div class="info-texto">📍 <b>Endereço:</b> {row.get('ENDERECO','')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}", use_container_width=True)
                    with col2:
                        if numero:
                            st.link_button("💬 WhatsApp", f"https://wa.me/55{numero}", use_container_width=True)
                if st.button("🔙 Voltar Cidades", use_container_width=True):
                    st.session_state.cidade_aberta = None
                    st.rerun()
        except Exception as e:
            st.error("Erro ao carregar cidades: " + str(e))
