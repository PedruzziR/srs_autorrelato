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
    return client.open("srs_autorrelato").sheet1  # LEMBRE-SE DE CRIAR ESTA PLANILHA NO DRIVE!

try:
    planilha = conectar_planilha()
except Exception as e:
    st.error(f"Erro de conexão com a planilha: {e}")
    st.stop()
# =============================================================

def enviar_email_resultados(dados_avaliado, resultados_brutos):
    assunto = f"Resultados SRS-2 (Autorrelato) - Paciente: {dados_avaliado['nome']}"
    
    corpo = f"Avaliação SRS-2 (Adulto Autorrelato) concluída.\n\n"
    corpo += f"=== DADOS DO AVALIADO (RESPONDENTE) ===\n"
    corpo += f"Nome: {dados_avaliado['nome']}\n"
    corpo += f"CPF (Login): {dados_avaliado['cpf']}\n"
    corpo += f"Data de Nascimento: {dados_avaliado['data_nasc']}\n"
    corpo += f"Sexo: {dados_avaliado['sexo']}\n\n"
    
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
    except Exception as e:
        return False

# =============================================================
# 1. PERGUNTAS DO TESTE
# =============================================================
perguntas = [
    "Eu fico muito mais desconfortável em situações sociais do que quando estou sozinho.",
    "Minhas expressões faciais passam uma mensagem errada aos outros sobre como eu realmente me sinto.",
    "Eu me sinto confiante (ou seguro) quando estou interagindo com os outros.",
    "Quando estou sob estresse, tenho um comportamento rígido e inflexível que parece estranho para os outros.",
    "Eu não reconheço quando os outros estão tentando tirar vantagem sobre mim.",
    "Eu preferia estar sozinho do que com os outros.",
    "Normalmente eu consigo perceber como os outros estão se sentindo.",
    "Eu me comporto de maneiras que parecem estranhas ou esquisitas aos outros.",
    "Eu sou excessivamente dependente dos outros para me ajudar entender às minhas necessidades diárias.",
    "Eu levo as coisas muito \"ao pé da letra\", e por causa disso, eu interpreto mal o significado pretendido de partes de uma conversa.",
    "Eu sou autoconfiante.",
    "Eu sou capaz de comunicar meus sentimentos aos outros.",
    "Eu fico estranho nas interações com os colegas (por exemplo, eu levo um tempo acompanhando o vai e vem da conversa).",
    "Eu não sou bem coordenado.",
    "Quando as pessoas mudam seu tom ou expressão facial, eu normalmente entendo o que isso significa.",
    "Eu evito contato visual ou me dizem que eu tenho contato visual diferente.",
    "Eu reconheço quando algo é injusto.",
    "Eu tenho dificuldade em fazer amigos, mesmo quando eu tento dar o melhor de mim.",
    "Eu fico frustrado tentando expressar minhas ideias em uma conversa.",
    "Eu tenho interesses sensoriais que os outros acham diferentes (por exemplo, cheirar ou olhar para as coisas de um jeito especial).",
    "Eu sou capaz de imitar a ação e expressão dos outros quando é socialmente apropriado.",
    "Eu interajo apropriadamente com os outros adultos.",
    "Eu não participo de atividades em grupo ou eventos sociais a menos que seja obrigado fazê-lo.",
    "Eu tenho mais dificuldade que os outros com mudanças na minha rotina.",
    "Eu não me importo de não estar \"na mesma onda\" ou fora de sintonia com os outros.",
    "Eu ofereço conforto aos outros quando eles estão tristes.",
    "Eu evito iniciar interações sociais com outros adultos.",
    "Eu penso ou falo sobre a mesma coisa repetidamente.",
    "Eu sou considerado pelos outros como estranho ou esquisito.",
    "Eu fico perturbado em situações com muitas coisas acontecendo.",
    "Eu não consigo tirar algo da minha mente uma vez que começo pensar sobre aquilo.",
    "Eu tenho boa higiene pessoal.",
    "Meu comportamento é socialmente desajeitado, mesmo quando eu estou tentando ser educado.",
    "Eu evito pessoas que querem ser emocionalmente próximas a mim.",
    "Eu tenho dificuldade em acompanhar o fluxo de uma conversa normal.",
    "Eu tenho dificuldade em me relacionar com os membros da minha família.",
    "Eu tenho dificuldade em me relacionar com pessoas que não são da minha família.",
    "Eu respondo adequadamente às mudanças de humor das outras pessoas (por exemplo, quando o humor de um amigo muda de feliz para triste).",
    "As pessoas me acham muito interessado em poucos assuntos, ou que eu me \"deixo levar\" por esses assuntos.",
    "Eu sou imaginativo.",
    "Eu às vezes mudo de uma atividade para outra sem nenhuma razão.",
    "Eu sou excessivamente sensível a certos sons, texturas ou cheiros.",
    "Eu gosto de conversas (conversas casuais com os outros).",
    "Eu tenho mais problema do que a maioria das pessoas com o entendimento da causalidade (em outras palavras, como os eventos estão relacionados uns com os outros).",
    "Quando os outros ao redor de mim estão prestando atenção em algo, eu fico interessado no que eles estão atentos.",
    "Os outros sentem que eu tenho expressões faciais excessivamente sérias.",
    "Eu dou risadas em momentos inapropriados.",
    "Eu tenho um bom senso de humor e consigo entender piadas.",
    "Eu sou extremamente bom em certos tipos de tarefas intelectuais, mas não sou tão bom na maioria das outras tarefas.",
    "Eu tenho comportamentos repetitivos que as outras pessoas consideram estranhos.",
    "Eu tenho dificuldade de responder perguntas diretamente e acabo discursando sobre o assunto.",
    "Eu falo muito alto sem perceber.",
    "Eu tenho tendência a falar com uma voz monótona (em outras palavras, menor inflexão da voz que a maioria das pessoas demonstra).",
    "Eu tenho uma tendência a pensar sobre as pessoas do mesmo jeito que eu faço com os objetos.",
    "Eu fico muito perto dos outros ou invado o espaço pessoal deles sem perceber.",
    "Às vezes eu cometo o erro de andar entre duas pessoas que estão tentando conversar uma com a outra.",
    "Eu tenho uma tendência a me isolar.",
    "Eu me concentro demais nas partes das coisas ao invés de ver a figura como um todo.",
    "Eu sou mais desconfiado que a maioria das pessoas.",
    "As outras pessoas me acham emocionalmente distante e que não demonstro meus sentimentos.",
    "Eu tenho uma tendência a ser inflexível.",
    "Quando eu conto a alguém a minha razão para fazer alguma coisa, a pessoa acha que é incomum, sem lógica.",
    "Meu jeito de cumprimentar uma outra pessoa é incomum.",
    "Eu sou muito mais tenso em situações sociais do que quando estou sozinho.",
    "Eu me pego olhando fixo para o espaço."
]

opcoes_respostas = {
    "1 = Não é verdade": 1,
    "2 = Algumas vezes é verdade": 2,
    "3 = Muitas vezes é verdade": 3,
    "4 = Quase sempre é verdade": 4
}

# 2. Interface Visual
st.set_page_config(page_title="SRS-2 Autorrelato", layout="centered")

if "logado" not in st.session_state:
    st.session_state.logado = False
if "cpf_avaliado" not in st.session_state:
    st.session_state.cpf_avaliado = ""
if "avaliacao_concluida" not in st.session_state:
    st.session_state.avaliacao_concluida = False

st.title("Clínica de Psicologia e Psicanálise Bruna Ligoski")

# ================= TELA DE LOGIN =================
if not st.session_state.logado:
    st.write("Bem-vindo(a) à Avaliação SRS-2 (Autorrelato).")
    
    with st.form("form_login"):
        cpf_input = st.text_input("Seu CPF (Login de Acesso - Apenas números)")
        senha_input = st.text_input("Senha de Acesso", type="password")
        botao_entrar = st.form_submit_button("Acessar Avaliação")
        
        if botao_entrar:
            if not cpf_input:
                st.error("Por favor, preencha o seu CPF.")
            elif senha_input != st.secrets["SENHA_MESTRA"]:
                st.error("Senha incorreta.")
            else:
                try:
                    cpfs_registrados = planilha.col_values(1)
                except:
                    cpfs_registrados = []
                    
                if cpfs_registrados.count(cpf_input) >= 4:
                    st.error("Acesso bloqueado. Este CPF já atingiu o limite máximo de 4 avaliações cadastradas.")
                else:
                    st.session_state.logado = True
                    st.session_state.cpf_avaliado = cpf_input
                    st.session_state.avaliacao_concluida = False
                    st.rerun()

# ================= TELA FINAL =================
elif st.session_state.avaliacao_concluida:
    st.success("Avaliação concluída e enviada com sucesso! Muito obrigado pela sua colaboração.")

# ================= QUESTIONÁRIO =================
else:
    st.write("### Escala de Responsividade Social (SRS-2) - Autorrelato")
    st.info("**Instrução:** Em cada questão, por favor escolha a alternativa que melhor descreva o seu comportamento nos últimos 6 meses.")
    st.divider()

    with st.form("formulario_avaliacao"):
        st.subheader("Seus Dados (Avaliado)")
        nome_avaliado = st.text_input("Nome completo *")
        cpf_form = st.text_input("CPF *", value=st.session_state.cpf_avaliado, disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            data_nasc_avaliado = st.date_input("Data de nascimento *", format="DD/MM/YYYY", min_value=datetime.date(1930, 1, 1), max_value=datetime.date.today())
        with col2:
            sexo_avaliado = st.selectbox("Sexo *", ["Selecione", "Masculino", "Feminino"])
        
        st.divider()

        respostas_coletadas = {}

        for index, texto_pergunta in enumerate(perguntas):
            num_q = index + 1
            st.write(f"**{num_q}. {texto_pergunta}**")
            resposta = st.radio(f"Oculto {num_q}", list(opcoes_respostas.keys()), index=None, label_visibility="collapsed", key=f"q_{num_q}")

            if resposta is not None:
                respostas_coletadas[num_q] = opcoes_respostas[resposta]
            else:
                respostas_coletadas[num_q] = None
            st.write("---")

        botao_enviar = st.form_submit_button("Finalizar Avaliação")

    # 3. Processamento e Envio
    if botao_enviar:
        questoes_em_branco = [q for q, r in respostas_coletadas.items() if r is None]

        if not nome_avaliado or sexo_avaliado == "Selecione":
            st.error("Por favor, preencha todos os seus dados de identificação obrigatórios.")
        elif questoes_em_branco:
            st.error(f"Por favor, responda todas as perguntas. Falta responder {len(questoes_em_branco)} questão(ões).")
        else:
            dados_avaliado = {
                "nome": nome_avaliado,
                "cpf": st.session_state.cpf_avaliado,
                "data_nasc": data_nasc_avaliado.strftime("%d/%m/%Y"),
                "sexo": sexo_avaliado
            }

            with st.spinner('Processando os resultados e enviando e-mail...'):
                sucesso = enviar_email_resultados(dados_avaliado, respostas_coletadas)
                
                if sucesso:
                    try:
                        planilha.append_row([st.session_state.cpf_avaliado])
                    except:
                        pass
                    st.session_state.avaliacao_concluida = True
                    st.rerun()
                else:
                    st.error("Houve um erro no envio. Avise a profissional responsável.")
