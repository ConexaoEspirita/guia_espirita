import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

st.markdown("""
<style>
/* [MANTÉM TODO CSS PREMIUM do código anterior] */
.titulo-premium {
    background: linear-gradient(90deg, #0047AB, #1976D2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 4px 12px rgba(0,71,171,0.3);
    font-size: 2.5rem !important;
}
.card-centro {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 20px;
    border: 1px solid rgba(0,71,171,0.1);
    box-shadow: 0 8px 32px rgba(0,71,171,0.15);
    margin-bottom: 16px;
}
/* [resto do CSS igual] */
</style>
""", unsafe_allow_html=True)

def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = unicodedata.normalize('NFD', str(texto))
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\w\s]', ' ', texto.lower())
    return texto.strip()

st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)

# ✅ SEM LOGIN - DIRETO NA BUSCA
col_busca, col_botao = st.columns([4, 1])
with col_busca:
    busca_input = st.text_input("🔍 Procure centros espíritas", 
                              placeholder="Kardec, Icém, sexta-feira...", 
                              label_visibility="collapsed")
with col_botao:
    if st.button("🔎", use_container_width=True):
        if busca_input.strip():
            st.session_state.busca = busca_input.strip()
            st.rerun()

busca = st.session_state.get("busca", "").strip()

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

        resultados_df = pd.DataFrame(resultados)
        
        if not resultados_df.empty:
            st.markdown(f'<div class="conta-pequena">✨ achou {len(resultados_df)} resultado{"s" if len(resultados_df) != 1 else ""}</div>', unsafe_allow_html=True)

            for _, row in resultados_df.iterrows():
                # [TODO O CÓDIGO DOS CARDS PREMIUM igual anterior]
                v_nome_real = str(row.get('Nome Real / Razão Social', 'Centro Espírita')) + " 🕊️"
                # ... resto dos cards
                st.markdown(f'<div class="card-centro"><div class="nome-grande">{v_nome_real}</div></div>', unsafe_allow_html=True)
                
        else:
            st.warning("❌ Nenhum resultado encontrado.")
            
    except Exception as erro:
        st.error(f"❌ Erro: {str(erro)}")
else:
    st.info("✨ Digite nome do centro, cidade ou dia da semana!")

if st.button("🚪 Fechar app", key="fechar"):
    st.stop()
