import streamlit as st
import chess
import chess.engine
import chess.svg
from stockfish import Stockfish
import base64
import os
from dotenv import load_dotenv
from groq import Groq
import re

load_dotenv()

# Initialize Stockfish engine
STOCKFISH_PATH = os.environ.get("STOCKFISH_PATH")
stockfish = Stockfish(STOCKFISH_PATH)
stockfish.set_skill_level(5)  # Moderate difficulty

# Initialize Groq client
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    st.error(f"Failed to initialize Groq: {str(e)}")
    client = None

def clean(response):
    """Remove think tags from LLM response"""
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    return response

def move_analysis(board, move, is_user_move=True):
    """Analyze a chess move using Groq LLM"""
    if not client:
        return "Move analysis unavailable: Groq client not initialized"
    
    fen = board.fen()
    move_str = move.uci() if isinstance(move, chess.Move) else move
    
    prompt = f"""As a chess expert, provide commentary on this move: Board Position (FEN): {fen} 
                move: {move_str}
                Commentarty should not exceed 2 sentences. Dont include Word White and Black in response.
                """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": " Provide analysis of Chess move in 2-3 sentences.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-70b-8192",
            max_tokens=100,
            temperature=0.7
        )
        return clean(chat_completion.choices[0].message.content)
    except Exception as e:
        return f"Move analysis unavailable: {str(e)}"

def initialize_board():
    """Initialize or return existing chess board from session state"""
    if 'board' not in st.session_state:
        st.session_state.board = chess.Board()
    if 'move_history' not in st.session_state:
        st.session_state.move_history = []
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    return st.session_state.board

def render_board(board):
    """Display the chess board as an SVG image"""
    board_svg = chess.svg.board(board=board)
    b64 = base64.b64encode(board_svg.encode('utf-8')).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}" width="400"/>'

def main():
    st.title("Play Chess vs Stockfish")

    board = initialize_board()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(render_board(board), unsafe_allow_html=True)
        user_move = st.text_input("Your move (e.g., e2e4):", key="move_input")
    
    with col2:
        st.subheader("Current Move Analysis")
        if st.session_state.current_analysis:
            st.text(st.session_state.current_analysis)

    if st.button("Make Move"):
        try:
            # Validate and make user's move
            move = chess.Move.from_uci(user_move)
            if move in board.legal_moves:
                # Make user's move
                board.push(move)
                user_analysis = move_analysis(board, move, is_user_move=True)
                st.session_state.current_analysis = f"Move Analysis: {user_analysis}"

                # Get and make Stockfish's move
                stockfish.set_fen_position(board.fen())
                ai_move = stockfish.get_best_move()
                if ai_move:
                    ai_move_obj = chess.Move.from_uci(ai_move)
                    board.push(ai_move_obj)
                    ai_analysis = move_analysis(board, ai_move, is_user_move=False)
                    st.session_state.current_analysis = f"Move Analysis: {ai_analysis}"
                
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
