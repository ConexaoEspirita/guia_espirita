import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import datetime
import random
import smtplib
from email.mime.text import MIMEText
from supabase import create_client, Client

# ================= SUPABASE =================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= CONFIGURAÇÃO DO APP =================
st.set_page_config(page_title="Guia Espírita", layout="wide")

# ================= SESSION STATE =================
if "pagina" not in st.session_state: st.session_state["pagina"] = None
if "logado" not in st.session_state: st.session_state["logado"] = False
if "usuario_email" not in st.session_state: st.session_state["usuario_email"] = ""
if "termo_pesquisa" not in st.session_state: st.session_state["termo_pesquisa"] = ""

# ================= CSS (SEU VISUAL ORIGINAL) =================
st.markdown("""
<style>
#MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
[data-testid="stStatusWidget"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
.stApp { background: #f4f7f9; }
.titulo-grande { font-size: 32px; font-weight: 800; margin-bottom: 8px; }
.card-centro { background: white; padding: 25px; border-radius: 20px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.12); border-left: 12px solid #0060D0; position: relative; }
.btn-link { text-decoration:none; color:white !important; padding:10px; border-radius:10px; font-weight:700; text-align:center; display:inline-block; width: 100%; }
.admin-linha-info { display: flex; gap: 15px; font-size: 13px; font-weight: 700; color: #1E3A8A; margin-bottom: 15px; border-bottom: 2px solid #0060D0; padding-bottom: 10px; flex-wrap: wrap; }
</style>
""", unsafe_allow_html=True)

# ================= FUNÇÕES DE APOIO (MANTIDAS) =================
def ajustar(txt): return str(txt).strip() if pd.notna(txt) else ""
def normalize_text(text):
    if pd.isna(text): return ""
    return unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8').lower()

def registrar_pulso():
    if st.session_state.get("logado") and st.session_state.get("usuario_email"):
        agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            supabase.table("participantes").update({"last_seen": agora}).eq("email", st.session_state["usuario_email"]).execute()
        except: pass

def renderizar_card(row, index):
    nome = ajustar(row.get('NOME', 'Centro Espírita'))
    fantasia = ajustar(row.get('NOME FANTASIA'))
    endereco = ajustar(row.get('ENDERECO'))
    cidade = ajustar(row.get('CIDADE DO CENTRO ESPIRITA'))
    palestra = ajustar(row.get('PALESTRA PUBLICA'))
    responsavel = ajustar(row.get('RESPONSAVEL'))
    celular = ajustar(row.get('CELULAR'))
    numero = "".join(filter(str.isdigit, celular))
    link_wa = f"https://wa.me/+55{numero}" if len(numero) >= 10 else "#"
    query = urllib.parse.quote(f"{endereco}, {cidade}".strip())
    link_maps = f"https://www.google.com/maps/search/?api=1&query={query}"

    st.markdown(f"""
    <div class="card-centro">
        <div style="position:absolute; top:10px; right:15px; font-size:12px; color:#6B7280; background:rgba(255,255,255,0.8); padding:2px 6px; border-radius:12px; font-weight:500;">#{index}</div>
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

# ================= FUNÇÃO DE EMAIL (FIXED SENDGRID) =================
def enviar_email(destinatario, codigo):
    try:
        api_key = st.secrets["SENDGRID_API_KEY"]
        remetente = st.secrets["EMAIL_REMETENTE"]
        
        msg = MIMEText(f"Seu código de confirmação para o Guia Espírita é: {codigo}")
        msg["Subject"] = "Código de Confirmação - Guia Espírita"
        msg["From"] = remetente
        msg["To"] = destinatario

        server = smtplib.SMTP_SSL("smtp.sendgrid.net", 465)
        server.login("apikey", api_key) 
        server.sendmail(remetente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Erro no e-mail: {e}")
        return False

# ================= LOGIN / CADASTRO =================
if not st.session_state.get("logado", False):
    st.markdown("<div style='text-align: center; color: #60A5FA; font-size: 32px; font-weight: 800; margin-bottom: 30px;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🚪 Entrar", "✨ Cadastrar", "✉️ Confirmar"])
    
    with t1:
        with st.form("login"):
            email_login = st.text_input("E-mail")
            senha_login = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                res = supabase.table("participantes").select("*").eq("email", email_login).execute().data
                if res and res[0]["senha"] == senha_login:
                    if not res[0]["confirmado"]: st.warning("Confirme seu e-mail.")
                    else:
                        agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
                        supabase.table("participantes").update({"last_login": agora}).eq("email", email_login).execute()
                        st.session_state["logado"] = True
                        st.session_state["usuario_email"] = email_login
                        st.rerun()
                else: st.error("E-mail ou senha incorretos.")

    with t2:
        with st.form("cadastro"):
            n_c = st.text_input("Nome")
            e_c = st.text_input("E-mail")
            s_c = st.text_input("Senha", type="password")
            if st.form_submit_button("Cadastrar", use_container_width=True):
                codigo = str(random.randint(100000, 999999))
                if enviar_email(e_c, codigo):
                    supabase.table("participantes").insert({"nome": n_c, "email": e_c, "senha": s_c, "confirmado": False, "codigo_confirmacao": codigo}).execute()
                    st.success("Verifique seu e-mail!")

    with t3:
        with st.form("conf"):
            ec = st.text_input("E-mail")
            cc = st.text_input("Código")
            if st.form_submit_button("Confirmar"):
                res = supabase.table("participantes").select("*").eq("email", ec).execute().data
                if res and res[0]["codigo_confirmacao"] == cc:
                    supabase.table("participantes").update({"confirmado": True}).eq("email", ec).execute()
                    st.success("Conta ativada!")

# ================= APP LOGADO =================
else:
    registrar_pulso()
    ag_br = datetime.datetime.now() - datetime.timedelta(hours=3)
    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()
    pag = st.session_state.get("pagina")

    if pag is None:
        st.markdown("<div class='titulo-grande' style='color: #60A5FA; text-align: center;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔎 Busca Avançada", use_container_width=True): st.session_state["pagina"] = "pesquisar"; st.rerun()
            if st.button("📍 Por Cidade", use_container_width=True): st.session_state["pagina"] = "cidade"; st.rerun()
        with c2:
            if st.session_state["usuario_email"] == "bmefbovespa2017@gmail.com":
                if st.button("📊 Admin", use_container_width=True): st.session_state["pagina"] = "admin"; st.rerun()
            if st.button("🕊️ Frases", use_container_width=True): st.session_state["pagina"] = "frases"; st.rerun()
        if st.button("🚪 Sair", use_container_width=True): st.session_state.clear(); st.rerun()

    elif pag == "admin":
        st.write("### 👥 Gestão de Acessos")
        users_data = supabase.table("participantes").select("*").execute().data
        tab_admin = []
        for u in users_data:
            tab_admin.append({
                "Nome": u["nome"], "E-mail": u["email"], 
                "Último Login": u.get("last_login", "-")[:16].replace("T", " "),
                "Confirmado": "✅" if u["confirmado"] else "❌"
            })
        st.table(pd.DataFrame(tab_admin))
        if st.button("⬅️ VOLTAR"): st.session_state["pagina"] = None; st.rerun()

    elif pag == "pesquisar":
        termo = st.text_input("Digite o que busca:", value=st.session_state["termo_pesquisa"])
        if st.button("⬅️ VOLTAR"): st.session_state["pagina"] = None; st.rerun()
        if termo and len(termo.strip()) >= 3:
            t_norm = normalize_text(termo.strip())
            res = df[df.apply(lambda r: t_norm in normalize_text(" ".join(r.astype(str))), axis=1)]
            for i, (_, row) in enumerate(res.iterrows(), 1): renderizar_card(row, i)

    elif pag == "cidade":
        if st.button("⬅️ VOLTAR"): st.session_state["pagina"] = None; st.rerun()
        cids = sorted(df["CIDADE DO CENTRO ESPIRITA"].dropna().unique())
        sel = st.selectbox("Selecione:", ["-- Selecione --"] + cids)
        if sel != "-- Selecione --":
            res = df[df["CIDADE DO CENTRO ESPIRITA"] == sel]
            for i, (_, row) in enumerate(res.iterrows(), 1): renderizar_card(row, i)

    elif pag == "frases":
        if st.button("⬅️ VOLTAR"): st.session_state["pagina"] = None; st.rerun()
        st.info('"Embora ninguém possa voltar atrás e fazer um novo começo, qualquer um pode começar agora e fazer um novo fim." — **Chico Xavier**')
