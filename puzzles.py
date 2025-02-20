import streamlit as st
import pandas as pd
import chess
import chess.svg
import base64
import os

# Load puzzles from CSV files
def load_puzzles(difficulty):
    file_map = {
        "Easy": "easy.csv",
        "Medium": "medium.csv",
        "Hard": "hard.csv"
    }
    return pd.read_csv(file_map[difficulty])

# Select a random puzzle
def get_random_puzzle(df):
    puzzle = df.sample().iloc[0]  # Select a random puzzle instead of always the first one
    moves_list = puzzle["Moves"].split()
    return puzzle["FEN"], moves_list, puzzle["Rating"]

# Function to render the board
def render_board(board):
    svg = chess.svg.board(board=board)
    encoded_svg = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{encoded_svg}" width="400"/>'

def main():
    # Streamlit UI
    st.title("♟️ Chess Puzzle Solver")
    st.sidebar.header("Select Difficulty")
    difficulty = st.sidebar.radio("Difficulty", ["Easy", "Medium", "Hard"], key="difficulty")

    # Update session state when difficulty changes
    if "selected_difficulty" not in st.session_state or st.session_state.selected_difficulty != difficulty:
        st.session_state.selected_difficulty = difficulty
        st.session_state.puzzle_data = load_puzzles(difficulty)
        st.session_state.fen, st.session_state.correct_moves, st.session_state.rating = get_random_puzzle(st.session_state.puzzle_data)
        st.session_state.board = chess.Board(st.session_state.fen)
        
        # Play the first move before displaying the board
        if st.session_state.correct_moves:
            st.session_state.board.push_uci(st.session_state.correct_moves.pop(0))

    # Display puzzle rating
    st.subheader(f"Puzzle Rating: {st.session_state.rating}")
    # Display board only once at the end to prevent multiple renderings
    st.markdown(render_board(st.session_state.board), unsafe_allow_html=True)
    st.write(f"FEN: {st.session_state.board.fen()}")
    # User move input
    uci_move = st.text_input("Enter your move in UCI format (e.g., e2e4):")
    # Validate move
    col1,col2, col3 = st.columns(3)
    with col1:
        if st.button("Submit Move"):
            if uci_move and uci_move in st.session_state.correct_moves:
                st.session_state.board.push_uci(uci_move)
                st.session_state.correct_moves.remove(uci_move)
                st.success("Correct move! The board has been updated.")
                
                # If an opponent's move exists, play it automatically
                if st.session_state.correct_moves:
                    st.session_state.board.push_uci(st.session_state.correct_moves.pop(0))
                else:
                    st.success("You solved the puzzle! 🎉")
            else:
                st.error("Incorrect move. Try again!")

    # Button to get a hint
    with col2:
        if st.button("Give Hint"):
            if st.session_state.correct_moves:
                st.info(f"Hint: {st.session_state.correct_moves[0]}")
            else:
                st.success("You can proceed to another puzzle.")

    # Button to load a new puzzle
    with col3:
        if st.button("Next Puzzle"):
            st.session_state.fen, st.session_state.correct_moves, st.session_state.rating = get_random_puzzle(st.session_state.puzzle_data)
            st.session_state.board = chess.Board(st.session_state.fen)
            
            # Play the first move before displaying the board
            if st.session_state.correct_moves:
                st.session_state.board.push_uci(st.session_state.correct_moves.pop(0))
            st.rerun()

if __name__ == "__main__":
    main()