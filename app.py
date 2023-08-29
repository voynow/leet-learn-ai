import streamlit as st
from llm_blocks import block_factory

# Constants and Config
PAGE_TITLE = "🧪 LeetLearn.ai"
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


def set_page_config():
    st.set_page_config(
        page_title="LeetLearn.ai",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://www.extremelycoolapp.com/help",
            "Report a bug": "https://www.extremelycoolapp.com/bug",
            "About": "# This is a header. This is an *extremely* cool app!",
        },
    )


def show_landing_page():
    st.title("Welcome to LeetLearn.ai")
    st.write(
        "Here, you can interact with our advanced AI to get insights, help, and much more."
    )
    if st.button("Proceed to Chat"):
        st.session_state.show_chat = True
        st.experimental_rerun()


def init_session_state():
    if "block" not in st.session_state:
        st.session_state["block"] = block_factory.get("chat", stream=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []
        add_message(
            BOT_ROLE,
            "Hi, I'm LeetLearn's AI assistant. What can I help you with today?",
        )


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


def render_chat():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def setup_sidebar():
    st.sidebar.title("Options Dropdown")
    selected_option = st.sidebar.selectbox("Choose an option:", OPTIONS)
    return selected_option


def main():
    set_page_config()
    init_session_state()

    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False

    if st.session_state.show_chat:
        st.title(PAGE_TITLE)
        selected_option = setup_sidebar()
        render_chat()

        if query := st.chat_input("Enter your query here"):
            add_message(USER_ROLE, query)
            with st.chat_message(USER_ROLE):
                st.markdown(query)
            with st.chat_message(BOT_ROLE):
                response = stream_response()
            add_message(BOT_ROLE, response)
    else:
        show_landing_page()


if __name__ == "__main__":
    main()
