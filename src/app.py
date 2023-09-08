import base64
import datetime
import json
import logging
import uuid

import openai
import streamlit as st
from llm_blocks import block_factory, blocks

import constants

with open(constants.DATA_PATH, encoding="utf-8") as f:
    solutions = json.load(f)

logging.basicConfig(level=logging.INFO)


def initialize_app():
    """Initialize the app and set up session state"""
    st.set_page_config(
        page_title=constants.PAGE_TITLE,
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False
    if "block" not in st.session_state:
        st.session_state.block = block_factory.get(
            "chat",
            stream=True,
            system_message=constants.SYS_MESSAGE,
            model_name="gpt-3.5-turbo-16k",
        )
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_selection" not in st.session_state:
        st.session_state.current_selection = None
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())


def log_message(**kwargs):
    print(json.dumps(kwargs, indent=4))


def add_message(role, content):
    """
    Messages are duplicated in the session state and the block. Session state
    message are for displaying whereas block messages are for the AI
    """
    st.session_state.messages.append({"role": role, "content": content})
    st.session_state.block.message_handler.add_message(role, content)
    log_message(
        session_id=st.session_state.session_id,
        conversation_id=st.session_state.conversation_id,
        message_id=str(uuid.uuid4()),
        problem_id=st.session_state.current_selection,
        timestamp=datetime.datetime.now().isoformat(),
        role=role,
        content=content,
    )


def render_gif():
    """Render the landing page gif"""
    file_ = open("data/leetlearnai_landing.gif", "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()

    st.markdown(
        f'<br><div style="text-align:center;"><img src="data:image/gif;base64,{data_url}" alt="demo gif" style="max-width:85%; height:auto; border:2px solid #ccc;"></div>',
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
        st.session_state.api_key = api_key
        add_message(constants.BOT_ROLE, "Hello! I am LeetLearn AI. Lets get coding!")
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
        response = st.session_state.block.completion_handler.create_completion(
            st.session_state.block
        )
        full_response = parse_stream(message_placeholder, response)
    except openai.error.AuthenticationError:
        full_response = constants.API_KEY_ERR_MSG

    message_placeholder.markdown(full_response)
    return full_response


def enrich_query(query):
    """Enrich query with HTML tags to improve readability"""
    replace_map = {
        "\n": "<br>",
        "    ": "&nbsp;&nbsp;&nbsp;&nbsp;",
        "  ": "&nbsp;&nbsp;",
    }
    for key, value in replace_map.items():
        query = query.replace(key, value)
    return query


def handle_chat(query):
    """Handle user input and bot response."""
    query = enrich_query(query)
    add_message(constants.USER_ROLE, query)
    with st.chat_message(constants.USER_ROLE):
        st.markdown(query, unsafe_allow_html=True)
    with st.chat_message(constants.BOT_ROLE):
        response = handle_response()
    add_message(constants.BOT_ROLE, response)


def setup_sidebar():
    """Set up the sidebar with selectable options."""
    st.sidebar.title("Options Dropdown")
    options = [None] + solutions["name"]
    return st.sidebar.selectbox(
        label="Choose an option:", options=options, key="selection"
    )


def display_messages():
    """Display the chat messages."""
    logging.info("Displaying %d messages", len(st.session_state.messages))
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)


def construct_chat_input(selected_option):
    """Select problem from solutions data given selected_option"""
    i = 0
    for i in range(len(solutions["name"])):
        if solutions["name"][i] == selected_option:
            break
    selected_problem = solutions["problem"][i]
    return f"{selected_option}\n\n{selected_problem}"


def clear_chat() -> None:
    st.session_state.messages = []
    st.session_state.block.message_handler.initialize_messages()


def handle_new_selection(selected_option):
    """Clear chat and handle new sidebar selection."""
    logging.info("New selection made, clearing chat and rerunning.")
    st.session_state.current_selection = selected_option
    st.session_state.conversation_id = str(uuid.uuid4())
    clear_chat()

    chat_input = construct_chat_input(selected_option)
    handle_chat(chat_input)
    st.experimental_rerun()


def display_chat_interface():
    """Main function to display the chat interface"""

    # Handle sidebar and check for new selections
    selected_option = setup_sidebar()
    selection_change = st.session_state.current_selection != selected_option

    if selection_change and selected_option is not None:
        handle_new_selection(selected_option)
        return

    # Display main interface
    st.title(constants.PAGE_TITLE)
    display_messages()

    # Handle user input
    user_input = st.chat_input("Enter your query here")
    if user_input:
        handle_chat(user_input)


def show_page():
    """Show the landing page or chat interface"""
    if st.session_state.show_chat:
        display_chat_interface()
    else:
        display_landing_page()


if __name__ == "__main__":
    initialize_app()
    show_page()
