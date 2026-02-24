import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

st.markdown("""
<style>
.stApp { 
    background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);
}
.titulo-premium {
    background: linear-gradient(90deg, #0047AB, #1976D2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 4px 12px rgba(0,71,171,0.3);
    font-size: 2.5rem !important;
    font-weight: 800 !important;
}
.card-centro {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 20px;
    border: 1px solid rgba(0,71,171,0.1);
    box-shadow: 0 8px 32px rgba(0,71,171,0.15), 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 16px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.card-centro:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0,71,171,0.25);
}
.card-centro::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #0047AB, #5CACE2, #0047AB);
}
.nome-grande { 
    color: #1E3A8A !important;
    font-size: 22px !important; 
    font-weight: 800 !important; 
    line-height: 1.3;
    margin-bottom: 6px;
}
.nome-fantasia { 
    color: #3B82F6 !important;
    font-size: 15px !important; 
    font-weight: 600 !important; 
    font-style: italic; 
    margin-bottom: 10px;
}
.info-texto { 
    color: #374151 !important;
    font-size: 13px !important; 
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}
div.stLinkButton > a { 
    background: linear-gradient(135deg, #10B981, #059669) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    height: 44px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 16px rgba(16,185,129,0.4) !important;
    transition: all 0.2s ease !important;
}
div.stLinkButton > a:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(16,185,129,0.5) !important;
}
div.stButton > button {
    background: linear-gradient(135deg, #0047AB, #1E40AF) !important;
    color: white !important;
    border-radius: 12px !important;
    height: 48px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 16px rgba(0,71,171,0.4) !important;
}
.conta-pequena { 
    font-size: 12px !important; 
    color: #6B7280 !important; 
    margin-bottom: 12px !important;
    background: rgba(255,255,255,0.7);
    padding: 8px 12px;
    border-radius: 20px;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

def limpar_busca(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
    return ' '.join(texto.split())

# Config Supabase
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "SUA_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "SUA_CHAVE")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if 'df_centros' not in st.session_state:
    st.session_state.df_centros = None
if 'logado' not in st.session_state:
    st.session_state.logado = False

st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
st.markdown("---")

if not st.session_state.logado:
    st.info("👋 Bem-vindo! Faça login para acessar o guia completo.")
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("🔑 Login", use_container_width=True):
            st.session_state.logado = True
            st.rerun()
    st.markdown("---")
else:
    if st.session_state.df_centros is None:
        try:
            response = supabase.table('centros_espirita').select("*").execute()
            data = response.data
            st.session_state.df_centros = pd.DataFrame(data)
        except:
            st.warning("⚠️ Sem Supabase. Usando dados teste...")
            data_exemplo = [
                {"Nome Fantasia": "Luz Divina", "Nome Real / Razão Social": "Centro Espírita Luz Divina", "Cidade": "São Paulo", "Endereço": "Rua das Flores, 123", "Responsável": "Maria Silva", "Palestra Pública": "Sexta 20h", "Celular": "(11)99999-9999"},
                {"Nome Fantasia": "Paz Interior", "Nome Real / Razão Social": "Sociedade Espírita Paz Interior", "Cidade": "Rio de Janeiro", "Endereço": "Av. Beira Mar, 456", "Responsável": "João Santos", "Palestra Pública": "Domingo 18h", "Celular": "(21)98888-8888"},
                {"Nome Fantasia": "Amor Fraterno", "Nome Real / Razão Social": "Grupo Espírita Amor Fraterno", "Cidade": "Catanduva", "Endereço": "Rua Central, 789", "Responsável": "José Oliveira", "Palestra Pública": "", "Celular": "(17)97777-7777"}
            ]
            st.session_state.df_centros = pd.DataFrame(data_exemplo)
        st.success(f"✅ Carregados {len(st.session_state.df_centros)} centros")

    df = st.session_state.df_centros

    col_busca, col_filtros = st.columns([3, 1])
    with col_busca:
        busca = st.text_input("🔍 Buscar centro, cidade ou responsável...", placeholder="Ex: Centro Luz, São Paulo, João")
    with col_filtros:
        if st.button("🔄 Recarregar", use_container_width=True):
            st.session_state.df_centros = None
            st.rerun()

    termo = limpar_busca(busca)
    resultados = []
    
    for idx, row in df.iterrows():
        campos = [row.get('Nome Fantasia',''), row.get('Nome Real / Razão Social',''), 
                 row.get('Cidade',''), row.get('Endereço',''), 
                 row.get('Responsável',''), row.get('Palestra Pública','')]
        linha_completa = " ".join([limpar_busca(val) for val in campos])
        
        if termo in linha_completa:
            resultados.append(row)

    resultados_df = pd.DataFrame(resultados) if resultados else pd.DataFrame()

    if not resultados_df.empty:
        st.markdown(f'<div class="conta-pequena">✨ achou {len(resultados_df)} resultado{"s" if len(resultados_df) != 1 else ""}</div>', unsafe_allow_html=True)

        for _, row in resultados_df.iterrows():
            v_fantasia = str(row.get('Nome Fantasia', 'Não informado'))
            v_nome_real = str(row.get('Nome Real / Razão Social', 'Centro Espírita')) + " 🕊️"
            v_cidade = str(row.get('Cidade', 'Não informada'))
            v_endereco = str(row.get('Endereço', 'Não informado'))
            v_palestra = str(row.get('Palestra Pública', ''))
            v_resp = str(row.get('Responsável', 'Não informado'))
            v_celular = str(row.get('Celular', ''))

            st.markdown(f"""
            <div class="card-centro">
                <div class="nome-grande">{v_nome_real}</div>
                <div class="nome-fantasia">{v_fantasia}</div>
                <div class="info-texto"><span style='font-size:16px'>👤</span> <b>Responsável:</b> {v_resp}</div>
                <div class="info-texto"><span style='font-size:16px'>📍</span> <b>Endereço:</b> {v_endereco}</div>
                <div class="info-texto"><span style='font-size:16px'>🏙️</span> <b>Cidade:</b> {v_cidade}</div>
                {f'<div class="info-texto"><span style="font-size:16px">🗓️</span> <b>Palestra:</b> {v_palestra}</div>' if v_palestra.strip() else ''}
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if 'Não informado' not in v_endereco:
                    query = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                    st.link_button("🗺️ Ver no MAPS", f"https://www.google.com/maps/search/?api=1&query={query}", use_container_width=True)
            with col2:
                numero = ''.join(filter(str.isdigit, v_celular))
                if len(numero) >= 10:
                    st.link_button("💬 WhatsApp", f"https://wa.me/55{numero}", use_container_width=True)
            st.divider()
    else:
        if busca:
            st.warning("❌ Nenhum resultado encontrado.")
        else:
            st.info("✨ Digite nome do centro, cidade ou dia da semana!")
    
    st.markdown("---")
    col_spacer, col_logout = st.columns([5, 1])
    with col_logout:
        if st.button("🚪 Sair", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; font-size: 12px; padding: 20px;'>
    🕊️ Guia Espírita - Conectando corações em busca da luz ✨
</div>
""", unsafe_allow_html=True)
