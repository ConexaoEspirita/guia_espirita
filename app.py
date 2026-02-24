import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="centered")
st.cache_data.clear()

# ==============================
# ESTILO VISUAL
# ==============================
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
.nome-grande {
    color: #0047AB;
    font-size: 26px;
    font-weight: bold;
    line-height: 1.1;
}
.nome-fantasia {
    color: #5CACE2 !important;
    font-size: 17px !important;
    font-weight: 500;
    font-style: italic;
    margin-bottom: 12px;
    display: block;
}
.info-texto {
    color: #444;
    font-size: 14px;
    margin-bottom: 4px;
}
div.stLinkButton > a {
    width: 100% !important;
    font-weight: bold !important;
    height: 45px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# CONEXÃO SUPABASE
# ==============================
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ==============================
# FUNÇÕES AUXILIARES
# ==============================
def limpar_busca(texto):
    texto = unicodedata.normalize('NFD', str(texto))
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto.lower()

def preparar_df(df_aba):
    """Padroniza colunas de cada aba"""
    df_aba = df_aba.fillna("")
    df_aba.columns = [col.strip() for col in df_aba.columns]
    
    # Mapeamento flexível de colunas (ignora se não existir)
    colunas_padrao = {
        "Nome Fantasia": "Nome Fantasia",
        "Nome Real / Razão Social": "Nome Real / Razão Social", 
        "Cidade": "Cidade",
        "Endereço": "Endereço",
        "Palestra Pública": "Palestra Pública",
        "Responsável": "Responsável",
        "Celular": "Celular"
    }
    
    # Aplica apenas colunas que existem
    renomeacoes = {old: new for old, new in colunas_padrao.items() 
                   if old in df_aba.columns}
    df_aba = df_aba.rename(columns=renomeacoes)
    
    # Garante que todas as colunas padrão existam (vazias se não houver)
    for col in colunas_padrao.values():
        if col not in df_aba.columns:
            df_aba[col] = ""
    
    return df_aba

# ==============================
# CONTROLE DE LOGIN
# ==============================
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

# ==============================
# ÁREA PRINCIPAL
# ==============================
else:
    st.title("🕊️ Guia Espírita 🕊️")
    busca = st.text_input("🔍 O que você procura?", placeholder="Digite aqui...")

    if busca:
        try:
            # ✅ LÊ TUDO ORDENADO ALFABETICAMENTE
            todas_abas = pd.read_excel("guia.xlsx", sheet_name=None)
            abas_ordenadas = sorted(todas_abas.keys())
            st.info(f"📊 Lidas {len(abas_ordenadas)} abas: {', '.join(abas_ordenadas)}")
            
            dfs_combinados = []
            for aba in abas_ordenadas:
                df_aba = preparar_df(todas_abas[aba])  # ✅ TRATA COLUNAS DIFERENTES
                dfs_combinados.append(df_aba)
                st.write(f"✅ Processada aba: **{aba}** ({len(df_aba)} linhas)")

            df = pd.concat(dfs_combinados, ignore_index=True)
            
            termo = limpar_busca(busca)
            mascara = df.apply(lambda linha: linha.apply(limpar_busca).str.contains(termo)).any(axis=1)
            resultados = df[mascara]

            if not resultados.empty:
                st.success(f"✅ {len(resultados)} resultado(s) encontrado(s)!")
                for _, row in resultados.iterrows():
                    v_fantasia = row["Nome Fantasia"]
                    v_nome_real = row["Nome Real / Razão Social"] + " 🕊️"
                    v_cidade = row["Cidade"]
                    v_endereco = row["Endereço"]
                    v_palestra = row["Palestra Pública"]
                    v_resp = row["Responsável"]
                    v_celular = row["Celular"]

                    # CARD
                    st.markdown(f"""
                    <div class="card-centro">
                        <div class="nome-grande">{v_nome_real}</div>
                        <div class="nome-fantasia">{v_fantasia}</div>
                        <div class="info-texto">👤 <b>Responsável:</b> {v_resp}</div>
                        <div class="info-texto">📍 <b>Endereço:</b> {v_endereco}</div>
                        <div class="info-texto">🏙️ <b>Cidade:</b> {v_cidade}</div>
                        {f'<div class="info-texto">🗓️ <b>Palestra Pública:</b> {v_palestra}</div>' if v_palestra.strip() else ''}
                    </div>
                    """, unsafe_allow_html=True)

                    # BOTÕES
                    col1, col2 = st.columns(2)
                    with col1:
                        if v_endereco.strip():
                            query = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                            st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}")
                    with col2:
                        if v_celular.strip() != "":
                            numero = ''.join(filter(str.isdigit, v_celular))
                            if len(numero) >= 10:
                                st.link_button("💬 WHATSAPP", f"https://wa.me/55{numero}")
                    st.write("")
            else:
                st.warning("Nenhum resultado encontrado.")
        except Exception as erro:
            st.error(f"Erro: {erro}")
            st.error("Verifique se 'guia.xlsx' está no diretório correto")
    else:
        st.info("👆 Digite algo para buscar nos centros espíritas!")
