import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS SEM CORTES E BOTÕES REAIS ---
st.markdown("""
<style>
    .stApp { background: #f0f2f6; }
    .card-centro { 
        background: white; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 20px; 
        border-left: 8px solid #0047AB;
    }
    .nome-grande { color: #1E3A8A; font-size: 22px; font-weight: 800; margin: 0; }
    .nome-fantasia { color: #3B82F6; font-size: 15px; font-style: italic; margin-bottom: 10px; }
    .palestras-verde { 
        color: #10B981; font-weight: 700; background: rgba(16,185,129,0.1); 
        padding: 8px; border-radius: 8px; margin: 10px 0; border: 1px solid #10B981;
    }
    .btn-row { display: flex; gap: 10px; margin-top: 15px; }
    .btn-link { 
        text-decoration: none !important; color: white !important; 
        padding: 12px 20px; border-radius: 10px; font-weight: bold; 
        display: inline-block; text-align: center; flex: 1;
    }
    .bg-wa { background-color: #25D366; }
    .bg-maps { background-color: #4285F4; }
</style>
""", unsafe_allow_html=True)

# --- CONFIG SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except:
    st.error("Configure as Secrets do Supabase!")

if "logado" not in st.session_state: st.session_state.logado = False

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    st.title("🕊️ Guia Espírita - Login")
    with st.form("login"):
        user = st.text_input("E-mail")
        pw = st.text_input("Senha", type="password")
        if st.form_submit_button("ENTRAR"):
            st.session_state.logado = True
            st.rerun()

# --- TELA PRINCIPAL (LOGADO) ---
else:
    # MENU HAMBURGUER (SIDEBAR)
    with st.sidebar:
        st.header("☰ MENU")
        aba = st.radio("Escolha uma opção:", ["📍 Cidades", "⚙️ Admin", "🚪 Sair"])
        
        if aba == "🚪 Sair":
            st.session_state.logado = False
            st.rerun()

    if aba == "📍 Cidades":
        try:
            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            df.columns = df.columns.str.strip()
            
            # Filtro de Cidades no Menu
            lista_cidades = sorted(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique())
            cidade_selecionada = st.selectbox("Selecione a cidade:", lista_cidades)
            
            dados = df[df['CIDADE DO CENTRO ESPIRITA'] == cidade_selecionada]

            for _, row in dados.iterrows():
                nome = str(row.get('NOME', 'Centro Espírita'))
                endereco = str(row.get('ENDERECO', ''))
                cidade = str(row.get('CIDADE DO CENTRO ESPIRITA', ''))
                palestras = str(row.get('PALESTRA PUBLICA', 'Não informado'))
                responsavel = str(row.get('RESPONSAVEL', 'N/I'))
                
                # LIMPEZA DO WHATSAPP (SÓ NÚMEROS)
                cel_bruto = str(row.get('CELULAR', ''))
                cel_limpo = re.sub(r'\D', '', cel_bruto)
                
                # LINKS (ENCODED PARA FUNCIONAR)
                query_maps = urllib.parse.quote(f"{nome}, {endereco}, {cidade}")
                link_maps = f"https://www.google.com{query_maps}"
                link_wa = f"https://wa.me{cel_limpo}"

                # CARD VISUAL
                st.markdown(f"""
                <div class="card-centro">
                    <div class="nome-grande">{nome} 🕊️</div>
                    <div class="nome-fantasia">{row.get('NOME FANTASIA', '')}</div>
                    <div class="palestras-verde">🗣️ PALESTRAS: {palestras}</div>
                    <p style="margin:5px 0;">👤 <b>Responsável:</b> {responsavel}</p>
                    <p style="margin:5px 0;">📍 <b>Endereço:</b> {endereco}</p>
                    <div class="btn-row">
                        <a href="{link_maps}" target="_blank" class="btn-link bg-maps">📍 VER NO MAPA</a>
                        <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WHATSAPP</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erro ao carregar planilha: {e}")

    elif aba == "⚙️ Admin":
        st.title("Painel Administrativo")
        st.write("Configurações do sistema aqui.")
