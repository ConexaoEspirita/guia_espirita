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

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
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
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES
# =========================
def ajustar(txt):
    return str(txt).strip() if pd.notna(txt) else ""

def normalize_text(text):
    if pd.isna(text):
        return ""
    return unicodedata.normalize("NFKD", str(text)).encode("ASCII", "ignore").decode("utf-8").lower().strip()

def renderizar_card(row, index):
    nome = ajustar(row.get("NOME","Centro Espírita"))
    fantasia = ajustar(row.get("NOME FANTASIA"))
    endereco = ajustar(row.get("ENDERECO"))
    cidade = ajustar(row.get("CIDADE DO CENTRO ESPIRITA"))
    palestra = ajustar(row.get("PALESTRA PUBLICA"))
    responsavel = ajustar(row.get("RESPONSAVEL"))
    numero = "".join(filter(str.isdigit, str(row.get("CELULAR"))))

    query = urllib.parse.quote(f"{endereco}, {cidade}")
    link_maps = f"https://www.google.com{query}"
    link_wa = f"https://wa.me{numero}" if len(numero)>=10 else "#"

    st.markdown(f"""
    <div class="card-centro">
        <div style="position:absolute; top:10px; right:15px; font-size:12px; color:#6B7280;">#{index}</div>
        <div style="color:#1E3A8A; font-size:22px; font-weight:800;">{nome} 🕊️</div>
        {"<div style='color:#3B82F6; font-style:italic;'>" + fantasia + "</div>" if fantasia else ""}
        <div style="color:#065F46; font-weight:700; background:#D1FAE5; padding:8px; border-radius:8px; margin:10px 0;">
            🗣️ PALESTRA: {palestra}
        </div>
        <div>👤 <b>Responsável:</b> {responsavel}</div>
        <div>🏙️ <b>Cidade:</b> {cidade}</div>
        <div>📍 <b>Endereço:</b> {endereco}</div>
        <div style="margin-top:15px; display:flex; gap:10px;">
            <a href="{link_maps}" target="_blank" class="btn-link" style="background:#4285F4;">📍 Maps</a>
            <a href="{link_wa}" target="_blank" class="btn-link" style="background:#25D366;">WhatsApp</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# LOGIN (TEU ORIGINAL)
# =========================
if not st.session_state["logado"]:

    st.markdown("<div style='text-align:center; color:#60A5FA; font-size:32px; font-weight:800;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🚪 Entrar","✨ Cadastrar"])

    with tab1:
        with st.form("login"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                st.session_state["logado"] = True
                st.rerun()

    with tab2:
        with st.form("cadastro"):
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Cadastrar", use_container_width=True):
                try:
                    # SALVA DATA/HORA PEQUENA NO SUPABASE
                    agora = (datetime.datetime.utcnow() - datetime.timedelta(hours=3))
                    dt_txt = agora.strftime('%d-%m-%Y - %Hh%M,%Ss')
                    
                    supabase.table("participantes").insert({
                        "nome": nome,
                        "email": email,
                        "criado_em": dt_txt
                    }).execute()
                    st.success("✅ Cadastrado com sucesso!")
                    st.session_state["logado"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar: {e}")

# =========================
# APP PRINCIPAL
# =========================
else:
    # MUDANÇA 1: HORÁRIO, DATA E LINHA NA MESMA LINHA
    agora = (datetime.datetime.utcnow() - datetime.timedelta(hours=3))
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
        <span style="font-weight:bold;">{agora.strftime('%H:%M')}</span>
        <span style="font-weight:bold;">{agora.strftime('%d/%m/%Y')}</span>
        <hr style="flex-grow: 1; border: none; border-top: 1px solid #ccc; margin: 0;">
    </div>
    """, unsafe_allow_html=True)

    @st.cache_data
    def carregar_dados():
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        return df

    try:
        df = carregar_dados()
    except:
        st.error("Erro ao carregar guia.xlsx. Verifique o arquivo e aba.")
        st.stop()

    pagina = st.session_state["pagina"]

    if pagina is None:
        st.markdown("<div class='titulo-grande' style='text-align:center; color:#60A5FA;'>🕊️ Guia Espírita 🕊️</div>", unsafe_allow_html=True)

        c1,c2 = st.columns(2)
        with c1:
            if st.button("🔎 Busca Avançada", use_container_width=True):
                st.session_state["pagina"] = "pesquisar"; st.rerun()
            if st.button("📍 Por Cidade", use_container_width=True):
                st.session_state["pagina"] = "cidade"; st.rerun()
        with c2:
            if st.button("📊 Admin", use_container_width=True):
                st.session_state["pagina"] = "admin"; st.rerun()
            if st.button("🕊️ Frases", use_container_width=True):
                st.session_state["pagina"] = "frases"; st.rerun()

        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear(); st.cache_data.clear(); st.rerun()

    else:

        col1,col2 = st.columns(2)
        with col1:
            if st.button("⬅️ VOLTAR", use_container_width=True):
                st.session_state["pagina"] = None; st.rerun()
        with col2:
            if st.button("🔄 LIMPAR", use_container_width=True):
                st.session_state["termo_pesquisa"] = "" ; st.rerun()

        if pagina == "pesquisar":
            termo = st.text_input("Digite nome ou cidade ou responsável:", value=st.session_state["termo_pesquisa"])
            if termo and len(termo.strip()) >= 3:
                st.session_state["termo_pesquisa"] = termo
                t_norm = normalize_text(termo)
                res = df[df["NOME"].apply(normalize_text).str.contains(t_norm,na=False) |
                         df["CIDADE DO CENTRO ESPIRITA"].apply(normalize_text).str.contains(t_norm,na=False)]
                for i,(_,row) in enumerate(res.iterrows(),1): renderizar_card(row,i)

        elif pagina == "cidade":
            # MUDANÇA 2: SELETOR COM CONTAGEM EM TODAS AS CIDADES
            contagem = df["CIDADE DO CENTRO ESPIRITA"].value_counts().to_dict()
            cidades_lista = sorted(df["CIDADE DO CENTRO ESPIRITA"].dropna().unique())
            opcoes_formatadas = [f"{c} ({contagem.get(c, 0)})" for c in cidades_lista]
            
            escolha = st.selectbox("Selecione uma cidade:", ["-- Selecione --"] + opcoes_formatadas)

            if escolha != "-- Selecione --":
                cidade_limpa = escolha.rsplit(" (", 1)[0]
                res = df[df["CIDADE DO CENTRO ESPIRITA"] == cidade_limpa]
                for i,(_,row) in enumerate(res.iterrows(),1): renderizar_card(row,i)

        elif pagina == "admin":
            st.subheader("👥 Usuários Cadastrados")
            # Mostra o que está no Supabase com o horário pequeno
            try:
                users = supabase.table("participantes").select("*").execute()
                for u in users.data:
                    st.write(f"{u.get('nome')}, {u.get('email')} - {u.get('criado_em')}")
            except: st.error("Erro ao ler Supabase")

        elif pagina == "frases":
            # MUDANÇA 3: FRASE CHICO XAVIER
            st.markdown("### 🕊️ Mensagem de Chico Xavier")
            st.info('"Embora ninguém possa voltar atrás e fazer um novo começo, qualquer um pode começar agora e fazer um novo fim." \n\n— **Chico Xavier**')
