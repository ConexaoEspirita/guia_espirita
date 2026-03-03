import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import datetime
from supabase import create_client, Client
import sendgrid
from sendgrid.helpers.mail import Mail

# ==============================
# SUPABASE + SENDGRID
# ==============================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Guia Espírita", layout="wide")

# ==============================
# SESSION STATE
# ==============================
if "pagina" not in st.session_state: st.session_state["pagina"] = None
if "logado" not in st.session_state: st.session_state["logado"] = False
if "termo_pesquisa" not in st.session_state: st.session_state["termo_pesquisa"] = ""
if "email_logado" not in st.session_state: st.session_state["email_logado"] = None

# ==============================
# CSS
# ==============================
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

# ==============================
# EMAIL
# ==============================
def enviar_email_confirmacao(email, acao="login"):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

    if acao == "login":
        assunto = "Login realizado - Guia Espírita"
        mensagem = f"Login em {datetime.datetime.now().strftime('%H:%M %d/%m/%Y')}"
    else:
        assunto = "Cadastro confirmado - Guia Espírita"
        mensagem = "Seu cadastro foi realizado com sucesso."

    email_msg = Mail(
        from_email='bMEFBOVESPA2017@gmail.com',
        to_emails=email,
        subject=assunto,
        plain_text_content=mensagem
    )

    try:
        sg.send(email_msg)
    except:
        pass

# ==============================
# FUNÇÕES AUX
# ==============================
def ajustar(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def normalize_text(text):
    if pd.isna(text): return ""
    return unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8').lower()

def renderizar_card(row, index):
    nome = ajustar(row.get('NOME', 'Centro Espírita'))
    cidade = ajustar(row.get('CIDADE DO CENTRO ESPIRITA'))
    endereco = ajustar(row.get('ENDERECO'))
    celular = ajustar(row.get('CELULAR'))

    numero = "".join(filter(str.isdigit, celular))
    link_wa = f"https://wa.me/+55{numero}" if len(numero) >= 10 else "#"

    texto_busca = f"{endereco}, {cidade}" if endereco else cidade
    query = urllib.parse.quote(texto_busca.strip())
    link_maps = f"https://www.google.com/maps/search/?api=1&query={query}"

    st.markdown(f"""
<div class="card-centro">
<div style="position:absolute; top:10px; right:15px; font-size:12px;">#{index}</div>
<div style="color: #1E3A8A; font-size: 22px; font-weight: 800;">{nome} 🕊️</div>
<div>🏙️ {cidade}</div>
<div>📍 {endereco}</div>
<div style="margin-top:15px; display:flex; gap:10px;">
<a href="{link_maps}" target="_blank" class="btn-link" style="background:#4285F4;">Maps</a>
<a href="{link_wa}" target="_blank" class="btn-link" style="background:#25D366;">WhatsApp</a>
</div>
</div>
""", unsafe_allow_html=True)

# ==============================
# LOGIN / CADASTRO
# ==============================
if not st.session_state["logado"]:

    st.markdown("## 🕊️ Guia Espírita")

    t1, t2 = st.tabs(["Entrar", "Cadastrar"])

    # LOGIN
    with t1:
        with st.form("login"):
            em = st.text_input("E-mail")
            se = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):

                em = em.strip()
                se = se.strip()

                users = supabase.table("participantes").select("*").eq("email", em).execute()

                if users.data:
                    user = users.data[0]

                    senha_bd = str(user.get("senha", "")).strip()

                    if senha_bd == se:

                        supabase.table("participantes").update({
                            "status": "online",
                            "ultimo_acesso": datetime.datetime.now().isoformat()
                        }).eq("email", em).execute()

                        st.session_state["logado"] = True
                        st.session_state["email_logado"] = em

                        enviar_email_confirmacao(em, "login")

                        st.success("Login realizado!")
                        st.rerun()
                    else:
                        st.error("Senha incorreta.")
                else:
                    st.error("E-mail não cadastrado.")

    # CADASTRO
    with t2:
        with st.form("cadastro"):
            n_c = st.text_input("Nome completo")
            e_c = st.text_input("E-mail")
            s_c = st.text_input("Senha", type="password")
            if st.form_submit_button("Cadastrar"):

                n_c = n_c.strip()
                e_c = e_c.strip()
                s_c = s_c.strip()

                if not n_c or not e_c or not s_c:
                    st.warning("Preencha todos os campos.")
                elif len(s_c) < 3:
                    st.warning("Senha mínimo 3 caracteres.")
                else:
                    check = supabase.table("participantes").select("*").eq("email", e_c).execute()

                    if check.data:
                        st.error("E-mail já cadastrado.")
                    else:
                        supabase.table("participantes").insert({
                            "nome": n_c,
                            "email": e_c,
                            "senha": s_c,
                            "status": "ausente",
                            "ultimo_acesso": None
                        }).execute()

                        enviar_email_confirmacao(e_c, "cadastro")

                        st.success("Cadastro realizado!")
                        st.rerun()

# ==============================
# ÁREA LOGADA
# ==============================
else:

    ag_br = datetime.datetime.now() - datetime.timedelta(hours=3)

    st.markdown(f"<b>{ag_br.strftime('%H:%M')} - {ag_br.strftime('%d/%m/%Y')}</b>", unsafe_allow_html=True)

    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()

    pag = st.session_state.get("pagina")

    if pag is None:

        if st.button("Busca Avançada"): st.session_state["pagina"] = "pesquisar"; st.rerun()
        if st.button("Por Cidade"): st.session_state["pagina"] = "cidade"; st.rerun()
        if st.button("Admin"): st.session_state["pagina"] = "admin"; st.rerun()
        if st.button("Frases"): st.session_state["pagina"] = "frases"; st.rerun()

        if st.button("Sair"):
            supabase.table("participantes").update({"status": "ausente"}).eq("email", st.session_state["email_logado"]).execute()
            st.session_state.clear()
            st.rerun()

    elif pag == "pesquisar":
        termo = st.text_input("Buscar:")
        if termo and len(termo.strip()) >= 3:
            t_norm = normalize_text(termo)
            res = df[df.apply(lambda r: t_norm in normalize_text(" ".join(r.astype(str))), axis=1)]
            for i, (_, row) in enumerate(res.iterrows(), 1):
                renderizar_card(row, i)

    elif pag == "cidade":
        cidades = sorted(df["CIDADE DO CENTRO ESPIRITA"].dropna().unique())
        sel = st.selectbox("Cidade:", cidades)
        res = df[df["CIDADE DO CENTRO ESPIRITA"] == sel]
        for i, (_, row) in enumerate(res.iterrows(), 1):
            renderizar_card(row, i)

    elif pag == "admin":
        senha_admin = st.text_input("Senha Admin", type="password")
        if senha_admin == "estudantesabio2026":
            users_data = supabase.table("participantes").select("*").execute().data
            st.write("Usuários cadastrados:", len(users_data))
            for u in users_data:
                st.write(u["nome"], "-", u["email"], "-", u["status"])

    elif pag == "frases":
        st.info("Embora ninguém possa voltar atrás e fazer um novo começo, qualquer um pode começar agora e fazer um novo fim. — Chico Xavier")
