import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import datetime
import random
import string
from supabase import create_client, Client

# ================= SUPABASE =================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Guia Espírita", layout="wide")

# ================= SESSION STATE =================
if "pagina" not in st.session_state: st.session_state["pagina"] = None
if "logado" not in st.session_state: st.session_state["logado"] = False
if "termo_pesquisa" not in st.session_state: st.session_state["termo_pesquisa"] = ""
if "codigo_confirmacao" not in st.session_state: st.session_state["codigo_confirmacao"] = ""

# ================= CSS =================
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

# ================= FUNÇÕES =================
def ajustar(txt): return str(txt).strip() if pd.notna(txt) else ""
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
    if len(numero) >= 10:
        numero_completo = f"+55{numero}"
        link_wa = f"https://wa.me/{numero_completo}"
    else:
        link_wa = "#"

    if endereco and cidade:
        texto_busca = f"{endereco}, {cidade}"
    elif cidade:
        texto_busca = cidade
    else:
        texto_busca = "Brasil"
    query = urllib.parse.quote(texto_busca.strip())
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

# ================= LOGIN / CADASTRO =================
if not st.session_state.get("logado", False):
    st.markdown("<div style='text-align: center; color: #60A5FA; font-size: 32px; font-weight: 800; margin-bottom: 30px;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🚪 Entrar", "✨ Cadastrar"])

    # ---------------- LOGIN ----------------
    with t1:
        with st.form("login"):
            em = st.text_input("E-mail")
            se = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                check = supabase.table("participantes").select("*").eq("email", em).execute()
                if check.data:
                    user = check.data[0]
                    if user.get("confirmado", False) and user.get("senha") == se:
                        st.session_state["logado"] = True
                        supabase.table("participantes").update({
                            "ultimo_acesso": datetime.datetime.now()
                        }).eq("email", em).execute()
                        st.rerun()
                    else:
                        st.warning("⚠️ Usuário não confirmado ou senha incorreta")
                else:
                    st.warning("⚠️ Usuário não encontrado")
        st.markdown('[🔑 Esqueci minha senha](#)', unsafe_allow_html=True)

    # ---------------- CADASTRO ----------------
    with t2:
        with st.form("cadastro"):
            n_c = st.text_input("Nome")
            e_c = st.text_input("E-mail")
            s_c = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Cadastrar", use_container_width=True)

            if submitted:
                try:
                    check = supabase.table("participantes").select("*").eq("email", e_c).execute()
                    if check.data:
                        st.warning("⚠️ E-mail já cadastrado!")
                    else:
                        codigo = "".join(random.choices(string.digits, k=6))
                        st.session_state["codigo_confirmacao"] = codigo

                        supabase.table("participantes").insert({
                            "nome": n_c,
                            "email": e_c,
                            "senha": s_c,
                            "confirmado": False,
                            "codigo_confirmacao": codigo
                        }).execute()

                        st.success("✅ Cadastro salvo! Por favor, confirme seu e-mail antes de logar.")
                        st.session_state["pagina"] = "login"  # volta para login
                        st.rerun()
                except Exception as e:
                    st.error("❌ ERRO SUPABASE:")
                    st.code(str(e))

# ================= RESTO DO APP =================
else:
    ag_br = datetime.datetime.now() - datetime.timedelta(hours=3)
    st.markdown(f'<div style="display:flex;align-items:center;gap:15px;margin-bottom:20px;"><span style="font-weight:800;color:#1E3A8A;">{ag_br.strftime("%H:%M")}</span><span style="font-weight:800;color:#1E3A8A;">{ag_br.strftime("%m-%d-%Y")}</span><hr style="flex-grow:1;border:none;border-top:1px solid #ccc;margin:0;"></div>', unsafe_allow_html=True)

    df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
    df.columns = df.columns.str.strip()
    pag = st.session_state.get("pagina")

    # ================= PÁGINA INICIAL =================
    if pag is None:
        st.markdown("<div class='titulo-grande' style='color: #60A5FA; text-align: center;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔎 Busca Avançada", use_container_width=True): st.session_state["pagina"] = "pesquisar"; st.rerun()
            if st.button("📍 Por Cidade", use_container_width=True): st.session_state["pagina"] = "cidade"; st.rerun()
        with c2:
            if st.button("📊 Admin", use_container_width=True): st.session_state["pagina"] = "admin"; st.rerun()
            if st.button("🕊️ Frases", use_container_width=True): st.session_state["pagina"] = "frases"; st.rerun()
        if st.button("🚪 Sair", use_container_width=True): st.session_state.clear(); st.rerun()

    # ================= PÁGINAS INTERMEDIÁRIAS =================
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ VOLTAR", use_container_width=True): st.session_state["pagina"] = None; st.rerun()
        with col2:
            if st.button("🔄 LIMPAR", use_container_width=True): st.session_state["termo_pesquisa"] = ""; st.rerun()

        if pag == "pesquisar":
            termo = st.text_input("Digite o que busca:", value=st.session_state["termo_pesquisa"])
            if termo and len(termo.strip()) >= 3:
                st.session_state["termo_pesquisa"] = termo
                t_norm = normalize_text(termo.strip())
                res = df[df.apply(lambda r: t_norm in normalize_text(" ".join(r.astype(str))), axis=1)]
                if not res.empty:
                    st.success(f"{len(res)} centro(s) encontrado(s)")
                    for i, (_, row) in enumerate(res.iterrows(), 1): renderizar_card(row, i)

        elif pag == "cidade":
            counts = df["CIDADE DO CENTRO ESPIRITA"].value_counts().to_dict()
            cids = sorted(df["CIDADE DO CENTRO ESPIRITA"].dropna().unique())
            opts = [f"{c} ({counts.get(c, 0)})" for c in cids]
            sel = st.selectbox("Selecione:", ["-- Selecione --"] + opts)
            if sel != "-- Selecione --":
                c_real = sel.rsplit(" (", 1)[0]
                res = df[df["CIDADE DO CENTRO ESPIRITA"] == c_real]
                for i, (_, row) in enumerate(res.iterrows(), 1): renderizar_card(row, i)

        elif pag == "admin":
            admin_pw = st.text_input("Senha Admin:", type="password")
            if admin_pw == "estudantesabio2026":
                st.markdown(f'<div class="admin-linha-info"><span>Centros: {len(df)}</span> | <span>Cidades: {df["CIDADE DO CENTRO ESPIRITA"].nunique()}</span> | <span>📅 {ag_br.strftime("%m-%d-%Y")}</span> | <span>🕐 {ag_br.strftime("%H:%M:%S")}</span> | <span>📱 Cadastros: {len(supabase.table("participantes").select("*").execute().data)}</span></div>', unsafe_allow_html=True)
                st.write("### 👥 Registros no Supabase")
                users = supabase.table("participantes").select("*").execute()
                for u in users.data:
                    st.markdown(f'<div class="admin-reg"><span><b>{u["nome"]}</b> ({u["email"]})</span><span>{u.get("created_at")}</span></div>', unsafe_allow_html=True)

        elif pag == "frases":
            st.info('"Embora ninguém possa voltar atrás e fazer um novo começo, qualquer um pode começar agora e fazer um novo fim." — **Chico Xavier**')
