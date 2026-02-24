import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #EBF4FA; }
.card-centro {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    border-left: 8px solid #0047AB;
    margin-bottom: 15px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.nome-grande { color: #0047AB; font-size: 26px; font-weight: bold; line-height: 1.1; }
.nome-fantasia { color: #5CACE2 !important; font-size: 17px !important; font-weight: 500; font-style: italic; margin-bottom: 12px; display: block; }
.info-texto { color: #444; font-size: 14px; margin-bottom: 4px; }
div.stLinkButton > a { width: 100% !important; font-weight: bold !important; height: 45px !important; display: flex !important; align-items: center !important; justify-content: center !important; }
.conta-pequena { font-size: 12px !important; color: #888 !important; margin-bottom: 10px !important; }
.botao-buscar { background-color: #0047AB !important; color: white !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def limpar_busca(texto):
    if pd.isna(texto):
        return ""
    texto = unicodedata.normalize('NFD', str(texto))
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto.lower()

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🕊️ Guia Espírita 🕊️")
    email = st.text_input("E-mail").strip().lower()
    senha = st.text_input("Senha", type="password")
    if st.button("ACESSAR GUIA"):
        resposta = supabase.table("acessos").select("*").eq("email", email).eq("senha", senha).execute()
        if resposta.data:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Dados incorretos!")
else:
    st.title("🕊️ Guia Espírita 🕊️")
    
    col_busca, col_botao = st.columns([3, 1])
    
    with col_busca:
        st.text_input("🔍 Nome do centro, cidade ou dia da semana", 
                     placeholder="Kardec, Icém, sexta-feira, Catanduva...", key="busca_input")
    
    with col_botao:
        if st.button("🔎 BUSCAR"):
            st.rerun()
    
    busca = st.session_state.get("busca_input", "").strip()
    
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
                st.markdown(f'<div class="conta-pequena">achou {len(resultados_df)} resultado{"s" if len(resultados_df) != 1 else ""}</div>', unsafe_allow_html=True)

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
                        <div class="info-texto">👤 <b>Responsável:</b> {v_resp}</div>
                        <div class="info-texto">📍 <b>Endereço:</b> {v_endereco}</div>
                        <div class="info-texto">🏙️ <b>Cidade:</b> {v_cidade}</div>
                        {f'<div class="info-texto">🗓️ <b>Palestra:</b> {v_palestra}</div>' if v_palestra.strip() else ''}
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        if 'Não informado' not in v_endereco:
                            query = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                            st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}")
                    with col2:
                        numero = ''.join(filter(str.isdigit, v_celular))
                        if len(numero) >= 10:
                            st.link_button("💬 WHATSAPP", f"https://wa.me/55{numero}")
                    st.divider()

            else:
                st.warning("Nenhum resultado encontrado.")
                
        except Exception as erro:
            st.error(f"Erro: {str(erro)}")
    else:
        st.info("Digite nome do centro, cidade ou dia da semana!")
