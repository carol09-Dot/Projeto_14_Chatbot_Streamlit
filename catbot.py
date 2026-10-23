import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

from banco import (
    criar_tabelas,
    criar_conversa,
    salvar_mensagem,
    listar_conversas,
    buscar_mensagens,
    atualizar_titulo
)


# Configuração inicial
st.set_page_config(page_title="Catbot", page_icon="🐈‍⬛")

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("Chave da API não encontrada. Confira seu arquivo .env.")
    st.stop()

client = Groq(api_key=api_key)

criar_tabelas()


# Personalidade do Catbot
def responder(historico):
    resposta = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é o Catbot, um gato vampiro "
                    "simpático e inteligente."
                )
            },
            *historico
        ]
    )

    return resposta.choices[0].message.content


def gerar_titulo(primeira_mensagem):
    resposta = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Crie um título curto para uma conversa. "
                    "Use de 2 a 6 palavras, no idioma da mensagem. "
                    "Retorne somente o título, sem aspas."
                )
            },
            {
                "role": "user",
                "content": primeira_mensagem
            }
        ]
    )

    return resposta.choices[0].message.content.strip()


# Inicializar a conversa selecionada
if "conversa_id" not in st.session_state:
    st.session_state.conversa_id = None
    st.session_state.mensagens = []


# Barra lateral: histórico de conversas

st.sidebar.image("assets/catbot.png", width=250)
st.sidebar.title("Catbot")
st.sidebar.subheader("Suas conversas")

if st.sidebar.button("＋ Nova conversa", use_container_width=True):
    st.session_state.conversa_id = criar_conversa()
    st.session_state.mensagens = []
    st.rerun()



conversas = listar_conversas()

for conversa_id, titulo, data_criacao in conversas:
    selecionada = (
        st.session_state.conversa_id == conversa_id
    )

    texto_botao = f"📂 {titulo}"

    if selecionada:
        texto_botao = f"📖 {titulo} (aberta)"

    if st.sidebar.button(
        texto_botao,
        key=f"conversa_{conversa_id}",
        use_container_width=True
    ):
        st.session_state.conversa_id = conversa_id
        st.session_state.mensagens = buscar_mensagens(
            conversa_id
        )
        st.rerun()



# Criar a primeira conversa automaticamente
if st.session_state.conversa_id is None:
    st.session_state.conversa_id = criar_conversa()
    st.session_state.mensagens = []


# Área principal do chat
st.title("🐈‍⬛ Catbot")
st.caption("Seu companheiro de conversas noturnas.")

for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.write(mensagem["content"])


pergunta = st.chat_input("Converse com o Catbot...")

if pergunta:
    # Salvar a mensagem do usuário
    salvar_mensagem(
        st.session_state.conversa_id,
        "user",
        pergunta
    )
    if not st.session_state.mensagens:
        try:
            titulo = gerar_titulo(pergunta)
        except Exception:
            titulo = pergunta.strip()[:35]

        atualizar_titulo(
            st.session_state.conversa_id,
            titulo
        )

    st.session_state.mensagens.append({
        "role": "user",
        "content": pergunta
    })

    with st.chat_message("user"):
        st.write(pergunta)

    # Gerar resposta usando o histórico da conversa
    try:
        resposta = responder(st.session_state.mensagens)

        salvar_mensagem(
            st.session_state.conversa_id,
            "assistant",
            resposta
        )

        st.session_state.mensagens.append({
            "role": "assistant",
            "content": resposta
        })

        with st.chat_message("assistant"):
            st.write(resposta)

    except Exception as erro:
        st.error(
            "Não consegui gerar uma resposta. "
            "Verifique sua conexão e tente novamente."
        )
