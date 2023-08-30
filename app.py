import logging
import json
import streamlit as st

from llm_blocks import block_factory, blocks

logging.basicConfig(level=logging.INFO)

SYS_MESSAGE = """
Your system message here.
"""

# Singleton class to manage session state
class SessionState:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(SessionState, cls).__new__(cls)
            cls.instance.initialize_state()
        return cls.instance

    def initialize_state(self):
        initial_state = {
            "show_chat": False,
            "messages": [],
            "last_selected": None,
            "block": block_factory.get("chat", stream=True, system_message=SYS_MESSAGE),
        }
        for key, value in initial_state.items():
            if key not in st.session_state:
                if key not in ["messages", "block"]:
                    logging.info(f"Initializing state: {key}={value}")
                st.session_state[key] = value

# Model for handling messages and session state
class MessageModel:
    def __init__(self):
        self.state = SessionState()

    def add_message(self, role, content):
        logging.info(f"Adding message from {role}: {content[:50]}...")
        st.session_state.messages.append({"role": role, "content": content})
        st.session_state.block.message_handler.add_message(role, content)

# Controller to connect the Model and the View
class ChatController:
    def __init__(self):
        self.model = MessageModel()

    def handle_user_input(self, user_input, message_placeholder):
        self.model.add_message("user", user_input)
        response = self.stream_response(message_placeholder)
        self.model.add_message("assistant", response)

    def stream_response(self, message_placeholder):
        full_response = ""
        for response in st.session_state.block.completion_handler.create_completion(
            st.session_state.block
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        return full_response

def display_landing_page():
    logging.info("Displaying landing page...")
    st.title("Welcome to LeetLearn.ai 🧪")
    api_key = st.text_input("OpenAI API key:", type="password")
    if api_key:
        blocks.set_api_key(api_key)
        st.session_state.show_chat = True
        st.experimental_rerun()

def manage_messages():
    message_placeholders = []
    for _ in st.session_state.messages:
        message_placeholders.append(st.empty())
    for idx, message in enumerate(st.session_state.messages):
        with message_placeholders[idx].chat_message(message["role"]):
            message_placeholders[idx].markdown(message["content"])
    return message_placeholders

def solutions_interface(solutions, controller):
    options = ["Select an option..."] + solutions["name"]
    selected_option = st.sidebar.selectbox("Choose an option:", options)
    if selected_option != "Select an option..." and selected_option != st.session_state.last_selected:
        st.session_state.last_selected = selected_option
        assistant_message_placeholder = st.empty()
        with assistant_message_placeholder.chat_message("assistant"):
            assistant_message_placeholder.markdown("...")
        controller.handle_user_input(selected_option, assistant_message_placeholder)

def display_chat_interface(solutions, controller):
    logging.info("Displaying chat interface...")
    st.title("LeetLearn.ai")
    solutions_interface(solutions, controller)
    manage_messages()
    user_input = st.chat_input("Enter your query here")
    
    if user_input:
        assistant_message_placeholder = st.empty()
        with assistant_message_placeholder.chat_message("assistant"):
            assistant_message_placeholder.markdown("...")
        controller.handle_user_input(user_input, assistant_message_placeholder)

def run_app():
    session_state = SessionState()
    controller = ChatController()

    solutions = json.loads(open("data/solutions.json").read())

    if st.session_state.show_chat:
        display_chat_interface(solutions, controller)
    else:
        display_landing_page()

if __name__ == "__main__":
    run_app()
