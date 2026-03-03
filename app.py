import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import datetime
from supabase import create_client, Client
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

# --- CONFIGURAÇÕES: SUPABASE + SENDGRID ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Guia Espírita", layout="wide")

# --- FUNÇÃO DE FORMATAÇÃO DE DATA (PEDIDO DO USUÁRIO) ---
def formatar_data_admin(data_iso):
    """Converte ISO do Supabase para o formato: -03-03-2026 - 03h00:30s"""
    try:
        if not data_iso: return ""
        # Limpa milissegundos e caracteres T/Z
        data_limpa = data_iso.split('.')[0].replace('Z', '').replace('T', ' ')
        dt = datetime.datetime.fromisoformat(data_limpa)
        # Formato exato solicitado: -dia-mes-ano - horahmin:segs
        return dt.strftime("-%d-%m-%Y - %Hh%M:%Ss")
    except:
        return data_iso

# --- SESSION STATE ---
if "pagina" not in st.session_state: st.session_state["pagina"] = None
if "logado" not in st.session_state: st.session_state["logado"] = False
if "termo_pesquisa" not in st.session_state: st.session_state["termo_pesquisa"] = ""
if "email_logado" not in st.session_state: st.session_state["email_logado"] = None
if "cadastro_ok" not in st.session_state: st.session_state["cadastro_ok"] = False
if "cadastro_msg" not in st.session_state: st.session_state["cadastro_msg"] = ""

# --- CSS (ESTILIZAÇÃO) ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
[data-testid="stStatusWidget"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
.stApp { background: #f4f7f9; }
.titulo-grande { font-size: 32px; font-weight: 800; margin-bottom: 8px; }
.card-centro { background: white; padding: 25px; border-radius: 20px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.12); border-left: 12px solid #0060D0; position: relative; }
.btn-link { text-decoration:none; color:white !important; padding:10px; border-radius:10px; font-weight:700; text-align:center; display:inline-block; width: 100%; }
.admin-linha-info { display: flex; gap: 15px; font-size: 13px; font-weight: 700; color: #1E3A8A; margin-bottom: 15px; border-bottom: 2px solid #0060D0; padding-bottom: 10px; flex-wrap: wrap; }
.admin-reg { font-size: 11px; border-bottom: 1px solid #eee; padding: 4px 0; display: flex; justify-content: space-between; align-items: center; }
.data-admin-cor { color: #0060D0; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- SENDGRID ---
def enviar_email_confirmacao(email, acao="login"):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    if acao == "login":
        assunto = "🕊️ Bem-vindo ao Guia Espírita!"
        mensagem = f"Olá! Você acaba de entrar no Guia Espírita às {datetime.datetime.now().strftime('%H:%M %d/%m/%Y')}."
    else:
        assunto = "✅ Cadastro confirmado!"
        mensagem = f"Seu cadastro foi confirmado!\n\nUse seu email: {email}\n\nFaça login na aba 'Entrar'."
    
    email_msg = Mail(from_email='bMEFBOVESPA2017@gmail.com', to_emails=email, subject=assunto, plain_text_content=mensagem)
    try:
        sg.send(email_msg)
        return True
    except:
        return False

# --- FUNÇÕES AUXILIARES ---
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
    celular = ajustar(row.get('CELULAR'))
    numero = "".join(filter(str.isdigit, celular))
    link_wa = f"https://wa.me/+55{numero}" if len(numero) >= 10 else "#"
    query = urllib.parse.quote(f"{endereco}, {cidade}".strip())
    link_maps = f"https://www.google.com/maps/search/?api=1&query={query}"

    st.markdown(f"""
<div class="card-centro">
    <div style="position:absolute; top:10px; right:15px; font-size:12px; color:#6B7280;">#{index}</div>
    <div style="color: #1E3A8A; font-size: 22px; font-weight: 800;">{nome} 🕊️</div>
    <div style="color:#065F46; font-weight:700; background:#D1FAE5; padding:8px; border-radius:8px; margin:10px 0;">🗣️ PALESTRA: {palestra}</div>
    <div style="margin:5px 0;">👤 <b>Responsável:</b> {responsavel}</div>
    <div style="margin:5px 0;">🏙️ <b>Cidade:</b> {cidade} | 📍 <b>Endereço:</b> {endereco}</div>
    <div style="margin-top:15px; display:flex; gap:10px;">
        <a href="{link_maps}" target="_blank" class="btn-link" style="background:#4285F4;">📍 Maps</a>
        <a href="{link_wa}" target="_blank" class="btn-link" style="background:#25D366;">WhatsApp</a>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SISTEMA DE LOGIN / CADASTRO ---
if not st.session_state.get("logado", False):
    st.markdown("<div style='text-align: center; color: #60A5FA; font-size: 32px; font-weight: 800; margin-bottom: 30px;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)
    
    # MOSTRAR MENSAGEM DE CADASTRO COM LÓGICA DE LIMPEZA
    if st.session_state.get("cadastro_ok"):
        col_m, col_b = st.columns([0.9, 0.1])
        with col_m:
            st.success(st.session_state["cadastro_msg"])
        with col_b:
            if st.button("X"): # Botão para remover a mensagem manualmente
                st.session_state["cadastro_ok"] = False
                st.rerun()

    t1, t2 = st.tabs(["🚪 Entrar", "✨ Cadastrar"])
    
    with t1:
        with st.form("login"):
            em = st.text_input("📧 E-mail")
            se = st.text_input("🔑 Senha", type="password")
            if st.form_submit_button("🚀 Entrar", use_container_width=True): 
                try:
                    users = supabase.table("participantes").select("*").eq("email", em).execute()
                    if users.data and users.data[0].get('senha') == se:
                        supabase.table("participantes").update({"status": "online", "ultimo_acesso": datetime.datetime.now().isoformat()}).eq("email", em).execute()
                        st.session_state["logado"] = True
                        st.session_state["email_logado"] = em
                        st.session_state["cadastro_ok"] = False # LIMPA A MENSAGEM AO LOGAR
                        st.rerun()
                    else: st.error("❌ Email ou Senha incorretos!")
                except Exception as e: st.error(f"Erro: {e}")
    
    with t2:
        with st.form("cadastro"):
            n_c = st.text_input("👤 Nome completo")
            e_c = st.text_input("📧 E-mail")
            s_c = st.text_input("🔑 Senha", type="password")
            if st.form_submit_button("✅ Cadastrar", use_container_width=True):
                if n_c and e_c and len(s_c) >= 3:
                    res = supabase.table("participantes").insert({"nome": n_c, "email": e_c, "senha": s_c, "status": "ausente"}).execute()
                    if res.data:
                        st.session_state["cadastro_ok"] = True
                        st.session_state["cadastro_msg"] = "✅ CADASTRO CONCLUÍDO! Email enviado! Vá na aba ENTRAR e faça login!"
                        enviar_email_confirmacao(e_c, "cadastro")
                        st.rerun()
                else: st.warning("Preencha todos os campos corretamente!")

# --- ÁREA LOGADA ---
else:
    # Resetar mensagem de cadastro se o usuário estiver logado
    st.session_state["cadastro_ok"] = False

    ag_br = datetime.datetime.now() - datetime.timedelta(hours=3)
    st.markdown(f"""<div style="display:flex;align-items:center;gap:15px;margin-bottom:20px;">
    <span style="font-weight:800;color:#1E3A8A;">{ag_br.strftime("%H:%M")}</span>
    <span style="font-weight:800;color:#1E3A8A;">{ag_br.strftime("%d/%m/%Y")}</span>
    <hr style="flex-grow:1;border:none;border-top:1px solid #ccc;margin:0;"></div>""", unsafe_allow_html=True)

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
            if st.button("🚪 Sair", use_container_width=True):
                supabase.table("participantes").update({"status": "ausente"}).eq("email", st.session_state["email_logado"]).execute()
                st.session_state.clear()
                st.rerun()
    else:
        if st.button("⬅️ VOLTAR"): st.session_state["pagina"] = None; st.rerun()

        if pag == "pesquisar":
            st.session_state["termo_pesquisa"] = st.text_input("Busca:", value=st.session_state["termo_pesquisa"])
            if len(st.session_state["termo_pesquisa"]) >= 3:
                t_norm = normalize_text(st.session_state["termo_pesquisa"])
                res = df[df.apply(lambda r: t_norm in normalize_text(" ".join(r.astype(str))), axis=1)]
                for i, (_, row) in enumerate(res.iterrows(), 1): renderizar_card(row, i)

        elif pag == "cidade":
            cids = sorted(df["CIDADE DO CENTRO ESPIRITA"].dropna().unique())
            sel = st.selectbox("Selecione:", ["-- Selecione --"] + list(cids))
            if sel != "-- Selecione --":
                res = df[df["CIDADE DO CENTRO ESPIRITA"] == sel]
                for i, (_, row) in enumerate(res.iterrows(), 1): renderizar_card(row, i)

        elif pag == "admin":
            admin_pw = st.text_input("Senha Admin:", type="password")
            if admin_pw == "1asd":
                users_data = supabase.table("participantes").select("*").execute().data
                st.markdown(f'<div class="admin-linha-info"><span>🟢 Online: {len([u for u in users_data if u.get("status") == "online"])}</span></div>', unsafe_allow_html=True)
                for u in users_data:
                    # DATA FORMATADA NO ADMIN (SEU PEDIDO)
                    data_form = formatar_data_admin(u.get("created_at"))
                    st.markdown(f'''
                        <div class="admin-reg">
                            <span><b>{u["nome"]}</b> ({u["email"]})</span>
                            <span class="data-admin-cor">{data_form}</span>
                        </div>
                    ''', unsafe_allow_html=True)

        elif pag == "frases":
            st.info('"Embora ninguém possa voltar atrás e fazer um novo começo, qualquer um pode começar agora e fazer um novo fim." — **Chico Xavier**')
