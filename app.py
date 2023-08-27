import streamlit as st
from llm_blocks import block_factory

PAGE_TITLE = "🧪🤖 Chat using LLM Blocks"
USER_ROLE = "user"
BOT_ROLE = "bot"

st.title(PAGE_TITLE)

if 'block' not in st.session_state:
    st.session_state['block'] = block_factory.get("chat")

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if prompt := st.chat_input("What is up?"):
    st.session_state['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        response = st.session_state['block'].execute(prompt)

        message_placeholder.markdown(response)
        st.session_state['messages'].append({"role": "assistant", "content": response})
