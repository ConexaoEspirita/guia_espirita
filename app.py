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
    background: white;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,71,171,0.1);
    margin-bottom: 16px;
    border-left: 5px solid #0047AB;
}
.nome-grande { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800 !important; }
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

if "logado" not in st.session_state:
    st.session_state.logado = False

# 4. Tela de Login
if not st.session_state.logado:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        email_input = st.text_input("📧 E-mail").strip().lower()
    with c2:
        senha_input = st.text_input("🔒 Senha", type="password").strip()
    
    if st.button("🚀 ACESSAR GUIA", use_container_width=True):
        res = supabase.table("acessos").select("*").eq("email", email_input).eq("senha", senha_input).execute()
        if res.data:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("❌ E-mail ou senha incorretos!")

# 5. Tela Principal
else:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    
    # Lógica para limpar a busca anterior ao digitar algo novo
    def ao_mudar_busca():
        st.session_state.busca = st.session_state.campo_pesquisa

    col_busca, col_btn = st.columns([4,1])
    with col_busca:
        # Usamos o 'on_change' para atualizar assim que o usuário digita
        busca_input = st.text_input("🔍 Buscar", 
                                  placeholder="Digite o nome, rua ou bairro...", 
                                  label_visibility="collapsed",
                                  key="campo_pesquisa",
                                  on_change=ao_mudar_busca)
    with col_btn:
        if st.button("🔎 Pesquisar", use_container_width=True):
            st.session_state.busca = st.session_state.campo_pesquisa
            st.rerun()
    
    busca = st.session_state.get("busca", "").strip()
    
    if busca:
        try:
            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            df.columns = [col.strip() for col in df.columns]
            df = df.rename(columns={
                'NOME FANTASIA': 'Nome Fantasia',
                'NOME': 'Nome Real',
                'CIDADE DO CENTRO ESPIRITA': 'Cidade',
                'ENDERECO': 'Endereco',
                'PALESTRA PUBLICA': 'Palestra',
                'RESPONSAVEL': 'Responsavel',
                'CELULAR': 'Celular'
            })

            termo = limpar_busca(busca)
            resultados = []
            
            for _, row in df.iterrows():
                dados_busca = [str(row.get('Nome Fantasia','')), str(row.get('Nome Real','')), 
                              str(row.get('Endereco','')), str(row.get('Cidade',''))]
                texto_comparar = " ".join([limpar_busca(v) for v in dados_busca])
                if termo in texto_comparar:
                    resultados.append(row)

            if resultados:
                st.write(f"✨ Encontrados {len(resultados)} resultados para: **{busca}**")
                # Botão para limpar a busca atual rapidamente
                if st.button("🧹 Limpar Pesquisa"):
                    st.session_state.busca = ""
                    st.rerun()
                
                for r in resultados:
                    st.markdown(f"""
                    <div class="card-centro">
                        <div class="nome-grande">{r['Nome Real']}</div>
                        <div class="info-texto"><b>📍 Endereço:</b> {r['Endereco']}</div>
                        <div class="info-texto"><b>🏙️ Cidade:</b> {r['Cidade']}</div>
                        <div class="info-texto"><b>👤 Responsável:</b> {r['Responsavel']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        link_maps = urllib.parse.quote(f"{r['Endereco']}, {r['Cidade']}")
                        st.link_button("🗺️ MAPS", f"https://www.google.com{link_maps}", use_container_width=True)
                    with c2:
                        whats = ''.join(filter(str.isdigit, str(r['Celular'])))
                        if len(whats) >= 10:
                            st.link_button("💬 WhatsApp", f"https://wa.me{whats}", use_container_width=True)
                    st.divider()
            else:
                st.warning(f"❌ Nenhum centro encontrado para '{busca}'.")
                if st.button("Voltar"):
                    st.session_state.busca = ""
                    st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.info("💡 Digite o **nome do centro**, a **rua** ou o **bairro**.")

    # Botão Sair
    if st.sidebar.button("🚪 Sair do Guia"):
        st.session_state.clear()
        st.rerun()
