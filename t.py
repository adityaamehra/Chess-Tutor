import streamlit as st
from streamlit_chat import message
import functions

# Initialize session state
st.session_state.setdefault("past", [])
st.session_state.setdefault("generated", [])

# Define better avatars
USER_AVATAR = "./assets/person.png"  # More professional and human-like

def handle_chess_query(user_input):
    """Processes user input and determines response using spell-checked version."""
    usi = functions.spell_check(user_input).strip()
    response = None

    # Check if input is a FEN string (likely requesting a move)
    if usi.lower().startswith("fen "):
        response = functions.bm_w_exp(usi[4:].strip())

    # Check if user is asking about a chess opening
    elif usi.lower().startswith("opening "):
        opening_name = usi[8:].strip()
        try:
            eco, name, pgn = functions.find(opening_name)
            response = functions.ch_comp_th(eco, name, pgn)
        except TypeError:
            response = "Sorry, I couldn't find that opening in my database."

    # Default response
    else:
        response = ("I'm here to assist with chess strategy, best moves, and opening theories! "
                    "Try entering:\n- **`FEN <position>`** to analyze a position\n"
                    "- **`Opening <name>`** to learn about an opening.")

    return response

def on_input_change():
    """Handles user input and generates responses."""
    user_input = st.session_state.user_input.strip()
    if not user_input:
        return

    # Store user query
    st.session_state.past.append(user_input)

    # Generate bot response
    bot_response = handle_chess_query(user_input)
    st.session_state.generated.append(bot_response)

    # Clear input field
    st.session_state.user_input = ""

def on_btn_click():
    """Clears chat history."""
    st.session_state.past.clear()
    st.session_state.generated.clear()

# Streamlit UI
st.title("♟️ The Chess Tutor - AI Chatbot")

chat_placeholder = st.empty()

with chat_placeholder.container():
    for i in range(len(st.session_state["generated"])):
        message(st.session_state["past"][i], is_user=True, key=f"{i}_user", avatar_style=USER_AVATAR)
        message(st.session_state["generated"][i], key=f"{i}_bot")

st.text_input("Ask me about Chess:", on_change=on_input_change, key="user_input")
st.button("Clear Chat", on_click=on_btn_click)