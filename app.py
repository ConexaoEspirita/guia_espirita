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
.card-centro {background: rgba(255,255,255,0.95);backdrop-filter: blur(10px);padding: 20px;border-radius: 20px;border: 1px solid rgba(0,71,171,0.1);box-shadow: 0 8px 32px rgba(0,71,171,0.15);margin-bottom: 16px;transition: all 0.3s ease;}
.card-centro:hover {transform: translateY(-4px);box-shadow: 0 16px 48px rgba(0,71,171,0.25);}
.nome-grande {color: #1E3A8A !important;font-size: 22px !important;font-weight: 800 !important;line-height: 1.3;margin-bottom: 6px;}
.nome-fantasia {color: #3B82F6 !important;font-size: 15px !important;font-weight: 600 !important;font-style: italic;margin-bottom: 10px;}
.info-texto {color: #374151 !important;font-size: 13px !important;margin-bottom: 4px;display: flex;align-items: center;gap: 6px;}
div.stButton > button {background: linear-gradient(135deg, #0047AB, #1E40AF) !important;color: white !important;border-radius: 12px !important;height: 50px !important;font-size: 16px !important;font-weight: 700 !important;box-shadow: 0 4px 12px rgba(0,71,171,0.4) !important;transition: all 0.2s !important;transform: translateY(0);}
div.stButton > button:hover {box-shadow: 0 6px 20px rgba(0,71,171,0.6) !important;transform: translateY(-2px) !important;}
div.stButton > button:active {transform: translateY(0px) !important;box-shadow: 0 2px 8px rgba(0,71,171,0.3) !important;}
div.stLinkButton > a {background: linear-gradient(135deg, #10B981, #059669) !important;color: white !important;border-radius: 12px !important;height: 44px !important;font-size: 15px !important;font-weight: 700 !important;}
.conta-pequena {font-size: 12px !important;color: #6B7280 !important;margin-bottom: 12px !important;background: rgba(255,255,255,0.7);padding: 6px 12px;border-radius: 20px;display: inline-block;}
@media (max-width: 768px) {.nome-grande {font-size: 28px !important;}.nome-fantasia {font-size: 20px !important;}.info-texto {font-size: 16px !important;}.card-centro {padding: 24px !important;}.stButton > button {height: 55px !important;font-size: 18px !important;}.stLinkButton > a {height: 50px !important;font-size: 16px !important;}}
@media (max-width: 480px) {.nome-grande {font-size: 26px !important;}.info-texto {font-size: 15px !important;}}
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
    st.session_state.ultima_busca = ""

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
        resposta = supabase.table("acessos").select("*").eq("email", email_limpo).eq("senha", senha_limpa).execute()
        if resposta.data:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("❌ E-mail ou senha incorretos!")
else:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    
    # Campo de busca SIMPLES
    busca = st.text_input("🔍 Procure centros espíritas", 
                         placeholder="Nome do centro, cidade ou responsável...", 
                         value=st.session_state.ultima_busca,
                         label_visibility="collapsed")
    
    # Botão PESQUISAR com feedback visual (AFUNDA NO CELULAR)
    if st.button("🔎 PESQUISAR", use_container_width=True, help="Clique para buscar!"):
        if busca.strip():
            st.session_state.ultima_busca = busca.strip()
            st.session_state.busca_resultados = True
            st.rerun()
        else:
            st.warning("❌ Digite algo para pesquisar!")
    
    # Limpar busca
    if st.button("🗑️ LIMPAR", use_container_width=True):
        st.session_state.ultima_busca = ""
        st.session_state.busca_resultados = False
        st.rerun()
    
    # EXECUTA BUSCA
    if st.session_state.get("busca_resultados", False) and st.session_state.ultima_busca.strip():
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
            
            termo = limpar_busca(st.session_state.ultima_busca)
            resultados = []
            
            for idx, row in df.iterrows():
                campos = [
                    limpar_busca(row.get('Nome Fantasia','')),
                    limpar_busca(row.get('Nome Real / Razão Social','')),
                    limpar_busca(row.get('Cidade','')),
                    limpar_busca(row.get('Responsável',''))
                ]
                if any(termo in campo for campo in campos if campo and len(termo) >= 2):
                    resultados.append(row)

            if resultados:
                st.markdown(f'<div class="conta-pequena">✨ Encontrados {len(resultados)} centro{"s" if len(resultados) != 1 else ""}!</div>', unsafe_allow_html=True)
                
                for idx, row in pd.DataFrame(resultados).iterrows():
                    v_fantasia = str(row.get('Nome Fantasia', 'Não informado'))
                    v_nome_real = str(row.get('Nome Real / Razão Social', 'Centro Espírita')) + " 🕊️"
                    v_cidade = str(row.get('Cidade', 'Não informada'))
                    v_endereco = str(row.get('Endereço', 'Não informado'))
                    v_resp = str(row.get('Responsável', 'Não informado'))
                    v_celular = str(row.get('Celular', ''))

                    st.markdown(f"""
                    <div class="card-centro">
                        <div class="nome-grande">{v_nome_real}</div>
                        <div class="nome-fantasia">{v_fantasia}</div>
                        <div class="info-texto">👤 <b>Responsável:</b> {v_resp}</div>
                        <div class="info-texto">📍 <b>Endereço:</b> {v_endereco}</div>
                        <div class="info-texto">🏙️ <b>Cidade:</b> {v_cidade}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        if 'Não informado' not in v_endereco:
                            query = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                            st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}", use_container_width=True)
                    with col2:
                        numero = ''.join(filter(str.isdigit, v_celular))
                        if len(numero) >= 10:
                            st.link_button("💬 WhatsApp", f"https://wa.me/55{numero}", use_container_width=True)
                    st.divider()
            else:
                st.warning("❌ Nenhum centro encontrado. Tente outro termo!")
                
        except FileNotFoundError:
            st.error("❌ Arquivo guia.xlsx não encontrado!")
        except Exception as erro:
            st.error(f"❌ Erro: {str(erro)}")
    
    st.markdown("---")
    col_spacer, col_logout = st.columns([5, 1])
    with col_logout:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logado = False
            st.session_state.ultima_busca = ""
            st.session_state.busca_resultados = False
            st.rerun()
