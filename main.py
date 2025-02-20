import streamlit as st
st.set_page_config(layout="wide")  # Ensures a wide layout

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Chatbot", "Puzzles", "Play chess"])

# Import the correct page dynamically
if page == "Chatbot":
    import chatbot
    chatbot.main()
elif page == "Puzzles":
    import puzzles
    puzzles.main()
elif page == "Play chess":
    import play_chess
    play_chess.main()