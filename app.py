import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

# 1. Configuração da Página
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# 2. Estilização CSS (Mantendo seu padrão visual)
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%); }
.titulo-premium {
    background: linear-gradient(90deg, #0047AB, #1976D2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem !important; font-weight: 800 !important; text-align: center;
}
.card-centro {
    background: white; padding: 20px; border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,71,171,0.1); margin-bottom: 16px;
    border-left: 5px solid #0047AB;
}
.nome-grande { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800 !important; }
.conta-pequena { 
    font-size: 12px !important; color: #6B7280 !important; margin-bottom: 12px !important;
    background: rgba(255,255,255,0.7); padding: 6px 12px; border-radius: 20px; display: inline-block;
}
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

# Estados de sessão
if "logado" not in st.session_state: st.session_state.logado = False
if "termo_pesquisado" not in st.session_state: st.session_state.termo_pesquisado = ""

# Funções de controle
def executar_pesquisa():
    if st.session_state.campo_digitado:
        st.session_state.termo_pesquisado = st.session_state.campo_digitado
        st.session_state.campo_digitado = "" # LIMPA A BARRA DE DIGITAÇÃO

def voltar_inicio():
    st.session_state.termo_pesquisado = ""
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

    # BARRA DE PESQUISA QUE SE AUTOLIMPA
    col_busca, col_btn = st.columns([4, 1])
    with col_busca:
        st.text_input("🔍 Buscar", placeholder="Digite o nome, rua ou bairro...", 
                      key="campo_digitado", label_visibility="collapsed", on_change=executar_pesquisa)
    with col_btn:
        if st.button("🔎 Pesquisar", use_container_width=True):
            executar_pesquisa()
            st.rerun()
    
    busca = st.session_state.termo_pesquisado
    
    if busca:
        try:
            # Carregamento do Excel
            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            df.columns = [col.strip() for col in df.columns]
            
            # Mapeamento exato das colunas da sua planilha
            df = df.rename(columns={
                'NOME FANTASIA': 'Nome Fantasia',
                'NOME': 'Nome Real',
                'CIDADE DO CENTRO ESPIRITA': 'Cidade',
                'ENDERECO': 'Endereco',
                'RESPONSAVEL': 'Responsavel',
                'CELULAR': 'Celular'
            })

            termo_limpo = limpar_busca(busca)
            resultados = []
            
            for _, row in df.iterrows():
                # Busca em Nome Real, Fantasia, Endereço e Cidade
                campos_busca = [str(row.get('Nome Fantasia','')), str(row.get('Nome Real','')), 
                               str(row.get('Endereco','')), str(row.get('Cidade',''))]
                linha_completa = " ".join([limpar_busca(v) for v in campos_busca])
                
                if termo_limpo in linha_completa:
                    resultados.append(row)

            if resultados:
                # O CONTADOR VOLTOU
                st.markdown(f'<div class="conta-pequena">✨ achou {len(resultados)} resultado{"s" if len(resultados) != 1 else ""} para "{busca}"</div>', unsafe_allow_html=True)
                
                if st.button("⬅️ Voltar / Nova Pesquisa"):
                    voltar_inicio()
                    st.rerun()

                for r in resultados:
                    v_nome = str(r.get('Nome Real', 'Centro Espírita'))
                    v_fantasia = str(r.get('Nome Fantasia', ''))
                    v_endereco = str(r.get('Endereco', ''))
                    v_cidade = str(r.get('Cidade', ''))
                    v_celular = str(r.get('Celular', ''))
                    v_resp = str(r.get('Responsavel', 'Não informado'))

                    st.markdown(f"""
                    <div class="card-centro">
                        <div class="nome-grande">{v_nome}</div>
                        {f'<div style="color:#3B82F6; font-weight:600; font-style:italic;">{v_fantasia}</div>' if v_fantasia else ''}
                        <div style="margin-top:8px;">📍 <b>Endereço:</b> {v_endereco}</div>
                        <div>🏙️ <b>Cidade:</b> {v_cidade}</div>
                        <div>👤 <b>Responsável:</b> {v_resp}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # COLUNAS DOS BOTÕES (CORRIGIDOS)
                    c1, c2 = st.columns(2)
                    with c1:
                        # Gerando link do Google Maps com endereço + cidade
                        if v_endereco:
                            query_maps = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                            st.link_button("🗺️ Ver no MAPS", f"https://www.google.com{query_maps}", use_container_width=True)
                    with c2:
                        # Gerando link do WhatsApp (limpando o número)
                        num_limpo = ''.join(filter(str.isdigit, v_celular))
                        if len(num_limpo) >= 10:
                            st.link_button("💬 WhatsApp", f"https://wa.me{num_limpo}", use_container_width=True)
                    st.divider()
            else:
                st.warning(f"❌ Nenhum centro encontrado para '{busca}'.")
                if st.button("⬅️ Voltar"):
                    voltar_inicio()
                    st.rerun()
        except Exception as e:
            st.error(f"Erro ao processar a planilha: {e}")
    else:
        st.info("💡 Digite o **nome do centro**, a **rua** ou o **bairro** para pesquisar.")

    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()
