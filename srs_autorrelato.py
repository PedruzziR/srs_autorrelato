import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import gspread
from google.oauth2.service_account import Credentials
import datetime

# ================= CONFIGURAÇÕES DE E-MAIL =================
SEU_EMAIL = st.secrets["EMAIL_USUARIO"]
SENHA_DO_EMAIL = st.secrets["SENHA_USUARIO"]
EMAIL_DESTINO = "psicologabrunaligoski@gmail.com"
# ===========================================================

# ================= CONEXÃO COM GOOGLE SHEETS =================
@st.cache_resource
def conectar_planilha():
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS_JSON"])
    escopos = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=escopos)
    client = gspread.authorize(creds)
    # CONECTA DIRETAMENTE À PLANILHA CENTRAL DE TOKENS
    return client.open("Controle_Tokens").sheet1 

try:
    planilha = conectar_planilha()
except Exception as e:
    st.error(f"Erro de conexão com a planilha de controle: {e}")
    st.stop()
# =============================================================

def enviar_email_resultados(dados_avaliado, resultados_brutos, token):
    assunto = f"Resultados SRS-2 (Autorrelato) - Paciente: {dados_avaliado['nome']}"
    
    corpo = f"Avaliação SRS-2 (Adulto Autorrelato) concluída.\n\n"
    corpo += f"=== DADOS DO(A) AVALIADO(A) ===\n"
    corpo += f"Nome: {dados_avaliado['nome']}\n"
    corpo += f"Data de Nascimento: {dados_avaliado['data_nasc']}\n"
    corpo += f"Sexo: {dados_avaliado['sexo']}\n"
    corpo += f"Token de Validação: {token}\n\n"
    
    corpo += "================ GABARITO DE RESPOSTAS ================\n"
    corpo += "Formato: [Número da Questão] - [Valor da Resposta]\n\n"
    
    for num_q, valor in resultados_brutos.items():
        corpo += f"{num_q} - {valor}\n"

    msg = MIMEMultipart()
    msg['From'] = SEU_EMAIL
    msg['To'] = EMAIL_DESTINO
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SEU_EMAIL, SENHA_DO_EMAIL)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# ================= PERGUNTAS DO TESTE =================
perguntas = [
    "Eu fico muito mais desconfortável em situações sociais do que quando estou sozinho(a).",
    "Minhas expressões faciais passam uma mensagem errada aos outros sobre como eu realmente me sinto.",
    "Eu me sinto confiante (ou seguro/a) quando estou interagindo com os outros.",
    "Quando estou sob estresse, tenho um comportamento rígido e inflexível que parece estranho para os outros.",
    "Eu não reconheço quando os outros estão tentando tirar vantagem sobre mim.",
    "Eu preferia estar sozinho(a) do que com os outros.",
    "Normalmente eu consigo perceber como os outros estão se sentindo.",
    "Eu me comporto de maneiras que parecem estranhas ou esquisitas aos outros.",
    "Eu sou excessivamente dependente dos outros para me ajudar entender às minhas necessidades diárias.",
    "Eu levo as coisas muito \"ao pé da letra\", e por causa disso, eu interpreto mal o significado pretendido de partes de uma conversa.",
    "Eu sou autoconfiante.",
    "Eu sou capaz de comunicar meus sentimentos aos outros.",
    "Eu fico estranho(a) nas interações com os colegas (por exemplo, eu levo um tempo acompanhando o vai e vem da conversa).",
    "Eu não sou bem coordenado(a).",
    "Quando as pessoas mudam seu tom ou expressão facial, eu normalmente entendo o que isso significa.",
    "Eu evito contato visual ou me dizem que eu tenho contato visual diferente.",
    "Eu reconheço quando algo é injusto.",
    "Eu tenho dificuldade em fazer amigos, mesmo quando eu tento dar o melhor de mim.",
    "Eu fico frustrado(a) tentando expressar minhas ideias em uma conversa.",
    "Eu tenho interesses sensoriais que os outros acham diferentes (por exemplo, cheirar ou olhar para as coisas de um jeito especial).",
    "Eu sou capaz de imitar a ação e expressão dos outros quando é socialmente apropriado.",
    "Eu interajo apropriadamente com os outros adultos.",
    "Eu não participo de atividades em grupo ou eventos sociais a menos que seja obrigado(a) fazê-lo.",
    "Eu tenho mais dificuldade que os outros com mudanças na minha rotina.",
    "Eu não me importo de não estar \"na mesma onda\" ou fora de sintonia com os outros.",
    "Eu ofereço conforto aos outros quando eles estão tristes.",
    "Eu evito iniciar interações sociais com outros adultos.",
    "Eu penso ou falo sobre a mesma coisa repetidamente.",
    "Eu sou considerado(a) pelos outros como estranho(a) ou esquisito(a).",
    "Eu fico perturbado(a) em situações com muitas coisas acontecendo.",
    "Eu não consigo tirar algo da minha mente uma vez que começo pensar sobre aquilo.",
    "Eu tenho boa higiene pessoal.",
    "Meu comportamento é socialmente desajeitado, mesmo quando eu estou tentando ser educado(a).",
    "Eu evito pessoas que querem ser emocionalmente próximas a mim.",
    "Eu tenho dificuldade em acompanhar o fluxo de uma conversa normal.",
    "Eu tenho dificuldade em se relacionar com os membros da minha família.",
    "Eu tenho dificuldade em se relacionar com pessoas que não são da minha família.",
    "Eu respondo adequadamente às mudanças de humor das outras pessoas (por exemplo, quando o humor de um amigo muda de feliz para triste).",
    "As pessoas me acham muito interessado(a) em poucos assuntos, ou que eu me \"deixo levar\" por esses assuntos.",
    "Eu sou imaginativo(a).",
    "Eu às vezes mudo de uma atividade para outra sem nenhuma razão.",
    "Eu sou excessivamente sensível a certos sons, texturas ou cheiros.",
    "Eu gosto de conversas (conversas casuais com os outros).",
    "Eu tenho mais problema do que a maioria das pessoas com o entendimento da causalidade (em outras palavras, como os eventos estão relacionados uns com os outros).",
    "Quando os outros ao redor de mim estão prestando atenção em algo, eu fico interessado(a) no que eles estão atentos.",
    "Os outros sentem que eu tenho expressões faciais excessivamente sérias.",
    "Eu dou risadas em momentos inapropriados.",
    "Eu tenho um bom senso de humor e consigo entender piadas.",
    "Eu sou extremamente bom(boa) em certos tipos de tarefas intelectuais, mas não sou tão bom(boa) na maioria das outras tarefas.",
    "Eu tenho comportamentos repetitivos que as outras pessoas consideram estranhos.",
    "Eu tenho dificuldade de responder perguntas diretamente e acabo discursando sobre o assunto.",
    "Eu falo muito alto sem perceber.",
    "Eu tenho tendência a falar com uma voz monótona (em outras palavras, menor inflexão da voz que a maioria das pessoas demonstra).",
    "Eu tenho uma tendência a pensar sobre as pessoas do mesmo jeito que eu faço com os objetos.",
    "Eu fico muito perto dos outros ou invado o espaço pessoal deles sem perceber.",
    "Às vezes eu cometo o erro de andar entre duas pessoas que estão tentando conversar uma com a outra.",
    "Eu tenho uma tendência a me isolar.",
    "Eu me concentro demais nas partes das coisas ao invés de ver a figura como um todo.",
    "Eu sou mais desconfiado(a) que a maioria das pessoas.",
    "As outras pessoas me acham emocionalmente distante e que não demonstro meus sentimentos.",
    "Eu tenho uma tendência a ser inflexível.",
    "Quando eu conto a alguém a minha razão para fazer alguma coisa, a pessoa acha que é incomum, sem lógica.",
    "Meu jeito de cumprimentar uma outra pessoa é incomum.",
    "Eu sou muito mais tenso(a) em situações sociais do que quando estou sozinho(a).",
    "Eu me pego olhando fixo para o espaço."
]

opcoes_respostas = {
    "1 = Não é verdade": 1,
    "2 = Algumas vezes é verdade": 2,
    "3 = Muitas vezes é verdade": 3,
    "4 = Quase sempre é verdade": 4
}

st.set_page_config(page_title="SRS-2 Autorrelato", layout="centered")

# CSS para Botão Azul Forçado
st.markdown("""
    <style>
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #0047AB !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 2.5rem !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #003380 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

if "avaliacao_concluida" not in st.session_state:
    st.session_state.avaliacao_concluida = False

# Título Centralizado
st.markdown("<h1 style='text-align: center;'>Clínica de Psicologia e Psicanálise Bruna Ligoski</h1>", unsafe_allow_html=True)

if st.session_state.avaliacao_concluida:
    st.success("Avaliação concluída e enviada com sucesso! Muito obrigado(a) pela sua colaboração.")
    st.stop()

# ================= VALIDAÇÃO SILENCIOSA DO TOKEN =================
parametros = st.query_params
token_url = parametros.get("token", None)

if not token_url:
    st.warning("⚠️ Link de acesso inválido. Solicite um novo link à profissional.")
    st.stop()

try:
    registros = planilha.get_all_records()
    dados_token = None
    linha_alvo = 2 
    for i, reg in enumerate(registros):
        if str(reg.get("Token")) == token_url:
            dados_token = reg
            linha_alvo += i
            break
            
    if not dados_token or dados_token.get("Status") != "Aberto":
        st.error("⚠️ Este link é inválido ou já foi utilizado.")
        st.stop()
except Exception:
    st.error("Erro técnico na validação do link.")
    st.stop()

# ================= INTERFACE DO TESTE =================
linha_fina = "<hr style='margin-top: 8px; margin-bottom: 8px;'/>"
st.markdown(linha_fina, unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Escala de Responsividade Social (SRS-2) - Autorrelato</h3>", unsafe_allow_html=True)
st.markdown(linha_fina, unsafe_allow_html=True)

st.info("**Instrução:** Em cada questão, por favor escolha a alternativa que melhor descreva o seu comportamento nos últimos 6 meses.")

with st.form("form_srs2_autorrelato"):
    st.subheader("Seus Dados (Avaliado/a)")
    nome_avaliado = st.text_input("Nome completo do(a) paciente *")
    
    col1, col2 = st.columns(2)
    with col1:
        data_nasc_avaliado = st.date_input("Data de nascimento *", format="DD/MM/YYYY", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today(), value=None)
    with col2:
        sexo_avaliado = st.selectbox("Sexo *", ["Selecione", "Masculino", "Feminino"])
    
    st.divider()

    respostas_coletadas = {}
    for index, texto_pergunta in enumerate(perguntas):
        num_q = index + 1
        st.write(f"**{num_q}. {texto_pergunta}**")
        resposta = st.radio(f"Oculto {num_q}", list(opcoes_respostas.keys()), index=None, label_visibility="collapsed")
        respostas_coletadas[num_q] = opcoes_respostas[resposta] if resposta else None
        st.divider()

    if st.form_submit_button("Enviar Avaliação"):
        questoes_em_branco = [q for q, r in respostas_coletadas.items() if r is None]

        if not nome_avaliado or sexo_avaliado == "Selecione" or data_nasc_avaliado is None:
            st.error("Por favor, preencha todos os seus dados de identificação obrigatórios.")
        elif questoes_em_branco:
            st.error(f"Por favor, responda todas as perguntas. Faltam {len(questoes_em_branco)} questão(ões).")
        else:
            dados_final = {
                "nome": nome_avaliado,
                "data_nasc": data_nasc_avaliado.strftime("%d/%m/%Y"),
                "sexo": sexo_avaliado
            }

            with st.spinner('Enviando avaliação...'):
                if enviar_email_resultados(dados_final, respostas_coletadas, token_url):
                    try:
                        planilha.update_cell(linha_alvo, 5, "Respondido")
                        st.session_state.avaliacao_concluida = True
                        st.rerun()
                    except:
                        st.session_state.avaliacao_concluida = True
                        st.rerun()
                else:
                    st.error("Houve um erro no envio. Tente novamente.")
