import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);}
.titulo-premium { 
    background: linear-gradient(90deg, #0047AB, #1976D2); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    text-shadow: 0 4px 12px rgba(0,71,171,0.3); 
    font-size: 2.5rem !important; 
    font-weight: 800 !important;
    color: white !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 20px !important;
    text-align: center !important;
    margin: 0 auto !important;
}
.titulo-premium::before, .titulo-premium::after {
    content: "🕊️" !important;
    font-size: 2.5rem !important;
    filter: brightness(0) saturate(100%) invert(100%) !important;
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
.search-input {width: 100%; padding: 16px 20px 16px 50px !important; border-radius: 12px !important; border: 2px solid #E5E7EB !important; font-size: 16px !important; transition: all 0.2s !important; background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' fill='%239C92AC' viewBox='0 0 16 16'%3E%3Cpath d='M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z'/%3E%3C/svg%3E") no-repeat 16px center !important;}
.search-input:focus {border-color: #3B82F6 !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important; background-size: 18px !important;}
@media (max-width: 768px) {.nome-grande {font-size: 28px !important;}.nome-fantasia {font-size: 20px !important;}.info-texto {font-size: 16px !important;}.stButton > button {height: 55px !important;font-size: 18px !important;}}
</style>""", unsafe_allow_html=True)

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# BUSCA FLEXÍVEL MELHORADA - VARIACOES DE NOMES
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

# VARIACOES COMUNS DE NOMES
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
    st.markdown('<h1 class="titulo-premium">Guia Espírita</h1>', unsafe_allow_html=True)
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
    st.markdown('<h1 class="titulo-premium">Guia Espírita</h1>', unsafe_allow_html=True)
    
    # ✅ CAMPO LIMPO COM LUPA DISCRETA
    busca = st.text_input(
        "",  # Label vazio
        placeholder="Ex: Joana, São Paulo, João, Luiz...",
        label_visibility="collapsed",
        key="busca_principal"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔎 **PESQUISAR**", use_container_width=True):
            if busca.strip():
                st.session_state.tem_busca = busca.strip()
                st.rerun()
    with col2:
        if st.button("🧹 **LIMPAR**", use_container_width=True):
            st.session_state.tem_busca = ""
            st.rerun()
    
    # EXECUTA BUSCA MELHORADA
    termo = st.session_state.get("tem_busca", "").strip()
    if termo:
        try:
            with st.spinner('🔍 Buscando com variações de nomes...'):
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
                
                # 🔍 BUSCA FLEXÍVEL EM MÚLTIPLAS COLUNAS
                todas_variacoes = expandir_variacoes(termo)
                resultados = []
                
                for idx, row in df.iterrows():
                    texto_row = " ".join([
                        limpar_busca(row.get('Nome Fantasia', '')),
                        limpar_busca(row.get('Nome Real / Razão Social', '')),
                        limpar_busca(row.get('Cidade', '')),
                        limpar_busca(row.get('Endereço', '')),
                        limpar_busca(row.get('Responsável', '')),
                        limpar_busca(row.get('Palestra Pública', ''))
                    ])
                    
                    # ✅ VERIFICA QUALQUER VARIAÇÃO DO TERMO
                    if any(variacao in texto_row for variacao in todas_variacoes):
                        resultados.append(row)
                
                if resultados:
                    df_resultados = pd.DataFrame(resultados)
                    st.success(f"✨ {len(resultados)} resultado{'s' if len(resultados) != 1 else ''} para '{termo}'")
                    
                    for idx, row in df_resultados.iterrows():
                        v_fantasia = str(row.get('Nome Fantasia', 'N/I'))
                        v_nome_real = str(row.get('Nome Real / Razão Social', 'Centro')) + " 🕊️"
                        v_cidade = str(row.get('Cidade', 'N/I'))
                        v_endereco = str(row.get('Endereço', 'N/I'))
                        v_resp = str(row.get('Responsável', 'N/I'))
                        v_celular = str(row.get('Celular', ''))
                        v_palestra = str(row.get('Palestra Pública', 'N/I'))

                        st.markdown(f"""
                        <div class="card-centro">
                            <div class="nome-grande">{v_nome_real}</div>
                            <div class="nome-fantasia">{v_fantasia}</div>
                            <div class="palestra-info">🗣️ <b>Palestras:</b> {v_palestra}</div>
                            <div class="info-texto">👤 <b>Responsável:</b> {v_resp}</div>
                            <div class="info-texto">📍 <b>Endereço:</b> {v_endereco}</div>
                            <div class="info-texto">🏙️ <b>Cidade:</b> {v_cidade}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        col1, col2 = st.columns(2)
                        with col1:
                            if 'N/I' not in v_endereco and v_endereco.strip():
                                query = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                                st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}", use_container_width=True)
                        with col2:
                            numero = ''.join(filter(str.isdigit, v_celular))
                            if len(numero) >= 10:
                                st.link_button("💬 WhatsApp", f"https://wa.me/55{numero}", use_container_width=True)
                        st.divider()
                else:
                    st.info(f"❌ Nada encontrado para '{termo}'. Tente: Joana (acha Joanna), São Paulo, João, Luiz...")
                    
        except FileNotFoundError:
            st.error("❌ guia.xlsx não encontrado!")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
    
    st.markdown("---")
    col_spacer, col_logout = st.columns([5, 1])
    with col_logout:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logado = False
            st.session_state.tem_busca = ""
            st.rerun()
