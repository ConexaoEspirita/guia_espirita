import streamlit as st
from supabase import create_client
import pandas as pd
import random
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# --- 1. CONFIGURAÇÕES INICIAIS (Substitua pelos seus dados) ---
URL = "SUA_URL_SUPABASE"
KEY = "SUA_CHAVE_SUPABASE"
supabase = create_client(URL, KEY)

SENDGRID_API_KEY = "SUA_CHAVE_SENDGRID"

# --- 2. FUNÇÕES DE SUPORTE ---
def enviar_email(destinatario, codigo):
    mensagem = Mail(
        from_email='seu_email_verificado@exemplo.com', # Deve ser o e-email validado no SendGrid
        to_emails=destinatario,
        subject='Seu Código de Confirmação - Guia Espírita',
        html_content=f'<strong>Seu código de acesso é: {codigo}</strong>'
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(mensagem)
        return True
    except Exception as e:
        print(f"Erro SendGrid: {e}")
        return False

def carregar_dados():
    try:
        df = pd.read_excel("guia.xlsx")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar guia.xlsx: {e}")
        return pd.DataFrame()

# --- 3. INTERFACE E SESSÃO ---
st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario_email" not in st.session_state:
    st.session_state["usuario_email"] = None

# --- 4. FLUXO DE ACESSO (LOGIN / CADASTRO) ---
if not st.session_state["logado"]:
    st.markdown("<h1 style='text-align:center;'>🕊️ Guia Espírita</h1>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["🚪 Entrar", "✨ Cadastrar", "✉️ Confirmar"])

    with t1:
        with st.form("login"):
            e_l = st.text_input("E-mail")
            s_l = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                res = supabase.table("participantes").select("*").eq("email", e_l).execute()
                if res.data:
                    user = res.data[0]
                    if user["senha"] == s_l:
                        if user["confirmado"]:
                            st.session_state["logado"] = True
                            st.session_state["usuario_email"] = e_l
                            st.rerun()
                        else:
                            st.warning("⚠️ Valide sua conta na aba 'Confirmar'.")
                    else:
                        st.error("❌ Senha incorreta.")
                else:
                    st.error("❌ Usuário não encontrado.")

    with t2:
        with st.form("cadastro"):
            n_c = st.text_input("Nome Completo")
            e_c = st.text_input("E-mail")
            s_c = st.text_input("Senha", type="password")
            if st.form_submit_button("Criar Conta", use_container_width=True):
                cod = str(random.randint(100000, 999999))
                if enviar_email(e_c, cod):
                    try:
                        supabase.table("participantes").insert({
                            "nome": n_c, "email": e_c, "senha": s_c, 
                            "confirmado": False, "codigo_confirmacao": cod
                        }).execute()
                        st.success("📩 Código enviado! Verifique seu e-mail.")
                    except:
                        st.error("❌ Erro: Este e-mail já pode estar cadastrado.")
                else:
                    st.error("❌ Falha ao enviar e-mail. Tente novamente.")

    with t3:
        with st.form("confirmar"):
            e_conf = st.text_input("E-mail para confirmar")
            c_conf = st.text_input("Código de 6 dígitos")
            if st.form_submit_button("Ativar Minha Conta"):
                res = supabase.table("participantes").select("*").eq("email", e_conf).execute()
                if res.data and str(res.data[0]["codigo_confirmacao"]) == str(c_conf):
                    supabase.table("participantes").update({"confirmado": True}).eq("email", e_conf).execute()
                    st.success("✅ Conta ativada! Faça o login.")
                    st.balloons()
                else:
                    st.error("❌ Código inválido.")

# --- 5. ÁREA LOGADA (CARDS E ADMIN) ---
else:
    # Sidebar
    st.sidebar.title("🕊️ Navegação")
    menu = ["🔍 Buscar Centros", "📜 Frase do Dia"]
    if st.session_state["usuario_email"] == "bmefbovespa2017@gmail.com":
        menu.append("📊 Painel Admin")
    
    escolha = st.sidebar.selectbox("Ir para:", menu)
    if st.sidebar.button("Sair"):
        st.session_state["logado"] = False
        st.rerun()

    df_guia = carregar_dados()

    if escolha == "🔍 Buscar Centros":
        st.title("🔍 Localizar Centros Espíritas")
        
        if not df_guia.empty:
            cidades = sorted(df_guia['cidade'].unique())
            cidade_f = st.selectbox("Escolha sua cidade", cidades)
            
            # Filtrar dados
            resultados = df_guia[df_guia['cidade'] == cidade_f]
            
            # Exibição em Cards
            for _, row in resultados.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                        <h3>🏠 {row['nome_centro']}</h3>
                        <p>📍 <b>Endereço:</b> {row['endereco']}</p>
                        <p>📞 <b>Contato:</b> {row['contato']}</p>
                        <p>📅 <b>Horários:</b> {row['horarios']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("O arquivo guia.xlsx não foi encontrado ou está vazio.")

    elif escolha == "📊 Painel Admin":
        st.title("📊 Gestão de Usuários")
        res_users = supabase.table("participantes").select("nome, email, confirmado, created_at").execute()
        if res_users.data:
            df_users = pd.DataFrame(res_users.data)
            st.dataframe(df_users, use_container_width=True)
            
            if st.button("🗑️ Limpar Contas Não Confirmadas"):
                supabase.table("participantes").delete().eq("confirmado", False).execute()
                st.success("Limpeza realizada!")
                st.rerun()

    elif escolha == "📜 Frase do Dia":
        st.title("📜 Mensagem de Luz")
        frases = [
            "O Cristo não pediu muita coisa... pediu apenas que nos amássemos uns aos outros.",
            "A caridade é o roteiro da felicidade.",
            "Tudo passa, mas o bem que fazemos permanece para sempre."
        ]
        st.subheader(random.choice(frases))
