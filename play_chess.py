# import streamlit as st
# import chess
# import chess.engine
# import chess.svg
# from stockfish import Stockfish
# import base64
# import os
# from dotenv import load_dotenv
# from groq import Groq
# import re
# import functions

# load_dotenv()

# # Initialize Stockfish engine
# STOCKFISH_PATH = os.environ.get("STOCKFISH_PATH")
# stockfish = Stockfish(STOCKFISH_PATH)

# # Initialize Groq client
# try:
#     client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
# except Exception as e:
#     st.error(f"Failed to initialize Groq: {str(e)}")
#     client = None

# def move_analysis(board, move, is_user_move=True):
#     """Analyze a chess move using Groq LLM"""
#     if not client:
#         return "Move analysis unavailable: Groq client not initialized"
    
#     fen = board.fen()
#     move_str = move.uci() if isinstance(move, chess.Move) else move
#     type_of_move,evaluation = functions.for_the_game(move_str, fen)
#     prompt = f"Please tell me the commentary of the move which is {move_str} with an evaluation of {evaluation} and the type of move is {type_of_move}"
    
#     try:
#         chat_completion = client.chat.completions.create(
#             messages=[
#                 {"role": "system", "content": "You are a top-tier chess coach with deep strategic and tactical mastery. Your task is to give the commentry of the move that was played the advantages and the disadvantages of the move , which has the correct information , do not use markdown and the commetarty does not exceed 3 lines.DO NOT USE UCI NOTATION but use english, positive evaluation is in favor of white and negative is in favor of black."},
#                 {"role": "user", "content": prompt},
#             ],
#             model="deepseek-r1-distill-llama-70b",
#         )
#         return functions.clean(chat_completion.choices[0].message.content)
#     except Exception as e:
#         return f"Move analysis unavailable: {str(e)}"


# def initialize_board():
#     """Initialize or return existing chess board from session state"""
#     if 'board' not in st.session_state:
#         st.session_state.board = chess.Board()
#     if 'move_history' not in st.session_state:
#         st.session_state.move_history = []
#     if 'current_analysis' not in st.session_state:
#         st.session_state.current_analysis = None
#     if 'skill_level' not in st.session_state:
#         st.session_state.skill_level = 5
#     if 'move_executed' not in st.session_state:
#         st.session_state.move_executed = False
#     return st.session_state.board


# def render_board(board):
#     """Display the chess board as an SVG image"""
#     board_svg = chess.svg.board(board=board)
#     b64 = base64.b64encode(board_svg.encode('utf-8')).decode("utf-8")
#     return f'<img src="data:image/svg+xml;base64,{b64}" width="400"/>'


# def main():
#     st.title("Play Chess vs Stockfish")
#     board = initialize_board()
#     previous_board = board.copy()
#     # Add a slider for skill level selection
#     skill_level = st.slider("Stockfish Skill Level", 1, 20, st.session_state.skill_level)
#     st.session_state.skill_level = skill_level
#     stockfish.set_skill_level(skill_level)
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         st.markdown(render_board(board), unsafe_allow_html=True)
#         user_move = st.text_input("Your move (e.g., e2e4):", key="move_input", value="" if st.session_state.move_executed else None)
    
#     with col2:
#         st.subheader("Current Move Analysis")
#         if st.session_state.current_analysis:
#             st.text(st.session_state.current_analysis)
    
#     if user_move:
#         try:
#             move = chess.Move.from_uci(user_move)
#             if move in board.legal_moves:
#                 board.push(move)
#                 user_analysis = move_analysis(previous_board, move, is_user_move=True)
#                 previous_board = board.copy()
#                 st.session_state.current_analysis = f"Move Analysis: {user_analysis}"
                
#                 # Get and make Stockfish's move
#                 stockfish.set_fen_position(board.fen())
#                 ai_move = stockfish.get_best_move()
#                 if ai_move:
#                     ai_move_obj = chess.Move.from_uci(ai_move)
#                     board.push(ai_move_obj)
#                     ai_analysis = move_analysis(previous_board, ai_move, is_user_move=False)
#                     previous_board = board.copy()
#                     st.session_state.current_analysis = f"Move Analysis: {ai_analysis}"
#                 # Update session state
#                 st.session_state.board = board
#                 st.session_state.move_executed = True
#                 st.rerun()
#             else:
#                 st.warning("Invalid move. Please try again!")
#         except ValueError:
#             st.error("Invalid move format. Please use format like 'e2e4'.")
    
#     # Reset move_executed to allow new input
#     st.session_state.move_executed = False
    
#     # Display game status
#     if board.is_checkmate():
#         st.success("Checkmate!")
#     elif board.is_stalemate():
#         st.info("Stalemate!")
#     elif board.is_check():
#         st.warning("Check!")

# if __name__ == "__main__":
#     main()




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
import functions

load_dotenv()

# Initialize Stockfish engine
STOCKFISH_PATH = os.environ.get("STOCKFISH_PATH")
stockfish = Stockfish(STOCKFISH_PATH)

# Initialize Groq client
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    st.error(f"Failed to initialize Groq: {str(e)}")
    client = None

def user_move_analysis(board, move, is_user_move=True):
    """Analyze a chess move using Groq LLM"""
    if not client:
        return "Move analysis unavailable: Groq client not initialized"
    
    fen = board.fen()
    move_str = move.uci() if isinstance(move, chess.Move) else move
    type_of_move, evaluation = functions.for_the_game(move_str, fen)
    prompt = f"Please tell me how is the move which is {move_str} with an evaluation of {evaluation} and the type of move is {type_of_move}."
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a top-tier chess coach with deep strategic and tactical mastery. Your task is to critize the move that was played with correct information , praise if the move was good and scold if the move was rubbish. Do not use markdown, and the commentary should not exceed 3 lines. DO NOT USE UCI NOTATION but use English. Positive evaluation favors White, and negative favors Black."},
                {"role": "user", "content": prompt},
            ],
            model="deepseek-r1-distill-llama-70b",
        )
        return functions.clean(chat_completion.choices[0].message.content)
    except Exception as e:
        return f"Move analysis unavailable: {str(e)}"

def ai_move_analysis(board, move, is_user_move=True):
    """Analyze a chess move using Groq LLM"""
    if not client:
        return "Move analysis unavailable: Groq client not initialized"
    
    fen = board.fen()
    move_str = move.uci() if isinstance(move, chess.Move) else move
    type_of_move, evaluation = functions.for_the_game(move_str, fen)
    prompt = f"Please tell me the commentary of the move which is {move_str} with an evaluation of {evaluation} and the type of move is {type_of_move}"
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a top-tier chess coach with deep strategic and tactical mastery. Your task is to give the commentary of the move that was played, the advantages and disadvantages of the move, with correct information. Do not use markdown, and the commentary should not exceed 3 lines. DO NOT USE UCI NOTATION but use English. Positive evaluation favors White, and negative favors Black."},
                {"role": "user", "content": prompt},
            ],
            model="deepseek-r1-distill-llama-70b",
        )
        return functions.clean(chat_completion.choices[0].message.content)
    except Exception as e:
        return f"Move analysis unavailable: {str(e)}"

def initialize_board():
    """Initialize or return existing chess board from session state"""
    if 'board' not in st.session_state:
        st.session_state.board = chess.Board()
    if 'move_history' not in st.session_state:
        st.session_state.move_history = []
    if 'ai_explanation' not in st.session_state:
        st.session_state.ai_explanation = None
    if 'user_assessment' not in st.session_state:
        st.session_state.user_assessment = None
    if 'skill_level' not in st.session_state:
        st.session_state.skill_level = 5
    if 'move_executed' not in st.session_state:
        st.session_state.move_executed = False
    return st.session_state.board

def render_board(board):
    """Display the chess board as an SVG image"""
    board_svg = chess.svg.board(board=board)
    b64 = base64.b64encode(board_svg.encode('utf-8')).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}" width="400"/>'

def main():
    st.title("Play Chess vs Stockfish")
    board = initialize_board()
    previous_board = board.copy()
    
    skill_level = st.slider("Stockfish Skill Level", 1, 20, st.session_state.skill_level)
    st.session_state.skill_level = skill_level
    stockfish.set_skill_level(skill_level)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(render_board(board), unsafe_allow_html=True)
        user_move = st.text_input("Your move (e.g., e2e4):", key="move_input", value="" if st.session_state.move_executed else None)
    
    if user_move:
        try:
            move = chess.Move.from_uci(user_move)
            if move in board.legal_moves:
                board.push(move)
                user_analysis = user_move_analysis(previous_board, move, is_user_move=True)
                previous_board = board.copy()
                st.session_state.user_assessment = f"{user_analysis}"
                
                stockfish.set_fen_position(board.fen())
                ai_move = stockfish.get_best_move()
                if ai_move:
                    ai_move_obj = chess.Move.from_uci(ai_move)
                    board.push(ai_move_obj)
                    ai_analysis = ai_move_analysis(previous_board, ai_move, is_user_move=False)
                    previous_board = board.copy()
                    st.session_state.ai_explanation = f"{ai_analysis}"
                
                st.session_state.board = board
                st.session_state.move_executed = True
                st.rerun()
            else:
                st.warning("Invalid move. Please try again!")
        except ValueError:
            st.error("Invalid move format. Please use format like 'e2e4'.")
    
    st.session_state.move_executed = False
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("AI Move Explanation")
        if st.session_state.ai_explanation:
            st.text(st.session_state.ai_explanation)
    
    with col4:
        st.subheader("User Move Assessment")
        if st.session_state.user_assessment:
            st.text(st.session_state.user_assessment)
    
    if board.is_checkmate():
        st.success("Checkmate!")
    elif board.is_stalemate():
        st.info("Stalemate!")
    elif board.is_check():
        st.warning("Check!")

if __name__ == "__main__":
    main()