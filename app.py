import streamlit as st
from llm_blocks import block_factory, blocks

# Constants and Config
PAGE_TITLE = "LeetLearn.ai"
USER_ROLE = "user"
BOT_ROLE = "assistant"
OPTIONS = [
    "Option A",
    "Option B",
    "Option C",
    "Option D",
    "Option E",
    "Option F",
    "Option G",
]


def initialize_app():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False
    if "block" not in st.session_state:
        st.session_state["block"] = block_factory.get("chat", stream=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []


def show_page():
    if st.session_state.show_chat:
        display_chat_interface()
    else:
        display_landing_page()


def introduce_ai():
    intro_message = (
        "Hello! I am LeetLearn AI. What are we working on today?"
    )
    add_message(BOT_ROLE, intro_message)


def display_landing_page():
    st.title("Welcome to LeetLearn.ai 🧪")
    st.write("Interact with our advanced AI for insights, help, and more.")
    api_key = st.text_input("OpenAI API key:", type="password")
    if api_key:
        blocks.set_api_key(api_key)
        st.session_state["api_key"] = api_key
        introduce_ai()
        st.session_state.show_chat = True
        st.experimental_rerun()


def display_chat_interface():
    st.title(PAGE_TITLE)
    setup_sidebar()
    display_messages()
    user_input = st.chat_input("Enter your query here")
    if user_input:
        handle_chat(user_input)


def setup_sidebar():
    st.sidebar.title("Options Dropdown")
    selected_option = st.sidebar.selectbox("Choose an option:", OPTIONS)
    return selected_option


def display_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_chat(query):
    add_message(USER_ROLE, query)
    with st.chat_message(USER_ROLE):
        st.markdown(query)
    with st.chat_message(BOT_ROLE):
        response = stream_response()
    add_message(BOT_ROLE, response)


def add_message(role, content):
    st.session_state["messages"].append({"role": role, "content": content})
    st.session_state["block"].message_handler.add_message(role, content)


def stream_response():
    message_placeholder = st.empty()
    full_response = ""
    for response in st.session_state["block"].completion_handler.create_completion(
        st.session_state["block"]
    ):
        full_response += response.choices[0].delta.get("content", "")
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    return full_response


if __name__ == "__main__":
    initialize_app()
    show_page()
