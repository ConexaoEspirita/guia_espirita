import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS PREMIUM SEM CORTES E COM BOTÕES BLINDADOS ---
st.markdown("""
<style>
    /* Ajuste para o menu não ficar colado no teto */
    [data-testid="stSidebar"] { padding-top: 20px; }
    .stApp { background: #f0f2f6; }
    
    .card-centro { 
        background: white; padding: 25px; border-radius: 15px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px; 
        border-left: 10px solid #0047AB; color: #1e1e1e !important;
    }
    .nome-grande { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800; margin: 0; line-height: 1.2; }
    .palestras-verde { 
        color: #065F46 !important; font-weight: 700; background: #D1FAE5; 
        padding: 10px; border-radius: 8px; margin: 12px 0; border: 1px solid #10B981;
    }
    .btn-row { display: flex; gap: 10px; margin-top: 15px; }
    .btn-link { 
        text-decoration: none !important; color: white !important; 
        padding: 12px; border-radius: 10px; font-weight: bold; 
        text-align: center; flex: 1; display: inline-block;
    }
    .bg-wa { background-color: #25D366; box-shadow: 0 3px 6px rgba(37,211,102,0.3); }
    .bg-maps { background-color: #4285F4; box-shadow: 0 3px 6px rgba(66,133,244,0.3); }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE CARD (PARA REUTILIZAR NA BUSCA E NA CIDADE) ---
def renderizar_card(row):
    nome = str(row.get('NOME', 'Centro Espírita')).strip()
    end = str(row.get('ENDERECO', 'N/I')).strip()
    cid = str(row.get('CIDADE DO CENTRO ESPIRITA', 'N/I')).strip()
    palestras = str(row.get('PALESTRA PUBLICA', 'Consulte')).strip()
    resp = str(row.get('RESPONSAVEL', 'N/I')).strip()
    
    # WhatsApp - Limpeza radical de caracteres
    whats_raw = str(row.get('CELULAR', ''))
    whats_num = "".join(filter(str.isdigit, whats_raw))
    link_wa = f"https://wa.me{whats_num}" if len(whats_num) >= 10 else "#"
    
    # Maps - Query completa
    query_maps = urllib.parse.quote(f"{nome}, {end}, {cid}")
    link_maps = f"https://www.google.com{query_maps}"

    st.markdown(f"""
    <div class="card-centro">
        <div class="nome-grande">{nome} 🕊️</div>
        <div class="palestras-verde">🗣️ PALESTRAS: {palestras}</div>
        <p style="margin:5px 0;">📍 <b>Endereço:</b> {end} - {cid}</p>
        <p style="margin:5px 0;">👤 <b>Responsável:</b> {resp}</p>
        <div class="btn-row">
            <a href="{link_maps}" target="_blank" class="btn-link bg-maps">📍 MAPA</a>
            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WHATSAPP</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🕊️ Guia Espírita")
    with st.form("login"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR"):
            st.session_state.logado = True
            st.rerun()
else:
    # --- MENU LATERAL (O HAMBÚRGUER) ---
    with st.sidebar:
        st.markdown("### ☰ NAVEGAÇÃO")
        opcao = st.radio("Ir para:", ["Início", "🔎 Pesquisar Geral", "📍 Cidades", "⚙️ Admin", "🚪 Sair"])
        
        if opcao == "🚪 Sair":
            st.session_state.logado = False
            st.rerun()

    # --- CARREGAR DADOS ---
    try:
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        col_cidade = 'CIDADE DO CENTRO ESPIRITA'
    except Exception as e:
        st.error(f"Erro ao carregar guia.xlsx: {e}")
        st.stop()

    # --- LÓGICA DAS PÁGINAS ---
    if opcao == "Início":
        st.title("🕊️ Bem-vindo ao Guia Espírita")
        st.info("Use o menu ao lado para pesquisar por nome ou filtrar por cidade.")

    elif opcao == "🔎 Pesquisar Geral":
        st.subheader("Busca em Todas as Cidades")
        termo = st.text_input("Digite o nome do centro, palavra-chave ou cidade:", placeholder="Ex: Kardec")
        
        if termo:
            # Busca em todas as colunas relevantes
            mask = df.astype(str).apply(lambda x: x.str.contains(termo, case=False)).any(axis=1)
            resultado = df[mask]
            
            st.write(f"Encontrados {len(resultado)} resultados:")
            for _, row in resultado.iterrows():
                renderizar_card(row)

    elif opcao == "📍 Cidades":
        cidades = sorted(df[col_cidade].dropna().unique())
        escolha = st.selectbox("Selecione a Cidade:", ["-- Selecione --"] + cidades)
        
        if escolha != "-- Selecione --":
            dados_cidade = df[df[col_cidade] == escolha]
            for _, row in dados_cidade.iterrows():
                renderizar_card(row)

    elif opcao == "⚙️ Admin":
        st.title("Painel Administrativo")
        st.warning("Área restrita para edição de dados.")

