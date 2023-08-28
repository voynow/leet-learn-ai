import streamlit as st
from llm_blocks import block_factory

PAGE_TITLE = "🧪🤖 Chat using LLM Blocks"
USER_ROLE = "user"
BOT_ROLE = "assistant"


def add_message(role, content):
    st.session_state['messages'].append({"role": role, "content": content})
    st.session_state['block'].message_handler.add_message(role, content)


def stream_response():
    message_placeholder = st.empty()
    full_response = ""
    for response in st.session_state['block'].completion_handler.create_completion(st.session_state['block']):
        full_response += response.choices[0].delta.get("content", "")
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    return full_response

st.title(PAGE_TITLE)

if 'block' not in st.session_state:
    st.session_state['block'] = block_factory.get("chat", stream=True)

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if query := st.chat_input("Enter your query here"):
    add_message(USER_ROLE, query)

    with st.chat_message(USER_ROLE):
        st.markdown(query)

    with st.chat_message(BOT_ROLE):
        response = stream_response()
    
    add_message(BOT_ROLE, response)