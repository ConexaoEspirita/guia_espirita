import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

# 1. Configuração da Página
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# 2. Estilização CSS
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%); }
.titulo-premium {
    background: linear-gradient(90deg, #0047AB, #1976D2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    text-align: center;
}
.card-centro {
    background: white; padding: 20px; border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,71,171,0.1); margin-bottom: 16px;
    border-left: 5px solid #0047AB;
}
.nome-grande { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800 !important; }
.info-texto { color: #374151 !important; font-size: 14px !important; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# 3. Conexão Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = unicodedata.normalize('NFD', str(texto))
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\w\s]', ' ', texto.lower())
    return texto.strip()

# Inicialização de estados
if "logado" not in st.session_state: st.session_state.logado = False
if "termo_pesquisado" not in st.session_state: st.session_state.termo_pesquisado = ""

def resetar_pesquisa():
    st.session_state.termo_pesquisado = ""
    if "campo_digitado" in st.session_state:
        st.session_state.campo_digitado = ""

# 4. Tela de Login
if not st.session_state.logado:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        email_in = st.text_input("📧 E-mail").strip().lower()
    with c2:
        senha_in = st.text_input("🔒 Senha", type="password").strip()
    
    if st.button("🚀 ACESSAR GUIA", use_container_width=True):
        res = supabase.table("acessos").select("*").eq("email", email_in).eq("senha", senha_in).execute()
        if res.data:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("❌ E-mail ou senha incorretos!")

# 5. Tela Principal
else:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)

    def processar_pesquisa():
        st.session_state.termo_pesquisado = st.session_state.campo_digitado

    col_busca, col_btn = st.columns([4, 1])
    with col_busca:
        st.text_input("🔍 Buscar", 
                      placeholder="Digite o nome, rua ou bairro...", 
                      label_visibility="collapsed",
                      key="campo_digitado",
                      on_change=processar_pesquisa)
    with col_btn:
        if st.button("🔎 Pesquisar", use_container_width=True):
            processar_pesquisa()
            st.rerun()
    
    busca = st.session_state.termo_pesquisado
    
    if busca:
        try:
            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            df.columns = [col.strip() for col in df.columns]
            df = df.rename(columns={
                'NOME FANTASIA': 'Nome Fantasia', 'NOME': 'Nome Real',
                'CIDADE DO CENTRO ESPIRITA': 'Cidade', 'ENDERECO': 'Endereco',
                'PALESTRA PUBLICA': 'Palestra', 'RESPONSAVEL': 'Responsavel', 'CELULAR': 'Celular'
            })

            termo_limpo = limpar_busca(busca)
            resultados = []
            
            for _, row in df.iterrows():
                dados = [str(row.get('Nome Fantasia','')), str(row.get('Nome Real','')), 
                         str(row.get('Endereco','')), str(row.get('Cidade',''))]
                if termo_limpo in " ".join([limpar_busca(v) for v in dados]):
                    resultados.append(row)

            if resultados:
                st.write(f"✨ Resultados para: **{busca}**")
                if st.button("⬅️ Voltar / Nova Pesquisa"):
                    resetar_pesquisa()
                    st.rerun()

                for r in resultados:
                    # Variáveis para os links
                    v_nome = str(r.get('Nome Real', 'Centro Espírita'))
                    v_endereco = str(r.get('Endereco', ''))
                    v_cidade = str(r.get('Cidade', ''))
                    v_celular = str(r.get('Celular', ''))
                    v_resp = str(r.get('Responsavel', 'Não informado'))

                    st.markdown(f"""
                    <div class="card-centro">
                        <div class="nome-grande">{v_nome}</div>
                        <div class="info-texto"><b>👤 Responsável:</b> {v_resp}</div>
                        <div class="info-texto"><b>📍 Endereço:</b> {v_endereco}</div>
                        <div class="info-texto"><b>🏙️ Cidade:</b> {v_cidade}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # COLUNAS DOS BOTÕES (MAPS E WHATSAPP REATIVADOS)
                    c1, c2 = st.columns(2)
                    with c1:
                        if v_endereco and v_cidade:
                            query = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                            st.link_button("🗺️ Ver no MAPS", f"https://www.google.com{query}", use_container_width=True)
                    with c2:
                        num_limpo = ''.join(filter(str.isdigit, v_celular))
                        if len(num_limpo) >= 10:
                            st.link_button("💬 WhatsApp", f"https://wa.me{num_limpo}", use_container_width=True)
                    st.divider()
            else:
                st.warning(f"❌ '{busca}' não encontrado.")
                if st.button("⬅️ Voltar"):
                    resetar_pesquisa()
                    st.rerun()
        except Exception as e:
            st.error(f"Erro ao ler os dados: {e}")
    else:
        st.info("💡 Digite o **nome do centro**, a **rua** ou o **bairro**.")

    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()
