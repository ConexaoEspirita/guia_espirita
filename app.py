import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import datetime
from supabase import create_client, Client
import sendgrid
from sendgrid.helpers.mail import Mail

# SUPABASE + SENDGRID
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Guia Espírita", layout="wide")

# SESSION STATE
if "pagina" not in st.session_state: st.session_state["pagina"] = None
if "logado" not in st.session_state: st.session_state["logado"] = False
if "termo_pesquisa" not in st.session_state: st.session_state["termo_pesquisa"] = ""
if "email_logado" not in st.session_state: st.session_state["email_logado"] = None

# CSS
st.markdown("""
<style>
#MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
[data-testid="stStatusWidget"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
.stApp { background: #f4f7f9; }
.titulo-grande { font-size: 32px; font-weight: 800; margin-bottom: 8px; }
.card-centro { background: white; padding: 25px; border-radius: 20px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.12); border-left: 12px solid #0060D0; position: relative; }
.btn-link { text-decoration:none; color:white !important; padding:10px; border-radius:10px; font-weight:700; text-align:center; display:inline-block; width: 100%; }
.admin-linha-info { display: flex; gap: 15px; font-size: 13px; font-weight: 700; color: #1E3A8A; margin-bottom: 15px; border-bottom: 2px solid #0060D0; padding-bottom: 10px; flex-wrap: wrap; }
.admin-reg { font-size: 11px; border-bottom: 1px solid #eee; padding: 4px 0; display: flex; justify-content: space-between; }
</style>
""", unsafe_allow_html=True)

# EMAIL
def enviar_email_confirmacao(email, acao="login"):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

    if acao == "login":
        assunto = "🕊️ Bem-vindo ao Guia Espírita!"
        mensagem = f"""
Olá! Você acaba de entrar no Guia Espírita às {datetime.datetime.now().strftime("%H:%M %d/%m/%Y")}.
🙏 Gratidão! Equipe Guia Espírita
"""
    else:
        assunto = "✅ Cadastro confirmado!"
        mensagem = f"""
Seu cadastro foi confirmado com sucesso!

Email: {email}

🕊️ Paz e Luz!
"""

    email_msg = Mail(
        from_email='bMEFBOVESPA2017@gmail.com',
        to_emails=email,
        subject=assunto,
        plain_text_content=mensagem
    )

    try:
        sg.send(email_msg)
        return True
    except:
        return False

def ajustar(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def normalize_text(text):
    if pd.isna(text): return ""
    return unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8').lower()

# LOGIN + CADASTRO
if not st.session_state.get("logado", False):

    st.markdown("<div style='text-align: center; color: #60A5FA; font-size: 32px; font-weight: 800; margin-bottom: 30px;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🚪 Entrar", "✨ Cadastrar"])

    with t1:
        with st.form("login"):
            em = st.text_input("📧 E-mail")
            se = st.text_input("🔑 Senha", type="password")
            if st.form_submit_button("🚀 Entrar", use_container_width=True):
                users = supabase.table("participantes").select("*").eq("email", em).execute()
                if users.data:
                    user = users.data[0]
                    if user.get('senha') == se:
                        supabase.table("participantes").update({
                            "status": "online",
                            "ultimo_acesso": datetime.datetime.now().strftime("%d-%m-%Y - %Hh%M:%Ss")
                        }).eq("email", em).execute()
                        st.session_state["logado"] = True
                        st.session_state["email_logado"] = em
                        st.rerun()
                    else:
                        st.error("❌ SENHA INCORRETA!")
                else:
                    st.error("❌ E-mail não cadastrado!")

    with t2:
        with st.form("cadastro"):
            n_c = st.text_input("👤 Nome completo")
            e_c = st.text_input("📧 E-mail")
            s_c = st.text_input("🔑 Senha", type="password")
            submitted = st.form_submit_button("✅ Cadastrar", use_container_width=True)

            if submitted and n_c and e_c and s_c and len(s_c) >= 3:
                check = supabase.table("participantes").select("*").eq("email", e_c).execute()
                if check.data:
                    st.error("❌ E-mail JÁ CADASTRADO!")
                else:
                    agora_br = datetime.datetime.now() - datetime.timedelta(hours=3)
                    data_formatada = agora_br.strftime("%d-%m-%Y - %Hh%M:%Ss")

                    supabase.table("participantes").insert({
                        "nome": n_c.strip(),
                        "email": e_c.strip(),
                        "senha": s_c,
                        "status": "ausente",
                        "ultimo_acesso": None,
                        "created_at": data_formatada
                    }).execute()

                    st.success("✅ CADASTRO CONCLUÍDO!")
                    st.rerun()

else:
    ag_br = datetime.datetime.now() - datetime.timedelta(hours=3)

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:15px;margin-bottom:20px;">
    <span style="font-weight:800;color:#1E3A8A;">{ag_br.strftime("%H:%M")}</span>
    <span style="font-weight:800;color:#1E3A8A;">{ag_br.strftime("%d/%m/%Y")}</span>
    <hr style="flex-grow:1;border:none;border-top:1px solid #ccc;margin:0;"></div>
    """, unsafe_allow_html=True)

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
            if st.button("📊 Admin", use_container_width=True): st.session_state["pagina"] = "admin"; st.rerun()
            if st.button("🕊️ Frases", use_container_width=True): st.session_state["pagina"] = "frases"; st.rerun()

        if st.button("🚪 Sair", use_container_width=True):
            supabase.table("participantes").update({"status": "ausente"}).eq("email", st.session_state["email_logado"]).execute()
            st.session_state.clear()
            st.rerun()

    else:
        if st.button("⬅️ VOLTAR"): st.session_state["pagina"] = None; st.rerun()

        if pag == "frases":
            st.info('"Embora ninguém possa voltar atrás e fazer um novo começo, qualquer um pode começar agora e fazer um novo fim." — **Chico Xavier**')
