import json
import logging
import streamlit as st
from llm_blocks import block_factory, blocks

PAGE_TITLE = "LeetLearn.ai"
USER_ROLE = "user"
BOT_ROLE = "assistant"

SYS_MESSAGE = """
You are a LeetCode interview tutor, mirroring the challenging yet encouraging environment of elite tech firms like Google, Amazon, etc.
Be Concise: Stay focused and succinct to optimize learning speed.
Adapt and Flex: Handle both structured and unstructured questions, and tailor your approach to the learner's needs.
Encourage Reflection: Offer feedback that emphasizes growth and understanding.
Preserve Autonomy: Allow users to ponder solutions first. Be VERY conservative with hints to foster independent thinking.
Never Reveal Answers: Challenge and support, but don't take away the opportunity to learn.
"""

solutions = json.loads(open("data/solutions.json").read())
logging.basicConfig(level=logging.INFO)


def initialize_app():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="🧪",
        initial_sidebar_state="expanded",
    )
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False
    if "block" not in st.session_state:
        st.session_state["block"] = block_factory.get("chat", stream=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_selection" not in st.session_state:
        st.session_state.current_selection = None


def add_message(role, content):
    st.session_state["messages"].append({"role": role, "content": content})
    st.session_state["block"].message_handler.add_message(role, content)


def introduce_ai():
    intro_message = "Hello! I am LeetLearn AI. What are we working on today?"
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


def stream_response():
    """
    This streaming mechanism is critical to the application and has been
    developed specifically to align with streamlit
    """
    message_placeholder = st.empty()
    full_response = ""
    for response in st.session_state["block"].completion_handler.create_completion(
        st.session_state["block"]
    ):
        full_response += response.choices[0].delta.get("content", "")
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    return full_response


def setup_sidebar():
    st.sidebar.title("Options Dropdown")
    options = [None] + solutions["name"]
    selected_option = st.sidebar.selectbox(
        label="Choose an option:", options=options, key='selection'
    )
    return selected_option


def display_messages():
    logging.info(f"Displaying {len(st.session_state.messages)} messages")
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


def handle_selected_option(selected_option):
    st.session_state.current_selection = selected_option
    logging.info(f"Selected option: {selected_option}")
    handle_chat(selected_option)
    st.experimental_rerun()


def handle_user_input():
    user_input = st.chat_input("Enter your query here")
    if user_input:
        logging.info(f"User input: {user_input}")
        handle_chat(user_input)


def display_chat_interface():
    st.title(PAGE_TITLE)
    display_messages()
    selected_option = setup_sidebar()

    selection_change = st.session_state.current_selection != selected_option
    if selected_option is not None and selection_change:
        handle_selected_option(selected_option)
    else:
        handle_user_input()


def show_page():
    if st.session_state.show_chat:
        display_chat_interface()
    else:
        display_landing_page()


if __name__ == "__main__":
    initialize_app()
    show_page()
