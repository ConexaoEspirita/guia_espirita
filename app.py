import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS Corrigido (Sem cortes e com botões funcionais) ---
st.markdown("""
<style>
.block-container { padding-top: 1rem !important; }
.stApp { background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%); }
.titulo-premium { background: linear-gradient(90deg, #0047AB, #1976D2);
-webkit-background-clip: text; -webkit-text-fill-color: transparent;
font-size: 2.5rem !important; font-weight: 800 !important; text-align: center; }

.card-centro { background: rgba(255,255,255,0.95); padding: 20px; border-radius: 20px; 
border: 1px solid rgba(0,71,171,0.1); box-shadow: 0 8px 32px rgba(0,71,171,0.15); margin-bottom: 20px; }

.nome-grande { color: #1E3A8A !important; font-size: 22px !important; font-weight: 800 !important; line-height: 1.2; }
.nome-fantasia { color: #3B82F6 !important; font-size: 15px !important; font-weight: 600 !important; font-style: italic; margin-bottom: 10px; }
.info-texto { color: #374151 !important; font-size: 14px !important; margin: 5px 0; display: flex; align-items: center; gap: 8px; }

.palestras-verde { color: #10B981 !important; font-weight: 700 !important; font-size: 14px !important; 
background: rgba(16,185,129,0.15) !important; padding: 8px 14px !important; border-radius: 12px !important; 
border-left: 4px solid #10B981 !important; margin: 10px 0; }

.btn-container { display: flex; gap: 10px; margin-top: 15px; }
.btn-link { text-decoration: none !important; color: white !important; padding: 10px 20px; border-radius: 10px; 
font-weight: bold; font-size: 14px; display: inline-flex; align-items: center; justify-content: center; min-width: 120px; }
.btn-whatsapp { background-color: #25D366; box-shadow: 0 4px 10px rgba(37,211,102,0.3); }
.btn-maps { background-color: #4285F4; box-shadow: 0 4px 10px rgba(66,133,244,0.3); }
</style>
""", unsafe_allow_html=True)

# --- Funções ---
def limpar_texto(texto):
    if pd.isna(texto): return ""
    return str(texto).strip()

# --- Conexão Supabase ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

if "logado" not in st.session_state: st.session_state.logado = False

# --- Lógica de Acesso ---
if not st.session_state.logado:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1,2,1])
    with col_c:
        aba = st.tabs(["Login", "Cadastro"])
        with aba[0]:
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.button("ACESSAR SISTEMA"):
                st.session_state.logado = True
                st.rerun()
else:
    # --- Menu Lateral (Hambúrguer) ---
    with st.sidebar:
        st.markdown("## ☰ Menu")
        menu = st.radio("Navegação", ["Cidades", "Admin", "Sair"])
        if menu == "Sair":
            st.session_state.logado = False
            st.rerun()

    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)

    try:
        df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
        df.columns = df.columns.str.strip()
        col_cidade = 'CIDADE DO CENTRO ESPIRITA'

        if menu == "Cidades":
            cidades = sorted(df[col_cidade].dropna().unique())
            escolha_cidade = st.selectbox("📍 Selecione a Cidade", cidades)
            
            centros = df[df[col_cidade] == escolha_cidade]

            for idx, row in centros.iterrows():
                v_nome = limpar_texto(row.get('NOME', 'Centro Espírita'))
                v_fantasia = limpar_texto(row.get('NOME FANTASIA', ''))
                v_endereco = limpar_texto(row.get('ENDERECO', 'Endereço não informado'))
                v_resp = limpar_texto(row.get('RESPONSAVEL', 'Não informado'))
                v_palestras = limpar_texto(row.get('PALESTRA PUBLICA', 'Consulte a casa'))
                
                # Tratar Celular para Link
                cel_raw = str(row.get('CELULAR', ''))
                cel_limpo = re.sub(r'\D', '', cel_raw)
                
                # Links Dinâmicos
                link_maps = f"https://www.google.com{urllib.parse.quote(f'{v_nome} {v_endereco} {escolha_cidade}')}"
                link_wa = f"https://wa.me{cel_limpo}" if len(cel_limpo) >= 10 else None

                st.markdown(f"""
                <div class="card-centro">
                    <div class="nome-grande">{v_nome} 🕊️</div>
                    <div class="nome-fantasia">{v_fantasia}</div>
                    <div class="palestras-verde">🗣️ PALESTRAS: {v_palestras}</div>
                    <div class="info-texto">👤 <b>Responsável:</b> {v_resp}</div>
                    <div class="info-texto">📍 <b>Endereço:</b> {v_endereco}</div>
                    <div class="btn-container">
                        <a href="{link_maps}" target="_blank" class="btn-link btn-maps">📍 VER MAPA</a>
                        {f'<a href="{link_wa}" target="_blank" class="btn-link btn-whatsapp">💬 WHATSAPP</a>' if link_wa else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        elif menu == "Admin":
            st.info("Painel administrativo em desenvolvimento.")

    except Exception as e:
        st.error(f"Erro ao ler planilha: {e}")
