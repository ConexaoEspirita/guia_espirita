import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);}
.titulo-premium {background: linear-gradient(90deg, #0047AB, #1976D2);-webkit-background-clip: text;-webkit-text-fill-color: transparent;text-shadow: 0 4px 12px rgba(0,71,171,0.3);font-size: 2.5rem !important;font-weight: 800 !important;}
.card-centro {background: rgba(255,255,255,0.95);backdrop-filter: blur(10px);padding: 20px;border-radius: 20px;border: 1px solid rgba(0,71,171,0.1);box-shadow: 0 8px 32px rgba(0,71,171,0.15);margin-bottom: 16px;}
.nome-grande {color: #1E3A8A !important;font-size: 22px !important;font-weight: 800 !important;}
.nome-fantasia {color: #3B82F6 !important;font-size: 15px !important;font-weight: 600 !important;font-style: italic;}
.info-texto {color: #374151 !important;font-size: 13px !important;display: flex;align-items: center;gap: 6px;}
.palestras-verde {color: #10B981 !important; font-weight: 700 !important; font-size: 14px !important; background: rgba(16,185,129,0.15) !important; padding: 8px 14px !important; border-radius: 12px !important; border-left: 4px solid #10B981 !important; box-shadow: 0 2px 8px rgba(16,185,129,0.2) !important;}
div.stButton > button {background: linear-gradient(135deg, #0047AB, #1E40AF) !important;color: white !important;border-radius: 12px !important;height: 50px !important;font-size: 16px !important;font-weight: 700 !important;box-shadow: 0 4px 12px rgba(0,71,171,0.4) !important;transition: all 0.2s !important;}
div.stButton > button:hover {box-shadow: 0 6px 20px rgba(0,71,171,0.6) !important;transform: translateY(-2px) !important;}
div.stButton > button:active {transform: translateY(0px) !important;box-shadow: 0 2px 8px rgba(0,71,171,0.3) !important;}
div.stLinkButton > a {background: linear-gradient(135deg, #10B981, #059669) !important;color: white !important;border-radius: 12px !important;height: 44px !important;font-size: 15px !important;}
div[data-testid="stTextInputBlock"] > label > div > small {display: none !important;}
div[data-testid="stInfoBlock"] div {display: none !important;}
#back-to-top-fixed {position: fixed !important; bottom: 30px !important; right: 30px !important; background: linear-gradient(135deg, #10B981, #059669) !important; color: white !important; border: none !important; border-radius: 50px !important; width: 60px !important; height: 60px !important; font-size: 24px !important; cursor: pointer !important; box-shadow: 0 6px 20px rgba(16,185,129,0.4) !important; z-index: 99999 !important; display: block !important;}
#back-to-top-fixed:hover {transform: translateY(-3px) !important; box-shadow: 0 8px 25px rgba(16,185,129,0.6) !important;}
.metric-container {background: rgba(16,185,129,0.1) !important; padding: 10px !important; border-radius: 12px !important; border-left: 4px solid #10B981 !important;}
@media (max-width: 768px) {.nome-grande {font-size: 28px !important;}.nome-fantasia {font-size: 20px !important;}.info-texto {font-size: 16px !important;}.stButton > button {height: 55px !important;font-size: 18px !important;} #back-to-top-fixed {bottom: 20px !important; right: 20px !important; width: 55px !important; height: 55px !important; font-size: 20px !important;}}
</style>""", unsafe_allow_html=True)

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    return texto

# INICIALIZA CONTADORES
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = ""
    st.session_state.total_entradas = 0
    st.session_state.total_saidas = 0

if not st.session_state.logado:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1,1])
    with col1:
        email = st.text_input("📧 E-mail")
    with col2:
        celular = st.text_input("📱 WhatsApp")
    
    if st.button("🚀 ENTRAR", use_container_width=True):
        if not email or not celular:
            st.error("❌ Preencha **email E celular**!")
        else:
            try:
                # SALVA ACESSO
                dados = {
                    "email": email.strip().lower(),
                    "celular": celular.strip(),
                    "data_entrada": pd.Timestamp.now().isoformat(),
                    "status": "ativo"
                }
                supabase.table("acessos_simples").upsert(dados).execute()
                
                # CONTADOR LOCAL
                st.session_state.total_entradas += 1
                st.session_state.logado = True
                st.session_state.usuario = email.strip()
                st.success("✅ Bem-vindo ao Guia Espírita!")
                st.rerun()
            except:
                st.error("❌ Erro ao conectar. Tente novamente!")
else:
    # === CONTADORES (SÓ VOCÊ VE) ===
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("👥 Total Entradas", st.session_state.total_entradas)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("🚪 Total Saídas", st.session_state.total_saidas)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<hr style="border: 2px solid #10B981; margin: 20px 0;">', unsafe_allow_html=True)
    
    # === BUSCA ===
    busca = st.text_input("🔍 Digite nome, cidade ou qualquer palavra...", label_visibility="collapsed")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔎 PESQUISAR", use_container_width=True):
            if busca.strip():
                st.session_state.tem_busca = busca.strip()
                st.rerun()
    with col2:
        if st.button("🗑️ LIMPAR", use_container_width=True):
            st.session_state.tem_busca = ""
            st.rerun()
    
    termo = st.session_state.get("tem_busca", "").strip()
    resultados = []
    
    if termo:
        try:
            with st.spinner('🔍 Buscando centros espíritas...'):
                df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
                if 'Unnamed: 0' in df.columns:
                    df = df.drop('Unnamed: 0', axis=1)
                
                df.columns = df.columns.str.strip()
                df = df.rename(columns={
                    'NOME FANTASIA': 'Nome Fantasia',
                    'NOME': 'Nome Real / Razão Social',
                    'CIDADE DO CENTRO ESPIRITA': 'Cidade',
                    'ENDERECO': 'Endereço',
                    'PALESTRA PUBLICA': 'Palestra Pública',
                    'RESPONSAVEL': 'Responsável',
                    'CELULAR': 'Celular'
                })

                termo_limpo = limpar_busca(termo)
                for idx, row in df.iterrows():
                    texto_row = " ".join([
                        limpar_busca(row.get('Nome Fantasia', '')),
                        limpar_busca(row.get('Nome Real / Razão Social', '')),
                        limpar_busca(row.get('Cidade', '')),
                        limpar_busca(row.get('Endereço', '')),
                        limpar_busca(row.get('Responsável', '')),
                        limpar_busca(row.get('Palestra Pública', ''))
                    ])
                    if termo_limpo in texto_row:
                        resultados.append(row.to_dict())
        except FileNotFoundError:
            st.error("❌ Arquivo guia.xlsx NÃO ENCONTRADO!")
        except Exception as e:
            st.error(f"❌ ERRO: {str(e)}")
    
    if resultados:
        st.success(f"✨ Encontrados {len(resultados)} centro{'s' if len(resultados) != 1 else ''}!")
        
        for idx, row in pd.DataFrame(resultados).iterrows():
            v_fantasia = str(row.get('Nome Fantasia', 'N/I'))
            v_nome_real = str(row.get('Nome Real / Razão Social', 'Centro Espírita')) + " 🕊️"
            v_cidade = str(row.get('Cidade', 'N/I'))
            v_endereco = str(row.get('Endereço', 'N/I'))
            v_resp = str(row.get('Responsável', 'N/I'))
            v_celular = str(row.get('Celular', ''))
            v_palestras = str(row.get('Palestra Pública', ''))

            st.markdown(f"""
            <div class="card-centro" style="position: relative;">
                <div class="nome-grande">{v_nome_real}</div>
                <div class="nome-fantasia">{v_fantasia}</div>
                <div class="palestras-verde">🗣️ PALESTRAS {v_palestras}</div>
                <div class="info-texto">👤 <b>Responsável:</b> {v_resp}</div>
                <div class="info-texto">📍 <b>Endereço:</b> {v_endereco}</div>
                <div class="info-texto">🏙️ <b>Cidade:</b> {v_cidade}</div>
                <div style="position: absolute; bottom: 12px; right: 16px; background: linear-gradient(135deg, #10B981, #059669); color: white; border-radius: 20px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; box-shadow: 0 2px 8px rgba(16,185,129,0.3);">{int(idx)+1}</div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if 'N/I' not in v_endereco and v_endereco != 'N/I':
                    query = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                    st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}", use_container_width=True)
            with col2:
                numero = ''.join(filter(str.isdigit, v_celular))
                if len(numero) >= 10:
                    st.link_button("💬 WhatsApp", f"https://wa.me/55{numero}", use_container_width=True)
            st.divider()
    
    # ESPAÇO PARA SCROLL
    st.markdown('<div style="height: 100vh;"></div>', unsafe_allow_html=True)
    
    # BOTÃO VOLTAR AO TOPO - SEMPRE VISÍVEL
    st.markdown("""
    <button onclick="window.scrollTo({top: 0, behavior: 'smooth'})" 
            id="back-to-top-fixed"
            title="⬆️ Voltar ao topo"
            style="position: fixed !important; bottom: 30px !important; right: 30px !important; 
                   background: linear-gradient(135deg, #10B981, #059669) !important; 
                   color: white !important; border: none !important; 
                   border-radius: 50px !important; width: 60px !important; height: 60px !important; 
                   font-size: 24px !important; cursor: pointer !important; 
                   box-shadow: 0 6px 20px rgba(16,185,129,0.4) !important;
                   z-index: 99999 !important; display: block !important;">⬆️</button>
    """, unsafe_allow_html=True)
    
    col_spacer, col_logout = st.columns([5, 1])
    with col_logout:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.total_saidas += 1  # CONTA SAÍDA
            st.session_state.logado = False
            if "tem_busca" in st.session_state:
                del st.session_state.tem_busca
            st.rerun()
