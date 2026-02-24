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
.titulo-premium { color: #0047AB; font-size: 2.5rem; font-weight: 800; text-align: center; }
.card-centro { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 15px; border-left: 5px solid #0047AB; }
.nome-grande { color: #1E3A8A; font-size: 20px; font-weight: 800; }
.conta-pequena { color: #6B7280; font-size: 14px; margin-bottom: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. Conexão Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def limpar_busca(texto):
    if pd.isna(texto): return ""
    texto = unicodedata.normalize('NFD', str(texto))
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\w\s]', ' ', texto.lower())
    return texto.strip()

# Inicialização de estados para evitar erros vermelhos
if "logado" not in st.session_state: st.session_state.logado = False
if "reset_key" not in st.session_state: st.session_state.reset_key = 0

# 4. Tela de Login
if not st.session_state.logado:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)
    e = st.text_input("📧 E-mail").strip().lower()
    s = st.text_input("🔒 Senha", type="password").strip()
    if st.button("🚀 ACESSAR GUIA", use_container_width=True):
        res = supabase.table("acessos").select("*").eq("email", e).eq("senha", s).execute()
        if res.data:
            st.session_state.logado = True
            st.rerun()
        else: st.error("❌ Dados incorretos")

# 5. Tela Principal
else:
    st.markdown('<h1 class="titulo-premium">🕊️ Guia Espírita</h1>', unsafe_allow_html=True)

    # A "key" muda quando clicamos em voltar, forçando a barra a limpar e focar
    busca = st.text_input("🔍 Buscar por nome, rua ou bairro", 
                         key=f"busca_{st.session_state.reset_key}", 
                         placeholder="Clique aqui para digitar...")
    
    if busca:
        try:
            df = pd.read_excel("guia.xlsx", sheet_name="casas espiritas python")
            df.columns = [col.strip() for col in df.columns]
            df = df.rename(columns={'NOME FANTASIA':'F','NOME':'N','CIDADE DO CENTRO ESPIRITA':'C','ENDERECO':'E','CELULAR':'Cel','RESPONSAVEL':'R'})

            t = limpar_busca(busca)
            res = [r for _, r in df.iterrows() if t in " ".join([limpar_busca(r.get('N','')), limpar_busca(r.get('F','')), limpar_busca(r.get('E','')), limpar_busca(r.get('C',''))])]

            if res:
                st.markdown(f'<div class="conta-pequena">✨ achou {len(res)} resultado(s)</div>', unsafe_allow_html=True)
                
                # BOTÃO VOLTAR QUE LIMPA A BARRA SEM ERRO
                if st.button("⬅️ VOLTAR / LIMPAR BUSCA"):
                    st.session_state.reset_key += 1 # Isso limpa a barra e foca o cursor nela
                    st.rerun()

                for r in res:
                    st.markdown(f"""
                    <div class="card-centro">
                        <div class="nome-grande">{r['N']}</div>
                        <div style="color:#3B82F6;">{r['F']}</div>
                        <div style="margin-top:8px;">📍 <b>Endereço:</b> {r['E']} - {r['C']}</div>
                        <div>👤 <b>Responsável:</b> {r['R']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        q = urllib.parse.quote(f"{r['E']}, {r['C']}")
                        st.link_button("🗺️ MAPS", f"https://www.google.com{q}", use_container_width=True)
                    with c2:
                        n = ''.join(filter(str.isdigit, str(r['Cel'])))
                        if len(n) >= 10:
                            st.link_button("💬 WHATSAPP", f"https://wa.me{n}", use_container_width=True)
                    st.divider()
            else:
                st.warning("❌ Nada encontrado.")
                if st.button("⬅️ Tentar novamente"):
                    st.session_state.reset_key += 1
                    st.rerun()
        except Exception as err:
            st.error(f"Erro no arquivo: {err}")
    else:
        st.info("💡 Digite o nome, rua ou bairro acima.")

    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()
