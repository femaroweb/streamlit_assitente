import streamlit as st
from openai import OpenAI
import traceback

st.set_page_config(page_title="Guia do Estudante", page_icon="🎓")
st.title("🎓 Guia do Estudante")
st.markdown("Converse com a sua assistente personalizada!")

# Configuração do OpenAI client usando Streamlit secrets
# Em vez de os.getenv, use st.secrets
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # ID da sua assistente criada no Playground
    ASSISTANT_ID = "asst_yaGBje1et0IslzPCZzdrhVX1"  # Substitua pelo seu ID real

    # Inicialização da sessão
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    if "thread_id" not in st.session_state:
        try:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id
        except Exception as e:
            st.error(f"Erro ao criar thread: {str(e)}")
            st.stop()

    # Exibir histórico de mensagens
    for role, msg in st.session_state.mensagens:
        with st.chat_message(role):
            st.markdown(msg)

    # Campo de entrada
    user_input = st.chat_input("Digite sua pergunta...")

    if user_input:
        # Mostrar a mensagem do usuário imediatamente
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Adicionar à lista de mensagens
        st.session_state.mensagens.append(("user", user_input))
        
        # Mostrar indicador de carregamento
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Pensando...")
            
            try:
                # Enviar a mensagem para a thread da assistente
                client.beta.threads.messages.create(
                    thread_id=st.session_state.thread_id,
                    role="user",
                    content=user_input,
                )

                # Criar e aguardar a execução
                run = client.beta.threads.runs.create_and_poll(
                    thread_id=st.session_state.thread_id,
                    assistant_id=ASSISTANT_ID,
                )

                if run.status == "completed":
                    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
                    resposta = messages.data[0].content[0].text.value
                else:
                    resposta = f"Status da execução: {run.status}. Algo deu errado ao tentar responder."
                
                # Atualizar o placeholder com a resposta
                message_placeholder.markdown(resposta)
                
                # Adicionar à lista de mensagens
                st.session_state.mensagens.append(("assistant", resposta))
                
            except Exception as e:
                error_message = f"Erro: {str(e)}\n\n```\n{traceback.format_exc()}\n```"
                message_placeholder.markdown(error_message)
                st.session_state.mensagens.append(("assistant", error_message))

except Exception as e:
    st.error(f"Erro na inicialização do aplicativo: {str(e)}")
    st.code(traceback.format_exc())