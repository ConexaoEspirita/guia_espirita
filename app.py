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

# ================= CSS (MANTIDO ORIGINAL) =================
st.markdown("""
<style>
#MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
[data-testid="stStatusWidget"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
.stApp { background: #f4f7f9; }
.titulo-grande { font-size: 32px; font-weight: 800; margin-bottom: 8px; }
.card-centro { background: white; padding: 25px; border-radius: 20px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.12); border-left: 12px solid #0060D0; position: relative; }
.btn-link { text-decoration:none; color:white !important; padding:10px; border-radius:10px; font-weight:700; text-align:center; display:inline-block; width: 100%; }
.admin-linha-info { display: flex; gap: 15px; font-size: 13px; font-weight: 700; color: #1E3A8A; margin-bottom: 15px; border-bottom: 2px solid #0060D0; padding-bottom: 10px; flex-wrap: wrap; }
.status-bola { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
</style>
""", unsafe_allow_html=True)

# ================= FUNÇÕES DE APOIO (MANTIDAS) =================
def ajustar(txt): return str(txt).strip() if pd.notna(txt) else ""
def normalize_text(text):
    if pd.isna(text): return ""
    return unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8').lower()

# 

# ================= NOVO: SISTEMA DE PULSAÇÃO (HEARTBEAT) =================
def registrar_pulso():
    """Atualiza o 'visto por último' do usuário logado no Supabase"""
    if st.session_state.get("logado") and st.session_state.get("usuario_email"):
        agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            supabase.table("participantes").update({"last_seen": agora}).eq("email", st.session_state["usuario_email"]).execute()
        except:
            pass

def renderizar_card(row, index):
    # --- SEU CÓDIGO DE RENDERIZAÇÃO DE CARD ORIGINAL AQUI (Mantido 100%) ---
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

def enviar_email(destinatario, codigo):
    # --- SEU CÓDIGO DE ENVIO DE EMAIL ORIGINAL ---
    smtp_user = st.secrets["EMAIL_USER"]
    smtp_pass = st.secrets["EMAIL_PASS"]
    msg = MIMEText(f"Seu código de confirmação para o Guia Espírita é: {codigo}")
    msg["Subject"] = "Código de Confirmação - Guia Espírita"
    msg["From"] = smtp_user
    msg["To"] = destinatario
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, destinatario, msg.as_string())
        server.quit()
        return True
    except: return False

# ================= LOGIN / CADASTRO (LÓGICA AJUSTADA) =================
if not st.session_state.get("logado", False):
    st.markdown("<div style='text-align: center; color: #60A5FA; font-size: 32px; font-weight: 800; margin-bottom: 30px;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🚪 Entrar", "✨ Cadastrar", "✉️ Confirmar e-mail"])
    
    with t1:
        with st.form("login"):
            email_login = st.text_input("E-mail")
            senha_login = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                res = supabase.table("participantes").select("*").eq("email", email_login).execute().data
                if res:
                    user = res[0]
                    if not user["confirmado"]: st.warning("⚠️ Confirme seu e-mail primeiro.")
                    elif user["senha"] == senha_login:
                        # REGISTRA HORA DO LOGIN
                        agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
                        supabase.table("participantes").update({"last_login": agora, "last_seen": agora}).eq("email", email_login).execute()
                        st.session_state["logado"] = True
                        st.session_state["usuario_email"] = email_login
                        st.success("✅ Bem-vindo!")
                        st.rerun()
                    else: st.error("❌ Senha incorreta.")
                else: st.error("❌ Usuário não encontrado.")

    with t2:
        with st.form("cadastro"):
            n_c = st.text_input("Nome")
            e_c = st.text_input("E-mail")
            s_c = st.text_input("Senha", type="password")
            if st.form_submit_button("Cadastrar", use_container_width=True):
                if n_c and e_c and s_c:
                    codigo = str(random.randint(100000, 999999))
                    if enviar_email(e_c, codigo):
                        supabase.table("participantes").insert({"nome": n_c, "email": e_c, "senha": s_c, "confirmado": False, "codigo_confirmacao": codigo}).execute()
                        st.success("✅ Verifique seu e-mail!")
    
    with t3:
        with st.form("confirmacao"):
            email_conf = st.text_input("E-mail")
            codigo_conf = st.text_input("Código")
            if st.form_submit_button("Confirmar", use_container_width=True):
                res = supabase.table("participantes").select("*").eq("email", email_conf).execute().data
                if res and res[0]["codigo_confirmacao"] == codigo_conf:
                    supabase.table("participantes").update({"confirmado": True}).eq("email", email_conf).execute()
                    st.success("✅ Confirmado! Pode logar.")

# ================= APP LOGADO =================
else:
    registrar_pulso() # ATUALIZA O STATUS ONLINE A CADA CLIQUE
    ag_br = datetime.datetime.now() - datetime.timedelta(hours=3)
    
    st.markdown(f'<div style="display:flex;align-items:center;gap:15px;margin-bottom:20px;"><span style="font-weight:800;color:#1E3A8A;">{ag_br.strftime("%H:%M")}</span><span style="font-weight:800;color:#1E3A8A;">{ag_br.strftime("%d/%m/%Y")}</span><hr style="flex-grow:1;border:none;border-top:1px solid #ccc;margin:0;"></div>', unsafe_allow_html=True)

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
            # TRAVA DE SEGURANÇA NO MENU ADMIN
            if st.session_state["usuario_email"] == "bmefbovespa2017@gmail.com":
                if st.button("📊 Admin (Privado)", use_container_width=True): st.session_state["pagina"] = "admin"; st.rerun()
            if st.button("🕊️ Frases", use_container_width=True): st.session_state["pagina"] = "frases"; st.rerun()
        if st.button("🚪 Sair", use_container_width=True): st.session_state.clear(); st.rerun()

    elif pag == "admin":
        if st.session_state["usuario_email"] != "bmefbovespa2017@gmail.com":
            st.error("Acesso negado.")
            st.session_state["pagina"] = None
            st.rerun()
            
        # --- CÁLCULO DE ONLINE / AUSENTE ---
        agora_utc = datetime.datetime.now(datetime.timezone.utc)
        limite_online = agora_utc - datetime.timedelta(minutes=5)
        limite_dia = agora_utc - datetime.timedelta(hours=24)
        
        users_data = supabase.table("participantes").select("*").execute().data
        
        online = 0
        ausente = 0
        tabela_horizontal = []

        for u in users_data:
            last_seen_str = u.get("last_seen")
            if last_seen_str:
                last_seen = datetime.datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                if last_seen > limite_online:
                    status = "🟢 Online"
                    online += 1
                elif last_seen > limite_dia:
                    status = "🟠 Ausente"
                    ausente += 1
                else:
                    status = "⚪ Inativo"
            else: status = "⚪ -"; 

            tabela_horizontal.append({
                "Nome": u["nome"],
                "E-mail": u["email"],
                "Último Login": u.get("last_login", "-")[:16].replace("T", " "),
                "Status": status
            })

        st.markdown(f'<div class="admin-linha-info"><span>Centros: {len(df)}</span> | <span>📱 Online: {online}</span> | <span>🟠 Ausentes (24h): {ausente}</span> | <span>👥 Total Cadastros: {len(users_data)}</span></div>', unsafe_allow_html=True)
        
        st.write("### 👥 Relatório Detalhado de Acessos")
        st.table(pd.DataFrame(tabela_horizontal)) # Tabela horizontal limpa
        
        if st.button("⬅️ VOLTAR"): st.session_state["pagina"] = None; st.rerun()

    # --- RESTANTE DO CÓDIGO (PESQUISAR, CIDADE, FRASES) MANTIDO IGUAL ---
    elif pag == "pesquisar":
        # ... (seu código original de pesquisa aqui)
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
