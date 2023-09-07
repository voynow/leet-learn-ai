import base64
import json
import logging

import openai
import streamlit as st
from llm_blocks import block_factory, blocks

PAGE_TITLE = "LeetLearn.ai"
USER_ROLE = "user"
BOT_ROLE = "assistant"

SYS_MESSAGE = """Role: You are a LeetCode interview tutor, mirroring the challenging yet encouraging environment of elite tech firms like Google, Amazon, etc.
Be Concise: Stay focused and be concise. The user's time is extremely valuable and every word you respond with takes some of the user's time.
Never Reveal Answers: Be very vey conservative with hints, never reveal answers, be as vague as possible.
Important: When the user shares a problem, let them think through the problem before providing hints.
"""

API_KEY_ERR_MSG = (
    "ERROR. Invalid API key. Please refresh the page and enter a valid API key"
)

solutions = json.loads(open("data/solutions_cleaned.json").read())
logging.basicConfig(level=logging.INFO)


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
        st.session_state["block"] = block_factory.get(
            "chat", stream=True, system_message=SYS_MESSAGE, model_name="gpt-4"
        )
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_selection" not in st.session_state:
        st.session_state.current_selection = None
    if "clear_chat" not in st.session_state:
        st.session_state.clear_chat = False


def add_message(role, content):
    """
    Messages are duplicated in the session state and the block. Session state
    message are for displaying whereas block messages are for the AI
    """
    st.session_state["messages"].append({"role": role, "content": content})
    st.session_state["block"].message_handler.add_message(role, content)


def render_gif():
    file_ = open("data/leetlearnai_landing.gif", "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()

    st.markdown(
        f'<br><div style="text-align:center;"><img src="data:image/gif;base64,{data_url}" alt="cat gif" style="max-width:85%; height:auto; border:2px solid #ccc;"></div>',
        unsafe_allow_html=True,
    )


def display_landing_page():
    st.title("Welcome to LeetLearn.ai 🧪")
    st.markdown("#### Supercharging the LeetCode grind with a little bit of AI magic.")

    api_key = st.text_input(
        "Enter your OpenAI API key to get started:", type="password"
    )

    render_gif()

    if api_key:
        blocks.set_api_key(api_key)
        st.session_state["api_key"] = api_key
        add_message(BOT_ROLE, "Hello! I am LeetLearn AI. Lets get coding!")
        st.session_state.show_chat = True
        st.experimental_rerun()


def parse_stream(message_placeholder, response):
    """Parse and display chunks from response generate"""
    full_response = ""
    for chunk in response:
        full_response += chunk.choices[0].delta.get("content", "")
        message_placeholder.markdown(full_response + "▌")
    return full_response


def handle_response():
    """
    This streaming mechanism is critical to the application and has been
    developed specifically to align with streamlit
    """
    message_placeholder = st.empty()

    try:
        response = st.session_state["block"].completion_handler.create_completion(
            st.session_state["block"]
        )
        full_response = parse_stream(message_placeholder, response)
    except openai.error.AuthenticationError:
        full_response = API_KEY_ERR_MSG

    message_placeholder.markdown(full_response)
    return full_response


def handle_chat(query):
    add_message(USER_ROLE, query)
    with st.chat_message(USER_ROLE):
        st.markdown(query)
    with st.chat_message(BOT_ROLE):
        response = handle_response()
    add_message(BOT_ROLE, response)


def setup_sidebar():
    """Set up the sidebar with selectable options."""
    st.sidebar.title("Options Dropdown")
    options = [None] + solutions["name"]
    return st.sidebar.selectbox(
        label="Choose an option:", options=options, key="selection"
    )


def display_messages():
    """Display the chat messages."""
    logging.info(f"Displaying {len(st.session_state.messages)} messages")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def construct_chat_input(selected_option):
    i = 0
    for i in range(len(solutions["name"])):
        if solutions["name"][i] == selected_option:
            break
    selected_problem = solutions["problem"][i]
    return f"{selected_option}\n\n{selected_problem}"


def handle_new_selection(selected_option):
    """Clear chat and handle new sidebar selection."""
    logging.info("New selection made, clearing chat and rerunning.")
    st.session_state.messages = []
    st.session_state.current_selection = selected_option

    chat_input = construct_chat_input(selected_option)
    handle_chat(chat_input)
    st.experimental_rerun()


def display_chat_interface():
    """Main function to display the chat interface."""

    # Handle sidebar and check for new selections
    selected_option = setup_sidebar()
    selection_change = st.session_state.current_selection != selected_option

    if selection_change and selected_option is not None:
        handle_new_selection(selected_option)
        return

    # Display main interface
    st.title(PAGE_TITLE)
    display_messages()

    # Handle user input
    user_input = st.chat_input("Enter your query here")
    if user_input:
        handle_chat(user_input)


def show_page():
    if st.session_state.show_chat:
        display_chat_interface()
    else:
        display_landing_page()


if __name__ == "__main__":
    initialize_app()
    show_page()
