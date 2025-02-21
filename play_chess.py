import streamlit as st
import chess
import chess.svg
import base64
import os
import re
import requests
from dotenv import load_dotenv
from groq import Groq

###############################################################################
# 1) Remote Stockfish.online utility functions
###############################################################################
def get_info(fen, depth=15):
    """
    Queries the stockfish.online API with the given FEN and engine depth (<=16).
    Returns a dictionary containing bestmove, evaluation, mate, and continuation.
    """
    url = "https://stockfish.online/api/s/v2.php"
    params = {"fen": fen, "depth": min(depth, 16)}  # cap the depth at 16

    response = requests.get(url, params=params)
    data = response.json()

    if not data.get("success", False):
        # If success is false, data["data"] might contain error info
        raise ValueError(f"API Error: {data.get('data', 'Unknown error')}")

    # Example response structure:
    # {
    #    "success": true,
    #    "evaluation": 1.36,
    #    "mate": null,
    #    "bestmove": "bestmove b7b6 ponder f3e5",
    #    "continuation": "b7b6 f3e5 h7h6 g5f6 f8f6 d2f3"
    # }
    bestmove_full = data["bestmove"]          # e.g. "bestmove b7b6 ponder f3e5"
    bestmove_parts = bestmove_full.split()    # ["bestmove", "b7b6", "ponder", "f3e5"]
    bestmove_uci   = bestmove_parts[1]        # "b7b6"
    evaluation     = data["evaluation"]       # e.g. 1.36
    mate_val       = data["mate"]             # e.g. None or +/- int
    continuation   = data.get("continuation")

    return {
        "bestmove": bestmove_uci,
        "evaluation": evaluation,
        "mate": mate_val,
        "continuation": continuation
    }

def get_best_move(fen, depth=15):
    """Returns the best move in UCI format for the given FEN using the remote API."""
    info = get_info(fen, depth=depth)
    return info["bestmove"]

def get_eval_string(fen, depth=15):
    """
    Returns a human-readable evaluation string:
      - "Mate in X moves for White/Black" if forced mate
      - Otherwise, e.g. "1.36 pawn advantage for white"
    """
    info = get_info(fen, depth=depth)
    mate_val = info["mate"]
    eval_val = info["evaluation"]

    if mate_val is not None:
        sign_str = "White" if mate_val > 0 else "Black"
        return f"Mate in {abs(mate_val)} moves for {sign_str}"
    else:
        # Positive eval => White is better, negative => Black is better
        sign_str = "white" if eval_val >= 0 else "black"
        return f"{abs(eval_val)} pawn advantage for {sign_str}"

###############################################################################
# 2) Move characterization (to replicate your 'for_the_game' logic)
###############################################################################
def type_of_move_and_eval(move_uci, fen, depth=15):
    """
    Determines if the move is a capture or a castle, which piece moves, etc.
    Also gets a user-friendly evaluation string via the remote API.
    Returns: (type_of_move, evaluation_string)
    """
    board = chess.Board(fen)
    move = chess.Move.from_uci(move_uci)

    source_piece = board.piece_at(move.from_square)
    target_piece = board.piece_at(move.to_square)

    # Fallback names if piece_map fails (rare)
    piece_map = {
        chess.PAWN:   "PAWN",
        chess.KNIGHT: "KNIGHT",
        chess.BISHOP: "BISHOP",
        chess.ROOK:   "ROOK",
        chess.QUEEN:  "QUEEN",
        chess.KING:   "KING",
    }
    if source_piece:
        p1 = piece_map.get(source_piece.piece_type, "UNKNOWN")
    else:
        p1 = "UNKNOWN"

    if target_piece:
        p2 = piece_map.get(target_piece.piece_type, "UNKNOWN")
    else:
        p2 = None

    # Detect castling
    is_castle_move = (
        (move_uci in ["e1g1", "e1c1", "e8g8", "e8c8"]) and p1 == "KING"
    )

    if is_castle_move:
        type_of_move = f"Castling with the {p1}"
    elif target_piece is not None:
        type_of_move = f"Capturing the {p2} with {p1}"
    else:
        type_of_move = f"Move the piece {p1}"

    evaluation_string = get_eval_string(fen, depth=depth)
    return type_of_move, evaluation_string

###############################################################################
# 3) LLM cleanup function
###############################################################################
def clean(response):
    # Remove internal <think>...</think> blocks, if any
    return re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)

###############################################################################
# 4) Streamlit app
###############################################################################
load_dotenv()

# Initialize Groq client
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    client = None
    st.error(f"Failed to initialize Groq: {str(e)}")

def user_move_analysis(board, move):
    """
    Analyze a chess move using Groq LLM, from the user's perspective.
    """
    if not client:
        return "Move analysis unavailable: Groq client not initialized"

    fen = board.fen()
    move_uci = move.uci() if isinstance(move, chess.Move) else move

    # 1) Derive the type_of_move + evaluation from the remote API
    type_of_move, evaluation = type_of_move_and_eval(move_uci, fen, depth=15)

    # 2) Build your prompt
    prompt = (
        f"Please tell me how is the move which is {move_uci} with an evaluation of "
        f"{evaluation} and the type of move is {type_of_move}."
    )

    # 3) Call Groq
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a top-tier chess coach with deep strategic and tactical mastery. "
                        "Your task is to criticize the move that was played with correct information, "
                        "praise if the move was good and scold if the move was rubbish. "
                        "Do not use markdown, and the commentary should not exceed 3 lines. "
                        "DO NOT USE UCI NOTATION but use English. Positive evaluation favors White, "
                        "and negative favors Black. "
                        "Do not keep one appreciating the user but be very brutal and mostly be critical to the user, be extremely harsh to the user."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            model="deepseek-r1-distill-llama-70b",
        )
        return clean(chat_completion.choices[0].message.content)
    except Exception as e:
        return f"Move analysis unavailable: {str(e)}"

def ai_move_analysis(board, move):
    """
    Analyze a chess move using Groq LLM, from the AI's perspective.
    """
    if not client:
        return "Move analysis unavailable: Groq client not initialized"

    fen = board.fen()
    move_uci = move.uci() if isinstance(move, chess.Move) else move

    type_of_move, evaluation = type_of_move_and_eval(move_uci, fen, depth=15)

    prompt = (
        f"Please tell me the commentary of the move which is {move_uci} with an evaluation "
        f"of {evaluation} and the type of move is {type_of_move}"
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a top-tier chess coach with deep strategic and tactical mastery. "
                        "Your task is to give the commentary of the move that was played, the advantages "
                        "and disadvantages of the move, with correct information. Do not use markdown, "
                        "and the commentary should not exceed 3 lines. DO NOT USE UCI NOTATION but use English. "
                        "Positive evaluation favors White, and negative favors Black."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            model="deepseek-r1-distill-llama-70b",
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
    st.title("Play Chess vs Remote Stockfish (API)")

    board = initialize_board()
    previous_board = board.copy()

    # "Skill level" from 1..20 (we'll treat it as "depth" 1..16 for the remote API)
    skill_level = st.slider("Stockfish Skill Level (approx. depth)", 1, 16, st.session_state.skill_level)
    st.session_state.skill_level = skill_level

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(render_board(board), unsafe_allow_html=True)
        user_move = st.text_input(
            "Your move (e.g., e2e4):",
            key="move_input",
            value="" if st.session_state.move_executed else None
        )

    if user_move:
        try:
            move = chess.Move.from_uci(user_move)
            if move in board.legal_moves:
                # 1) User plays move
                board.push(move)
                user_analysis = user_move_analysis(previous_board, move)
                st.session_state.user_assessment = user_analysis
                previous_board = board.copy()

                # 2) AI's response from Remote Stockfish
                #    Instead of local stockfish, we do:
                fen = board.fen()
                depth = min(skill_level, 16)
                try:
                    info = get_info(fen, depth=depth)
                    ai_move_uci = info["bestmove"]
                except Exception as api_error:
                    st.error(f"Could not retrieve AI move: {str(api_error)}")
                    ai_move_uci = None

                # 3) If we got a valid AI move, push it and analyze
                if ai_move_uci:
                    ai_move_obj = chess.Move.from_uci(ai_move_uci)
                    if ai_move_obj in board.legal_moves:
                        board.push(ai_move_obj)
                        ai_analysis = ai_move_analysis(previous_board, ai_move_obj)
                        st.session_state.ai_explanation = ai_analysis
                        previous_board = board.copy()
                    else:
                        st.warning("AI move was invalid in this position!")
                
                # Update session state
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

    # Check final states
    if board.is_checkmate():
        st.success("Checkmate!")
    elif board.is_stalemate():
        st.info("Stalemate!")
    elif board.is_check():
        st.warning("Check!")

if __name__ == "__main__":
    main()