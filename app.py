import logging
import json
import streamlit as st

from llm_blocks import block_factory, blocks

SYS_MESSAGE = """
You are a LeetCode interview tutor, mirroring the challenging yet encouraging environment of elite tech firms like Google, Amazon, etc.
Be Concise: Stay focused and succinct to optimize learning speed.
Adapt and Flex: Handle both structured and unstructured questions, and tailor your approach to the learner's needs.
Encourage Reflection: Offer feedback that emphasizes growth and understanding.
Preserve Autonomy: Allow users to ponder solutions first. Be VERY conservative with hints to foster independent thinking.
Never Reveal Answers: Challenge and support, but don't take away the opportunity to learn.
"""

logging.basicConfig(level=logging.INFO)


def initialize_state():
    initial_state = {
        "show_chat": False,
        "messages": [],
        "last_selected": None,
        "block": block_factory.get("chat", stream=True, system_message=SYS_MESSAGE),
    }
    for key, value in initial_state.items():
        if key not in st.session_state:
            logging.info(f"Initializing state: {key}={value}")
            st.session_state[key] = value

def add_message(role, content):
    """Add a message to the state"""
    logging.info(f"Adding message from {role}: {content[:50]}...")
    st.session_state.messages.append({"role": role, "content": content})
    st.session_state.block.message_handler.add_message(role, content)


def display_landing_page():
    """Display the landing page"""
    logging.info("Displaying landing page...")
    st.title("Welcome to LeetLearn.ai 🧪")
    api_key = st.text_input("OpenAI API key:", type="password")
    if api_key:
        blocks.set_api_key(api_key)
        add_message("assistant", "Hello! I'm your LeetLearn AI.")
        st.session_state.show_chat = True
        st.experimental_rerun()


def solutions_interface(solutions):
    """Manage the solutions dropdown"""
    logging.info("Displaying solutions interface...")
    options = ["Select an option..."] + solutions["name"]
    selected_option = st.sidebar.selectbox("Choose an option:", options)
    if (
        selected_option != "Select an option..."
        and selected_option != st.session_state.last_selected
    ):
        st.session_state.last_selected = selected_option
        handle_chat(selected_option)


def display_messages():
    """Display chat messages"""
    for message in st.session_state.messages:
        logging.info(f"Displaying message from {message['role']}: {message['content'][:50]}...")
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def stream_response():
    """Stream chat response from AI"""
    full_response = ""
    for response in st.session_state.block.completion_handler.create_completion(
        st.session_state.block
    ):
        full_response += response.choices[0].delta.get("content", "")
    return full_response


def handle_chat(query):
    """Handle a chat interaction"""
    add_message("user", query)
    response = stream_response()
    add_message("assistant", response)

def display_chat_interface(solutions):
    """Display the main chat interface"""
    logging.info("Displaying chat interface...")
    st.title("LeetLearn.ai")
    solutions_interface(solutions)
    user_input = st.chat_input("Enter your query here")
    
    if user_input:
        handle_chat(user_input)
        
    display_messages()


def run_app():
    """Main function to run the app"""
    initialize_state()
    solutions = json.loads(open("data/solutions.json").read())

    if st.session_state.show_chat:
        display_chat_interface(solutions)
    else:
        display_landing_page()


if __name__ == "__main__":
    run_app()
