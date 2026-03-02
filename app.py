import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import datetime
import pytz  # Necessário para o horário de Brasília
from supabase import create_client, Client

# =========================
# CONFIGURAÇÕES E CONEXÃO
# =========================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Guia Espírita", layout="wide")

# Ajuste para Horário de Brasília
fuso_br = pytz.timezone('America/Sao_Paulo')
agora = datetime.datetime.now(fuso_br)

if "pagina" not in st.session_state: st.session_state["pagina"] = None
if "logado" not in st.session_state: st.session_state["logado"] = False

# =========================
# CSS - LINHA E ESTILOS
# =========================
st.markdown("""
<style>
#MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
.stApp { background: #f4f7f9; }
.header-info { 
    display: flex; 
    align-items: center; 
    gap: 15px; 
    color: #4B5563; 
    font-weight: 600; 
    margin-bottom: 20px; 
}
.header-info hr { flex-grow: 1; border: none; border-top: 1px solid #ccc; margin: 0; }
</style>
""", unsafe_allow_html=True)

# =========================
# LOGIN / CADASTRO
# =========================
if not st.session_state["logado"]:
    st.markdown("<h2 style='text-align:center; color:#60A5FA;'>🕊️ Guia Espírita</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🚪 Entrar", "✨ Cadastrar"])
    with t1:
        with st.form("login"):
            em = st.text_input("E-mail")
            if st.form_submit_button("Entrar", use_container_width=True):
                st.session_state["logado"] = True; st.rerun()
    with t2:
        with st.form("cad"):
            n = st.text_input("Nome"); e = st.text_input("E-mail")
            if st.form_submit_button("Cadastrar", use_container_width=True):
                supabase.table("participantes").insert({"nome": n, "email": e}).execute()
                st.session_state["logado"] = True; st.rerun()

# =========================
# APP PRINCIPAL
# =========================
else:
    # 1. HORÁRIO, DATA E LINHA NA MESMA LINHA (HEADER)
    st.markdown(f"""
    <div class="header-info">
        <span>{agora.strftime('%H:%M')}</span>
        <span>{agora.strftime('%d/%m/%Y')}</span>
        <hr>
    </div>
    """, unsafe_allow_html=True)

    @st.cache_data
    def carregar():
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        return df
    
    df = carregar()
    pag = st.session_state["pagina"]

    if pag is None:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔎 Busca"): st.session_state["pagina"] = "busca"; st.rerun()
            if st.button("📍 Por Cidade"): st.session_state["pagina"] = "cidade"; st.rerun()
        with c2:
            if st.button("📊 Admin"): st.session_state["pagina"] = "admin"; st.rerun()
            if st.button("🕊️ Frases"): st.session_state["pagina"] = "frases"; st.rerun()
        if st.button("🚪 Sair"): st.session_state.clear(); st.rerun()

    else:
        if st.button("⬅️ VOLTAR"): st.session_state["pagina"] = None; st.rerun()

        # 2. SELETOR COM CONTAGEM EM TODAS AS CIDADES
        if pag == "cidade":
            contagem = df["CIDADE DO CENTRO ESPIRITA"].value_counts().to_dict()
            cidades_unicas = sorted(df["CIDADE DO CENTRO ESPIRITA"].dropna().unique())
            opcoes = [f"{c} ({contagem.get(c, 0)})" for c in cidades_unicas]
            
            escolha = st.selectbox("Cidades:", ["-- Selecione --"] + opcoes)
            if escolha != "-- Selecione --":
                cid_nome = escolha.rsplit(" (", 1)[0]
                res = df[df["CIDADE DO CENTRO ESPIRITA"] == cid_nome]
                st.write(f"Resultados para {cid_nome}:")
                st.dataframe(res)

        # 3. ADMIN - LISTA DE CADASTROS DO SUPABASE COM DATA/HORA PEQUENA
        elif pag == "admin":
            pw = st.text_input("Senha Admin:", type="password")
            if pw == "suasenha123": # <--- Altere aqui
                users = supabase.table("participantes").select("*").execute()
                for u in users.data:
                    dt_log = agora.strftime('%d-%m-%Y - %Hh%M,%Ss')
                    st.markdown(f"""
                        <div style="border-bottom:1px solid #eee; padding:5px 0;">
                            <b>{u['nome']}</b>, {u['email']}
                            <br><span style="font-size:10px; color:gray;">{dt_log}</span>
                        </div>
                    """, unsafe_allow_html=True)

        # 4. FRASE CHICO XAVIER
        elif pag == "frases":
            st.info('"Embora ninguém possa voltar atrás e fazer um novo começo, qualquer um pode começar agora e fazer um novo fim."\n\n— **Chico Xavier**')
