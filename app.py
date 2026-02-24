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
    padding: 6px 12px;
    border-radius: 20px;
    display: inline-block;
}
@media (max-width: 768px) {
    .nome-grande { font-size: 28px !important; line-height: 1.2 !important; }
    .nome-fantasia { font-size: 20px !important; }
    .info-texto { font-size: 16px !important; line-height: 1.4 !important; padding: 8px 0 !important; }
    .card-centro { padding: 24px !important; margin-bottom: 20px !important; }
    div.stButton > button, div.stLinkButton > a { height: 52px !important; font-size: 18px !important; }
    div.stTextInput > div > div > input { font-size: 18px !important; padding: 16px !important; }
}
@media (max-width: 480px) {
    .nome-grande { font-size: 26px !important; }
    .nome-fantasia { font-size: 18px !important; }
    .info-texto { font-size: 15px !important; }
    .card-centro { padding: 20px !important; }
}
</style>""", unsafe_allow_html=True)

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def limpar_busca(texto):
    if pd.isna(texto):
        return ""
    texto = unicodedata.normalize('NFD', str(texto))
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\\w\\s]', ' ', texto.lower())
    return texto.strip()

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        email = st.text_input("📧 E-mail")
    with col2:
        senha = st.text_input("🔒 Senha", type="password")
    
    if st.button("🚀 ACESSAR GUIA", use_container_width=True):
        email_limpo = email.strip().lower()
        senha_limpa = senha.strip()
        
        resposta = supabase.table("acessos").select("*") \
            .eq("email", email_limpo) \
            .eq("senha", senha_limpa) \
            .execute()
            
        if resposta.data:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("❌ E-mail ou senha incorretos!")
else:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    
    col_busca, col_botao = st.columns([4, 1])
    with col_busca:
        busca_input = st.text_input("🔍 Procure centros espíritas", 
                                  placeholder="Digite nome, cidade ou dia...", 
                                  label_visibility="collapsed",
                                  value=st.session_state.get("busca", ""))
    with col_botao:
        if st.button("🔎", use_container_width=True):
            if busca_input.strip():
                st.session_state.busca = busca_input.strip()
                st.rerun()
    
    busca = st.session_state.get("busca", "").strip()
    
    if busca:
        try:
            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            if 'Unnamed: 0' in df.columns:
                df = df.drop('Unnamed: 0', axis=1)
            df.columns = [col.strip() for col in df.columns]
            
            df = df.rename(columns={
                'NOME FANTASIA': 'Nome Fantasia',
                'NOME': 'Nome Real / Razão Social',
                'CIDADE DO CENTRO ESPIRITA': 'Cidade',
                'ENDERECO': 'Endereço',
                'PALESTRA PUBLICA': 'Palestra Pública',
                'RESPONSAVEL': 'Responsável',
                'CELULAR': 'Celular'
            })
            
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

                for idx, row in resultados_df.iterrows():
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
                        <div class="info-texto"><span style='font-size:18px'>👤</span> <b>Responsável:</b> {v_resp}</div>
                        <div class="info-texto"><span style='font-size:18px'>📍</span> <b>Endereço:</b> {v_endereco}</div>
                        <div class="info-texto"><span style='font-size:18px'>🏙️</span> <b>Cidade:</b> {v_cidade}</div>
                        {f'<div class="info-texto"><span style="font-size:18px">🗓️</span> <b>Palestra:</b> {v_palestra}</div>' if v_palestra.strip() else ''}
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2 = st.columns([1,1])
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
                st.warning("❌ Nenhum resultado encontrado.")
        except FileNotFoundError:
            st.error("❌ Arquivo guia.xlsx não encontrado!")
        except Exception as erro:
            st.error(f"❌ Erro: {str(erro)}")
    else:
        st.info("✨ Digite nome do centro, cidade ou dia da semana!")
    
    st.markdown("---")
    col_spacer, col_logout = st.columns([5, 1])
    with col_logout:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logado = False
            st.rerun()
