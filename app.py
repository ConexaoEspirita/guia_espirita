import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# 1. Configuração e Estilo Visual (App Premium)
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    /* Card de Resultado Compacto */
    .card-resultado {
        background-color: white;
        padding: 12px 15px;
        border-radius: 10px;
        border-left: 5px solid #0047AB;
        margin-bottom: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .titulo-centro { color: #1A1A1B; font-size: 17px; font-weight: bold; margin-bottom: 2px; }
    .texto-end { color: #5F6368; font-size: 13px; margin-bottom: 8px; }
    
    /* Deixar botões pequenos e lado a lado */
    div.stButton > button, div.stLinkButton > a {
        width: auto !important;
        padding: 3px 10px !important;
        font-size: 12px !important;
        height: 30px !important;
        min-height: 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO SUPABASE ---
url = "https://fjqowpuzenqraugcmmtp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZqcW93cHV6ZW5xcmF1Z2NtbXRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE4Njk2NzQsImV4cCI6MjA4NzQ0NTY3NH0.otWbLrbW4zYOb8-PCZwHYP9vQIbcWCRP_drXHGwIjzw"
supabase = create_client(url, key)

if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuario_email' not in st.session_state: st.session_state.usuario_email = ""

# ⚠️ COLOQUE SEU E-MAIL DE ADMIN AQUI ⚠️
EMAIL_MESTRE = "seu-email-aqui@gmail.com" 

# --- TELA DE ACESSO ---
if not st.session_state.logado:
    st.title("🕊️ Guia Espírita 🕊️")
    aba1, aba2 = st.tabs(["🔐 Entrar", "📝 Criar Conta"])
    with aba1:
        e = st.text_input("E-mail", key="l_e").strip().lower()
        s = st.text_input("Senha", type="password", key="l_s")
        if st.button("ACESSAR GUIA"):
            res = supabase.table("acessos").select("*").eq("email", e).eq("senha", s).execute()
            if len(res.data) > 0:
                supabase.table("acessos").insert({"email": e, "status": "ENTRADA"}).execute()
                st.session_state.logado = True
                st.session_state.usuario_email = e
                st.rerun()
            else: st.error("Incorreto!")
    with aba2:
        ec = st.text_input("Novo E-mail").strip().lower()
        sc = st.text_input("Nova Senha", type="password")
        if st.button("CADASTRAR"):
            supabase.table("acessos").insert({"email": ec, "senha": sc, "status": "CADASTRO"}).execute()
            st.success("Criado! Vá em Entrar.")

# --- TELA PRINCIPAL ---
else:
    st.title("🕊️ Guia Espírita")
    if st.sidebar.button("Sair"): 
        supabase.table("acessos").insert({"email": st.session_state.usuario_email, "status": "SAIDA"}).execute()
        st.session_state.logado = False; st.rerun()

    # Admin: Painel escondido
    if st.session_state.usuario_email == EMAIL_MESTRE:
        with st.expander("🛠️ ADMIN: Ver Planilha"):
            st.dataframe(pd.read_excel("guia.xlsx"), use_container_width=True)

    # BARRA DE PESQUISA (A LUPA)
    busca = st.text_input("🔍 O que você procura?", placeholder="Digite o nome do centro ou cidade...")

    if busca: # SÓ APARECE SE DIGITAR
        try:
            df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
            res = df[df.apply(lambda r: r.str.contains(busca, case=False).any(), axis=1)]

            if not res.empty:
                st.write(f"Resultados ({len(res)}):")
                for _, row in res.iterrows():
                    nome = row.get('Nome', 'Centro')
                    end = row.get('Endereco', row.get('Endereço', ''))
                    cid = row.get('Cidade', '')
                    cel = row.get('Celular', '')

                    # Card Compacto
                    st.markdown(f"""<div class="card-resultado"><div class="titulo-centro">{nome}</div><div class="texto-end">📍 {end} - {cid}</div></div>""", unsafe_allow_html=True)
                    
                    # Botões na mesma linha
                    c1, c2, c3 = st.columns([1,1,2]) 
                    with c1:
                        if end:
                            u_m = f"https://www.google.com{urllib.parse.quote(end + ' ' + cid)}"
                            st.link_button("🗺️ Maps", u_m)
                    with c2:
                        if cel:
                            n = ''.join(filter(str.isdigit, cel))
                            st.link_button("💬 Zap", f"https://wa.me{n}")
                    st.write("") 
            else:
                st.warning("Nenhum resultado.")
        except:
            st.error("Erro ao carregar dados.")
    else:
        st.info("Digite acima para encontrar um centro! 🙏")
