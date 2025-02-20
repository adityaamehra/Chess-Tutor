import streamlit as st
import pandas as pd
import chess
import chess.svg
import base64
import os
import time

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
    puzzle = df.sample().iloc[0]  # Select a random puzzle
    moves_list = puzzle["Moves"].split()
    return puzzle["FEN"], moves_list, puzzle["Rating"]

# Function to render the board
def render_board(board, perspective):
    svg = chess.svg.board(board=board, flipped=(perspective == chess.WHITE))  # Swapped perspective
    encoded_svg = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{encoded_svg}" width="400"/>'

def initialize_puzzle():
    """Initialize puzzle board independently."""
    if "puzzle_fen" not in st.session_state or "puzzle_moves" not in st.session_state or not st.session_state.puzzle_moves:
        st.session_state.puzzle_fen, st.session_state.puzzle_moves, st.session_state.puzzle_rating = get_random_puzzle(st.session_state.puzzle_data)
        st.session_state.puzzle_board = chess.Board(st.session_state.puzzle_fen)
        st.session_state.puzzle_to_move = "Black" if st.session_state.puzzle_board.turn == chess.WHITE else "White"
        if st.session_state.puzzle_moves:
            st.session_state.puzzle_board.push_uci(st.session_state.puzzle_moves.pop(0))

def main():
    # Streamlit UI
    st.title("♟️ Chess Puzzle Solver")
    st.sidebar.header("Select Difficulty")
    difficulty = st.sidebar.radio("Difficulty", ["Easy", "Medium", "Hard"], key="difficulty")
    
    if "selected_difficulty" not in st.session_state or st.session_state.selected_difficulty != difficulty:
        st.session_state.selected_difficulty = difficulty
        st.session_state.puzzle_data = load_puzzles(difficulty)
    
    initialize_puzzle()
    
    # Display puzzle rating and player to move
    st.subheader(f"Puzzle Rating: {st.session_state.puzzle_rating}")
    st.subheader(f"{st.session_state.puzzle_to_move} to Move")
    
    # Display puzzle board
    st.markdown(render_board(st.session_state.puzzle_board, chess.BLACK if st.session_state.puzzle_to_move == "White" else chess.WHITE), unsafe_allow_html=True)  # Swapped perspective
    st.write(f"FEN: {st.session_state.puzzle_board.fen()}")
    
    # User move input
    uci_move = st.text_input("Enter your move in UCI format (e.g., e2e4):")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Submit Move"):
            if uci_move and uci_move in st.session_state.puzzle_moves:
                st.session_state.puzzle_board.push_uci(uci_move)
                st.session_state.puzzle_moves.remove(uci_move)
                st.success("Correct move! The board has been updated.")
                
                if st.session_state.puzzle_moves:
                    st.session_state.puzzle_board.push_uci(st.session_state.puzzle_moves.pop(0))
                else:
                    st.success("You solved the puzzle! 🎉 Loading a new puzzle...")
                    time.sleep(2)
                    initialize_puzzle()
                st.rerun()
            else:
                st.error("Incorrect move. Try again!")
                time.sleep(1)
                st.rerun()
    
    with col2:
        if st.button("Give Hint"):
            if st.session_state.puzzle_moves:
                st.info(f"Hint: {st.session_state.puzzle_moves[0]}")
            else:
                st.success("You can proceed to another puzzle.")

    with col3:
        if st.button("Next Puzzle"):
            initialize_puzzle()
            st.rerun()

if __name__ == "__main__":
    main()
