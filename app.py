import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

# 1. Configuração da Página
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

# 2. Estilização CSS
st.markdown("""
<style>
.stApp { background: #EBF4FA; }
.titulo-premium { color: #0047AB; font-size: 2.2rem; font-weight: 800; text-align: center; margin-bottom: 15px; }
.card-centro { background: white; padding: 18px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 12px; border-left: 5px solid #0047AB; }
.nome-grande { color: #1E3A8A; font-size: 19px; font-weight: 800; line-height: 1.2; }
.conta-pequena { color: #4B5563; font-size: 13px; margin-bottom: 10px; font-weight: 700; background: #FFF; padding: 5px 12px; border-radius: 50px; display: inline-block; border: 1px solid #D1D5DB; }
</style>
""", unsafe_allow_html=True)

# 3. Conexão Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def limpar_texto(t):
    if pd.isna(t): return ""
    t = unicodedata.normalize('NFD', str(t))
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^\w\s]', ' ', t.lower()).strip()

# Inicialização de Estados (Evita o erro vermelho)
if "logado" not in st.session_state: st.session_state.logado = False
if "form_key" not in st.session_state: st.session_state.form_key = 0

# 4. Tela de Login
if not st.session_state.logado:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    with st.container():
        e = st.text_input("📧 E-mail").strip().lower()
        s = st.text_input("🔒 Senha", type="password").strip()
        if st.button("🚀 ACESSAR GUIA", use_container_width=True):
            res = supabase.table("acessos").select("*").eq("email", e).eq("senha", s).execute()
            if res.data:
                st.session_state.logado = True
                st.rerun()
            else: st.error("❌ E-mail ou senha incorretos.")

# 5. Tela Principal
else:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)

    # BARRA DE PESQUISA COM KEY DINÂMICA (Para limpar no Voltar)
    busca = st.text_input("🔍 Pesquisar por Nome, Rua ou Bairro", 
                         key=f"input_{st.session_state.form_key}", 
                         placeholder="Digite aqui...")
    
    if busca:
        try:
            # Carregar Planilha
            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            df.columns = [c.strip() for c in df.columns]
            
            # Mapeamento Seguro
            df = df.rename(columns={
                'NOME FANTASIA': 'Fantasia', 'NOME': 'Nome',
                'CIDADE DO CENTRO ESPIRITA': 'Cidade', 'ENDERECO': 'Endereco',
                'RESPONSAVEL': 'Responsavel', 'CELULAR': 'Celular'
            })

            termo = limpar_texto(busca)
            # Lógica de Filtro
            res = []
            for _, row in df.iterrows():
                alvo = " ".join([limpar_texto(row.get('Nome','')), limpar_texto(row.get('Fantasia','')), 
                                 limpar_texto(row.get('Endereco','')), limpar_texto(row.get('Cidade',''))])
                if termo in alvo: res.append(row)

            if res:
                # CONTADOR DE RESULTADOS
                st.markdown(f'<div class="conta-pequena">✨ Encontrados {len(res)} resultados</div>', unsafe_allow_html=True)
                
                if st.button("⬅️ VOLTAR / LIMPAR"):
                    st.session_state.form_key += 1 # ISSO LIMPA A BARRA E SOBE O TECLADO
                    st.rerun()

                for r in res:
                    st.markdown(f"""
                    <div class="card-centro">
                        <div class="nome-grande">{r['Nome']}</div>
                        <div style="color:#2563EB; font-size:14px; font-style:italic;">{r['Fantasia']}</div>
                        <div style="margin-top:8px; font-size:14px;">📍 <b>Endereço:</b> {r['Endereco']} - {r['Cidade']}</div>
                        <div style="font-size:14px;">👤 <b>Responsável:</b> {r['Responsavel']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        # GOOGLE MAPS
                        end = urllib.parse.quote(f"{r['Endereco']}, {r['Cidade']}")
                        st.link_button("🗺️ MAPS", f"https://www.google.com{end}", use_container_width=True)
                    with c2:
                        # WHATSAPP
                        tel = ''.join(filter(str.isdigit, str(r['Celular'])))
                        if len(tel) >= 10:
                            st.link_button("💬 WHATSAPP", f"https://wa.me{tel}", use_container_width=True)
                    st.divider()
            else:
                st.warning("❌ Nenhum resultado para esta pesquisa.")
                if st.button("⬅️ Tentar Outra"):
                    st.session_state.form_key += 1
                    st.rerun()

        except Exception as e:
            st.error(f"Erro ao ler guia.xlsx: {e}")
    else:
        st.info("💡 Digite o nome do centro ou a rua para pesquisar.")

    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()
