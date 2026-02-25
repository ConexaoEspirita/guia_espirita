import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# --- CSS TOTALMENTE CORRIGIDO ---
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
    .stApp { background: #f0f2f6; }
    .card-centro { 
        background: white; padding: 25px; border-radius: 15px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 25px; 
        border-left: 10px solid #0047AB; color: #1e1e1e !important;
    }
    .nome-grande { color: #1E3A8A !important; font-size: 24px !important; font-weight: 800; margin: 0; }
    .palestras-verde { 
        color: #065F46 !important; font-weight: 700; background: #D1FAE5; 
        padding: 10px; border-radius: 8px; margin: 12px 0; border: 1px solid #10B981;
    }
    .btn-row { display: flex; gap: 15px; margin-top: 20px; }
    .btn-link { 
        text-decoration: none !important; color: white !important; 
        padding: 15px; border-radius: 12px; font-weight: 800; 
        text-align: center; flex: 1; transition: 0.3s;
    }
    .bg-wa { background-color: #25D366; }
    .bg-maps { background-color: #4285F4; }
</style>
""", unsafe_allow_html=True)

# --- LOGIN / SESSION ---
if "logado" not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🕊️ Guia Espírita")
    with st.form("login_form"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR"):
            st.session_state.logado = True
            st.rerun()
else:
    # --- O MENU HAMBÚRGUER (SIDEBAR) ---
    with st.sidebar:
        st.header("☰ MENU PRINCIPAL")
        # Aqui você escolhe o que quer ver. Por padrão, começa em "Início" (vazio)
        opcao = st.selectbox("Navegar para:", ["Selecione...", "📍 Cidades", "⚙️ Admin", "🚪 Sair"])
        
        if opcao == "🚪 Sair":
            st.session_state.logado = False
            st.rerun()

    # --- LÓGICA DE EXIBIÇÃO ---
    if opcao == "Selecione...":
        st.subheader("Bem-vindo ao Guia Espírita! 🕊️")
        st.info("Clique no menu (ícone no topo esquerdo) para listar as Cidades ou acessar o Admin.")

    elif opcao == "📍 Cidades":
        try:
            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            df.columns = df.columns.str.strip()
            
            cidades = sorted(df['CIDADE DO CENTRO ESPIRITA'].dropna().unique())
            escolha = st.selectbox("Escolha a Cidade:", ["-- Selecione --"] + cidades)
            
            if escolha != "-- Selecione --":
                dados = df[df['CIDADE DO CENTRO ESPIRITA'] == escolha]
                
                for _, row in dados.iterrows():
                    nome = str(row.get('NOME', 'Centro Espírita'))
                    end = str(row.get('ENDERECO', ''))
                    cid = str(row.get('CIDADE DO CENTRO ESPIRITA', ''))
                    resp = str(row.get('RESPONSAVEL', 'N/I'))
                    
                    # Limpeza do WhatsApp
                    whats = re.sub(r'\D', '', str(row.get('CELULAR', '')))
                    link_wa = f"https://wa.me{whats}"
                    
                    # Link Maps
                    link_maps = f"https://www.google.com{urllib.parse.quote(f'{nome} {end} {cid}')}"

                    st.markdown(f"""
                    <div class="card-centro">
                        <div class="nome-grande">{nome} 🕊️</div>
                        <div class="palestras-verde">🗣️ PALESTRAS: {row.get('PALESTRA PUBLICA', 'Consulte')}</div>
                        <p>👤 <b>Responsável:</b> {resp}</p>
                        <p>📍 <b>Endereço:</b> {end}</p>
                        <div class="btn-row">
                            <a href="{link_maps}" target="_blank" class="btn-link bg-maps">📍 GOOGLE MAPS</a>
                            <a href="{link_wa}" target="_blank" class="btn-link bg-wa">💬 WHATSAPP</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro: {e}")

    elif opcao == "⚙️ Admin":
        st.title("Área Administrativa")
        st.write("Somente pessoal autorizado.")
