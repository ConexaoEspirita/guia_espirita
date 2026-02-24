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
.nome-grande { color: #0047AB; font-size: 26px; font-weight: bold; line-height: 1.1; }
.nome-fantasia { color: #5CACE2 !important; font-size: 17px !important; font-weight: 500; font-style: italic; margin-bottom: 12px; display: block; }
.info-texto { color: #444; font-size: 14px; margin-bottom: 4px; }
div.stLinkButton > a { width: 100% !important; font-weight: bold !important; height: 45px !important; display: flex !important; align-items: center !important; justify-content: center !important; }
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

def debug_df(df, nome="DataFrame"):
    """Debug: mostra colunas e primeiras linhas"""
    st.write(f"🔍 Colunas em {nome}: {list(df.columns)}")
    st.write(f"📏 Tamanho: {len(df)} linhas")
    if len(df) > 0:
        st.write("Primeiras 3 linhas:")
        st.dataframe(df.head(3))

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
# ÁREA PRINCIPAL - VERSÃO ULTRA SIMPLES
# ==============================
else:
    st.title("🕊️ Guia Espírita 🕊️")
    busca = st.text_input("🔍 O que você procura?", placeholder="Digite aqui...")

    if busca:
        try:
            # ✅ LÊ APENAS A ABA COM DADOS (casas espiritas python)
            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            st.success("✅ Carregou aba 'casas espiritas python' com {len(df)} linhas")
            
            # Debug das colunas originais
            st.write("**COLUNAS ENCONTRADAS:**", list(df.columns))
            debug_df(df, "ORIGINAL")
            
            # Limpa nomes das colunas
            df.columns = [col.strip() for col in df.columns]
            st.write("**COLUNAS LIMPA:**", list(df.columns))
            
            # Padroniza nomes das colunas (usa os nomes reais que você tem)
            colunas_originais = list(df.columns)
            mapeamento = {}
            for col in colunas_originais:
                col_limpo = col.lower().strip()
                if any(x in col_limpo for x in ['nome fantasia', 'fantasia']):
                    mapeamento[col] = "Nome Fantasia"
                elif any(x in col_limpo for x in ['nome real', 'razao', 'social']):
                    mapeamento[col] = "Nome Real / Razão Social"
                elif any(x in col_limpo for x in ['cidade']):
                    mapeamento[col] = "Cidade"
                elif any(x in col_limpo for x in ['endereco', 'rua', 'av']):
                    mapeamento[col] = "Endereço"
                elif any(x in col_limpo for x in ['palestra', 'evento']):
                    mapeamento[col] = "Palestra Pública"
                elif any(x in col_limpo for x in ['responsavel', 'contato']):
                    mapeamento[col] = "Responsável"
                elif any(x in col_limpo for x in ['celular', 'telefone', 'whatsapp']):
                    mapeamento[col] = "Celular"
            
            st.write("**MAPEAMENTO AUTOMÁTICO:**", mapeamento)
            df = df.rename(columns=mapeamento)
            
            # Garante colunas mínimas
            colunas_necessarias = ["Nome Fantasia", "Nome Real / Razão Social", "Cidade", "Endereço", "Responsável", "Celular"]
            for col in colunas_necessarias:
                if col not in df.columns:
                    df[col] = ""
            
            debug_df(df, "FINAL")
            
            termo = limpar_busca(busca)
            mascara = df.apply(lambda linha: linha.astype(str).apply(limpar_busca).str.contains(termo, na=False)).any(axis=1)
            resultados = df[mascara]

            if not resultados.empty:
                st.success(f"✅ {len(resultados)} resultado(s) encontrado(s)!")
                for _, row in resultados.iterrows():
                    # Usa .get() para evitar erros
                    v_fantasia = row.get("Nome Fantasia", "") or "Não informado"
                    v_nome_real = row.get("Nome Real / Razão Social", "") or "Centro Espírita"
                    v_nome_real = v_nome_real + " 🕊️" if v_nome_real != "Centro Espírita" else "Centro Espírita 🕊️"
                    v_cidade = row.get("Cidade", "") or "Não informada"
                    v_endereco = row.get("Endereço", "") or "Não informado"
                    v_palestra = row.get("Palestra Pública", "") or ""
                    v_resp = row.get("Responsável", "") or "Não informado"
                    v_celular = row.get("Celular", "") or ""

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
                        if v_endereco != "Não informado":
                            query = urllib.parse.quote(f"{v_endereco}, {v_cidade}")
                            st.link_button("🗺️ MAPS", f"https://www.google.com/maps/search/?api=1&query={query}")
                    with col2:
                        if v_celular and len(''.join(filter(str.isdigit, v_celular))) >= 10:
                            numero = ''.join(filter(str.isdigit, v_celular))
                            st.link_button("💬 WHATSAPP", f"https://wa.me/55{numero}")
                    st.write("")
            else:
                st.warning("Nenhum resultado encontrado.")
                
        except Exception as erro:
            st.error(f"❌ ERRO: {erro}")
            st.error("Verifique se 'guia.xlsx' existe e tem a aba 'casas espiritas python'")
    else:
        st.info("👆 Digite algo para buscar nos centros espíritas!")
