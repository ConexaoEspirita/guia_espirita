import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse  # ESSENCIAL PARA O MAPS FUNCIONAR

# 1. Configuração e Estilo "Placar Profissional"
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .card-centro {
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 8px solid #0047AB; margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .nome-principal { color: #0047AB; font-size: 26px; font-weight: bold; line-height: 1.1; }
    .nome-fantasia { color: #5CACE2; font-size: 17px; font-weight: 500; margin-bottom: 12px; font-style: italic; }
    .info-texto { color: #555; font-size: 15px; margin-bottom: 4px; }
    .tag-palestra { 
        background-color: #D4EDDA; color: #155724; padding: 5px 10px; 
        border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block; margin-top: 10px;
    }
    div.stLinkButton > a { 
        width: 100% !important; font-size: 15px !important; font-weight: bold !important; 
        height: 45px !important; display: flex !important; align-items: center !important; justify-content: center !important;
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
EMAIL_MESTRE = "seu-email@gmail.com" 

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
                st.session_state.logado = True; st.session_state.usuario_email = e; st.rerun()
            else: st.error("Incorreto!")
    with aba2:
        ec = st.text_input("Novo E-mail").strip().lower()
        sc = st.text_input("Nova Senha", type="password")
        if st.button("CADASTRAR"):
            supabase.table("acessos").insert({"email": ec, "senha": sc, "status": "CADASTRO"}).execute()
            st.success("Criado! Vá em Entrar.")

# --- TELA PRINCIPAL ---
else:
    # BANNER DE BOAS-VINDAS 🕊️
    st.image("https://images.unsplash.com", use_container_width=True)
    st.title("🕊️ Guia Espírita 🕊️")
    
    if st.sidebar.button("🚪 Sair do Guia"): 
        supabase.table("acessos").insert({"email": st.session_state.usuario_email, "status": "SAIDA"}).execute()
        st.session_state.logado = False; st.rerun()

    # BUSCA INTELIGENTE
    busca = st.text_input("🔍 O que você procura?", placeholder="Busque por Nome, Cidade ou Responsável...")

    if busca:
        try:
            df = pd.read_excel("guia.xlsx").astype(str).replace('nan', '')
            res = df[df.apply(lambda r: r.str.contains(busca, case=False).any(), axis=1)]

            if not res.empty:
                for _, row in res.iterrows():
                    fantasia = row.get('Nome Fantasia', '')
                    nome = row.get('Nome', 'Centro Espírita')
                    cidade = row.get('Cidade', '')
                    endereco = row.get('Endereco', '')
                    palestra = row.get('Palestra', '')
                    responsavel = row.get('Responsavel', 'Não informado')
                    contato = row.get('Celular', '')

                    # Card Visual Estilo Placar 🕊️
                    st.markdown(f"""
                        <div class="card-centro">
                            <div class="nome-principal">{nome}</div>
                            <div class="nome-fantasia">{fantasia}</div>
                            <div class="info-texto">👤 <b>Responsável:</b> {responsavel}</div>
                            <div class="info-texto">📍 {endereco}</div>
                            <div class="info-texto">🏙️ {cidade}</div>
                            {f'<div class="tag-palestra">🗓️ Palestra: {palestra}</div>' if palestra else ''}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # CORREÇÃO DOS BOTÕES DE AÇÃO
                    col1, col2 = st.columns(2)
                    with col1:
                        if endereco:
                            # MAPS: Codifica para aceitar acentos e espaços
                            end_completo = f"{endereco} {cidade}".strip()
                            u_maps = f"https://www.google.com{urllib.parse.quote(end_completo)}"
                            st.link_button("🗺️ MAPS", u_maps)
                    with col2:
                        if contato:
                            # WHATSAPP: Limpa ( ) - e espaços
                            num_limpo = ''.join(filter(str.isdigit, contato))
                            if len(num_limpo) >= 10:
                                st.link_button("💬 WHATSAPP", f"https://wa.me{num_limpo}")
                            else:
                                st.link_button("📞 LIGAR", f"tel:{num_limpo}")
                    st.write("") 
            else:
                st.warning("Nenhum resultado encontrado.")
        except:
            st.error("Erro ao ler a planilha. Verifique os nomes das colunas!")
    else:
        st.info("Digite acima para pesquisar! 🙏")
