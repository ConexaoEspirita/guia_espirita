import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);}
.titulo-container {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 25px !important;
    width: 100% !important;
    margin: 0 auto 40px !important;
    padding: 20px 0 !important;
}
.titulo-premium { 
    background: linear-gradient(90deg, #0047AB, #1976D2) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    color: white !important;
    font-size: 2.5rem !important; 
    font-weight: 800 !important;
    text-shadow: 0 4px 12px rgba(0,71,171,0.5) !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}
.pombinha {
    font-size: 2.5rem !important;
    margin: 0 !important;
}
.card-centro {background: rgba(255,255,255,0.95);backdrop-filter: blur(10px);padding: 20px;border-radius: 20px;border: 1px solid rgba(0,71,171,0.1);box-shadow: 0 8px 32px rgba(0,71,171,0.15);margin-bottom: 16px;}
.nome-grande {color: #1E3A8A !important;font-size: 22px !important;font-weight: 800 !important;}
.nome-fantasia {color: #3B82F6 !important;font-size: 15px !important;font-weight: 600 !important;font-style: italic;}
.info-texto {color: #374151 !important;font-size: 13px !important;display: flex;align-items: center;gap: 6px;}
.palestra-info {color: #059669 !important;font-size: 14px !important;font-weight: 600 !important;display: flex;align-items: center;gap: 8px;}
div.stButton > button {background: linear-gradient(135deg, #0047AB, #1E40AF) !important;color: white !important;border-radius: 12px !important;height: 50px !important;font-size: 16px !important;font-weight: 700 !important;box-shadow: 0 4px 12px rgba(0,71,171,0.4) !important;transition: all 0.2s !important;}
div.stButton > button:hover {box-shadow: 0 6px 20px rgba(0,71,171,0.6) !important;transform: translateY(-2px) !important;}
div.stButton > button:active {transform: translateY(0px) !important;box-shadow: 0 2px 8px rgba(0,71,171,0.3) !important;}
div.stLinkButton > a {background: linear-gradient(135deg, #10B981, #059669) !important;color: white !important;border-radius: 12px !important;height: 44px !important;font-size: 15px !important;}
.search-container input { 
    width: 100%; 
    padding: 16px 20px 16px 50px !important; 
    border-radius: 12px !important; 
    border: 2px solid #E5E7EB !important; 
    font-size: 16px !important; 
    transition: all 0.2s !important; 
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' fill='%239C92AC' viewBox='0 0 16 16'%3E%3Cpath d='M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z'/%3E%3C/svg%3E") no-repeat 16px center !important;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.15) !important;
}
.search-container input:focus { 
    border-color: #10B981 !important; 
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2) !important, 0 4px 12px rgba(16, 185, 129, 0.3) !important;
}
@media (max-width: 768px) {.nome-grande {font-size: 28px !important;}.nome-fantasia {font-size: 20px !important;}.info-texto {font-size: 16px !important;}.stButton > button {height: 55px !important;font-size: 18px !important;}}
</style>""", unsafe_allow_html=True)

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def limpar_busca(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower().strip()
    texto = re.sub(r'[àáâãäå]', 'a', texto)
    texto = re.sub(r'[èéêë]', 'e', texto)
    texto = re.sub(r'[ìíîï]', 'i', texto)
    texto = re.sub(r'[òóôõö]', 'o', texto)
    texto = re.sub(r'[ùúûü]', 'u', texto)
    texto = re.sub(r'[ç]', 'c', texto)
    return re.sub(r'[^a-z0-9\s]', '', texto)

def expandir_variacoes(termo):
    variacoes = {
        'joana': ['joana', 'joanna', 'johanna', 'joanne', 'juana'],
        'maria': ['maria', 'marie', 'mariana', 'mary', 'maira'],
        'ana': ['ana', 'anna', 'anne', 'ania'],
        'luiz': ['luiz', 'luis', 'luís', 'lewis'],
        'carlos': ['carlos', 'charles'],
        'fernando': ['fernando', 'nando'],
        'joao': ['joao', 'joão', 'john', 'jonas'],
        'pedro': ['pedro', 'peter'],
        'francisco': ['francisco', 'francis', 'chico']
    }
    termo_limpo = limpar_busca(termo)
    if termo_limpo in variacoes:
        return variacoes[termo_limpo]
    return [termo_limpo]

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
