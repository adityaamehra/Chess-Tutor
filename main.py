import streamlit as st
import zipfile

# Specify the path to the zip file
zip_file_path = "Puzzles data.zip"

# Extract the contents
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall()  # Change to your desired folder
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