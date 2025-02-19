import streamlit as st
import chess
import chess.engine
import chess.svg
from stockfish import Stockfish
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Stockfish engine
STOCKFISH_PATH = os.environ.get("STOCKFISH_PATH")
stockfish = Stockfish(STOCKFISH_PATH)
stockfish.set_skill_level(5)  # Moderate difficulty

def initialize_board():
    if 'board' not in st.session_state:
        st.session_state.board = chess.Board()
    return st.session_state.board

def render_board(board):
    """Display the chess board as an SVG image"""
    board_svg = chess.svg.board(board=board)
    b64 = base64.b64encode(board_svg.encode('utf-8')).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}" width="400"/>'

def main():
    st.title("Play Chess vs Stockfish")
    
    # Initialize or get the board from session state
    board = initialize_board()
    
    # Show the current board state
    st.markdown(render_board(board), unsafe_allow_html=True)

    # Get user's move
    user_move = st.text_input("Your move (e.g., e2e4):")

    if st.button("Make Move"):
        try:
            # Validate and make user's move
            move = chess.Move.from_uci(user_move)
            if move in board.legal_moves:
                board.push(move)
                stockfish.set_fen_position(board.fen())

                # Get and make Stockfish's move
                ai_move = stockfish.get_best_move()
                if ai_move:
                    board.push(chess.Move.from_uci(ai_move))
                
                # Update session state
                st.session_state.board = board
                st.rerun()
            else:
                st.warning("Invalid move. Please try again!")
        except ValueError:
            st.error("Invalid move format. Please use format like 'e2e4'.")

    # Display game status
    if board.is_checkmate():
        st.success("Checkmate!")
    elif board.is_stalemate():
        st.info("Stalemate!")
    elif board.is_check():
        st.warning("Check!")

if __name__ == "__main__":
    main()
