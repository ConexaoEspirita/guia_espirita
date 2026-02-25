import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS COM SOMBRA FORTE E LINHA DE DESTAQUE ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { padding-top: 35px; }
    .stApp { background: #f0f2f6; }
    
    .card-centro { 
        background: white; padding: 25px; border-radius: 20px; 
        /* Sombra intensa para o efeito 'flutuante' */
        box-shadow: 0 10px 30px rgba(0,0,0,0.15); 
        margin-bottom: 25px; 
        border-left: 12px solid #0047AB; 
        color: #1e1e1e !important;
    }
    
    .header-card { 
        display: flex; flex-wrap: wrap; align-items: center; gap: 8px; 
        border-bottom: 2px solid #f0f2f6; padding-bottom: 10px; margin-bottom: 15px; 
    }
    .tag-cidade { 
        background: #0047AB; color: white !important; padding: 4px 12px; 
        border-radius: 8px; font-weight: 800; font-size: 14px; text-transform: uppercase;
    }
    .nome-centro { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800; }
    
    .palestras-verde { 
        color: #065F46 !important; font-weight: 700; background: #D1FAE5; 
        padding: 10px; border-radius: 10px; margin: 12px 0; border: 1px solid #10B981;
    }
    
    .info-linha { margin: 8px 0; font-size: 15px; display: flex; gap: 8px; }
    .label-bold { font-weight: 800; color: #555; min-width: 100px; }
    
    .btn-row { display: flex; gap: 12px; margin-top: 20px; }
    .btn-link { 
        text-decoration: none !important; color: white !important; 
        padding: 14px; border-radius: 12px; font-weight: 800; 
        text-align: center; flex: 1; transition: 0.2s;
    }
    .bg-wa { background-color: #25D366; box-shadow: 0 4px 12px rgba(37,211,102,0.3); }
    .bg-maps { background-color: #4285F4; box-shadow: 0 4px 12px rgba(66,133,244,0.3); }
    .btn-link:hover { transform: translateY(-2px); filter: brightness(1.1); }
</style>
""", unsafe_allow_html=True)

def renderizar_card(row):
    nome = str(row.get('NOME', 'Centro Espírita')).strip()
    end = str(row.get('ENDERECO', 'N/I')).strip()
    cid = str(row.get('CIDADE DO CENTRO ESPIRITA', 'N/I')).strip()
    palestras = str(row.get('PALESTRA PUBLICA', 'Consulte')).strip()
    resp = str(row.get('RESPONSAVEL', 'N/I')).strip()
    
    # WhatsApp Limpeza
    whats_num = "".join(filter(str.isdigit, str(row.get('CELULAR', ''))))
    link_wa = f"https://wa.me{whats_num}" if len(whats_num) >= 10 else "#"
    
    # Maps Query
    query_maps = urllib.parse.quote(f"{nome}, {end}, {cid}")
    link_maps = f"https://www.google.com{query_maps}"

    st.markdown(f"""
    <div class="card-centro">
        <div class="header-card">
            <span class="tag-cidade">🏙️ {cid}</span>
            <span class="nome-centro">{nome} 🕊️</span>
        </div>
        
        <div class="palestras-verde">🗣️ PALESTRAS: {palestras}</div>
        
        <div class="info-linha"><span class="label-bold">📍 ENDEREÇO:</span> <span>{end}</span></div>
        <div class="info-linha"><span class="label-bold">👤 RESPONS.:</span> <span>{resp}</span></div>

        <div class="btn-row">
            <a href="{link_maps}" target="_blank" class="btn-link bg-maps">📍 GOOGLE MAPS</a>
            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WHATSAPP</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- SISTEMA ---
if "logado" not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🕊️ Guia Espírita")
    with st.form("login"):
        u = st.text_input("E-mail")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR GUIA"):
            st.session_state.logado = True
            st.rerun()
else:
    with st.sidebar:
        st.markdown("### ☰ MENU")
        opcao = st.radio("Escolha uma opção:", ["Início", "🔎 Pesquisar Geral", "📍 Por Cidade", "🚪 Sair"])
        if opcao == "🚪 Sair":
            st.session_state.logado = False
            st.rerun()

    try:
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"Erro: {e}")
        st.stop()

    if opcao == "Início":
        st.title("🕊️ Guia Espírita")
        st.info("Abra o menu lateral para pesquisar centros.")

    elif opcao == "🔎 Pesquisar Geral":
        termo = st.text_input("Digite o que procura (Nome, Cidade, etc):")
        if termo:
            mask = df.astype(str).apply(lambda x: x.str.contains(termo, case=False)).any(axis=1)
            for _, row in df[mask].iterrows():
                renderizar_card(row)

    elif opcao == "📍 Por Cidade":
        cidades = sorted(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique())
        sel = st.selectbox("Selecione a Cidade:", ["-- Selecione --"] + cidades)
        if sel != "-- Selecione --":
            for _, row in df[df['CIDADE DO CENTRO ESPIRITA'] == sel].iterrows():
                renderizar_card(row)
