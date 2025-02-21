import os
import re
import requests
import pandas as pd
import numpy as np
import chess  # Used to parse FEN and extract piece/move info
from dotenv import load_dotenv
from groq import Groq

# Global variables you previously used
STOCKFISH_PATH = None
LLAMA_MODEL_PATH = None
client = None
d1 = d2 = d3 = d4 = d5 = None

def initialize():
    global STOCKFISH_PATH, LLAMA_MODEL_PATH, client, d1, d2, d3, d4, d5
    if STOCKFISH_PATH is not None:
        return
    load_dotenv()  
    # Initialize your Groq client
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    # Load your theory data
    d1 = pd.read_csv('Theory/a.tsv', sep='\t', header=0)
    d2 = pd.read_csv('Theory/b.tsv', sep='\t', header=0)
    d3 = pd.read_csv('Theory/c.tsv', sep='\t', header=0)
    d4 = pd.read_csv('Theory/d.tsv', sep='\t', header=0)
    d5 = pd.read_csv('Theory/e.tsv', sep='\t', header=0)

initialize()

def clean(response):
    # Remove any internal <think> ... </think> blocks
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    return response

###############################################################################
# 1) Function to call the remote stockfish.online API
###############################################################################
def get_info(fen, depth=15):
    """
    Queries the stockfish.online API with the given FEN and engine depth (<=16).
    Returns a dictionary containing bestmove, evaluation, mate, and continuation.
    """
    url = "https://stockfish.online/api/s/v2.php"
    params = {
        "fen": fen,
        "depth": depth
    }

    response = requests.get(url, params=params)
    data = response.json()

    if not data.get("success", False):
        # If success is false, data["data"] might contain error info
        raise ValueError(f"API Error: {data.get('data', 'Unknown error')}")

    # Example response structure:
    # {
    #     "success": true,
    #     "evaluation": 1.36,
    #     "mate": null,
    #     "bestmove": "bestmove b7b6 ponder f3e5",
    #     "continuation": "b7b6 f3e5 h7h6 g5f6 f8f6 d2f3"
    # }

    bestmove_full = data["bestmove"]            # e.g. "bestmove b7b6 ponder f3e5"
    bestmove_parts = bestmove_full.split()      # ["bestmove", "b7b6", "ponder", "f3e5"]
    bestmove_uci   = bestmove_parts[1]          # "b7b6"
    evaluation     = data["evaluation"]         # e.g. 1.36
    mate_val       = data["mate"]               # e.g. None or a number (+ for White, - for Black)
    continuation   = data.get("continuation")   # e.g. "b7b6 f3e5 h7h6 ..."

    return {
        "bestmove": bestmove_uci,
        "evaluation": evaluation,
        "mate": mate_val,
        "continuation": continuation
    }

###############################################################################
# 2) Functions to get bestmove and evaluation from the remote API
###############################################################################
def get_best_move(fen):
    """
    Returns the best move in UCI format for the given FEN 
    (using the remote API instead of the local Stockfish).
    """
    info = get_info(fen)
    return info["bestmove"]

def get_eval(fen):
    """
    Returns a human-readable evaluation string:
      - "Mate in X moves" if there's a forced mate
      - Otherwise, e.g. "1.36 pawn advantage for white"
    """
    info = get_info(fen)
    mate_val = info["mate"]
    eval_val = info["evaluation"]

    if mate_val is not None:
        # Positive mate_val means White mates in X, negative means Black mates in X
        sign_str = "White" if mate_val > 0 else "Black"
        return f"Mate in {abs(mate_val)} moves for {sign_str}"
    else:
        sign_str = "white" if eval_val > 0 else "black"
        return f"{abs(eval_val)} pawn advantage for {sign_str}"

###############################################################################
# 3) LLM calls remain the same, except we remove references to local Stockfish
###############################################################################
def ch_comp_bm_w_exp(fen, best_move, type_of_move, evaluation):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a top-tier chess coach with deep strategic and "
                    "tactical mastery. Your task is to recommend the best move "
                    "with absolute clarity, using proper chess notation and piece names. "
                    "Justify the move with precise reasoning—covering positional, tactical, "
                    "and strategic factors. Highlight threats, weaknesses, and long-term plans. "
                    "Keep explanations concise, potent, and highly structured to maximize the "
                    "user's chess understanding. Don't use the UCI notation but simple English notation."
                ),
            },
            {
                "role": "user",
                "content": f"Justify why {type_of_move} {best_move} is the best move for the FEN {fen} with an evaluation of {evaluation}",
            }
        ],
        model="deepseek-r1-distill-llama-70b",
    )
    return clean(chat_completion.choices[0].message.content)

def ch_comp_th(eco, name, pgn):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a chess coach, explain the theory behind the opening of the "
                    f"move with the name {name}, ECO {eco}, and the PGN {pgn}. "
                    f"Please tell ALL THE pros and cons of the opening, all the variations, "
                    f"and how to play against them."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Explain the pros and cons and how to play against the best variations of "
                    f"the opening of the name {name}, ECO {eco}, and the PGN {pgn}."
                ),
            }
        ],
        model="deepseek-r1-distill-llama-70b",
    )
    return clean(chat_completion.choices[0].message.content)

###############################################################################
# 4) Utility to find openings in your data
###############################################################################
def find(theory):
    theory_lower = theory.lower()
    for x in range(len(d1["name"])):
        if d1["name"][x].lower() == theory_lower:
            return d1['eco'][x], d1['name'][x], d1['pgn'][x]
    for x in range(len(d2["name"])):
        if d2["name"][x].lower() == theory_lower:
            return d2['eco'][x], d2['name'][x], d2['pgn'][x]
    for x in range(len(d3["name"])):
        if d3["name"][x].lower() == theory_lower:
            return d3['eco'][x], d3['name'][x], d3['pgn'][x]
    for x in range(len(d4["name"])):
        if d4["name"][x].lower() == theory_lower:
            return d4['eco'][x], d4['name'][x], d4['pgn'][x]
    for x in range(len(d5["name"])):
        if d5["name"][x].lower() == theory_lower:
            return d5['eco'][x], d5['name'][x], d5['pgn'][x]

###############################################################################
# 5) Spell check function remains as-is (Groq usage)
###############################################################################
def spell_check(text):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "Check and correct spelling errors in the given text while keeping its original structure intact. "
                    "Do not modify proper names, technical terms, or specialized jargon. "
                    "If the input represents a chess opening, return it in the format 'opening <corrected opening spelling>' "
                    "while ensuring that only spelling errors are corrected and chess terminology remains unchanged. "
                    "Do not rephrase, restructure, or explain corrections. Return only the corrected text."
                ),
            },
            {
                "role": "user",
                "content": text,
            }
        ],
        model="deepseek-r1-distill-llama-70b",
    )
    return clean(chat_completion.choices[0].message.content)

###############################################################################
# 6) Build the final "best-move-with-explanation" function using the remote API
###############################################################################
def bm_w_exp(fen):
    """
    This function calls the remote API to get the best move,
    then uses python-chess to figure out if it's a capture, a castle, etc.
    Finally calls the LLM for an explanation.
    """
    # 6a) Query the API for bestmove & evaluation data
    info = get_info(fen)  # bestmove, evaluation, mate
    best_move = info["bestmove"]

    # 6b) Parse the board position using python-chess
    board = chess.Board(fen)
    move_obj = chess.Move.from_uci(best_move)
    source_square = move_obj.from_square
    target_square = move_obj.to_square

    source_piece = board.piece_at(source_square)
    target_piece = board.piece_at(target_square)

    # 6c) Convert piece types to the same naming style you used before
    piece_map = {
        chess.PAWN:   "PAWN",
        chess.KNIGHT: "KNIGHT",
        chess.BISHOP: "BISHOP",
        chess.ROOK:   "ROOK",
        chess.QUEEN:  "QUEEN",
        chess.KING:   "KING",
    }
    p1 = piece_map.get(source_piece.piece_type, "UNKNOWN") if source_piece else "UNKNOWN"
    p2 = piece_map.get(target_piece.piece_type, "UNKNOWN") if target_piece else None

    # 6d) Determine if it's a capture
    is_capture = (target_piece is not None)

    # 6e) Detect castling specifically by the UCI move
    #     (For example: White short castle: e1g1, White long castle: e1c1, etc.)
    if best_move in ["e8g8", "e8c8", "e1g1", "e1c1"] and p1 == "KING":
        type_of_move = f"Castling with the {p1}"
    elif is_capture:
        type_of_move = f"Capturing the {p2} with {p1}"
    else:
        type_of_move = f"Move the piece {p1}"

    # 6f) Get a readable evaluation string
    evaluation = get_eval(fen)

    # 6g) Now call your LLM-based explanation function
    return ch_comp_bm_w_exp(fen, best_move, type_of_move, evaluation)

###############################################################################
# 7) Helper function if you only want the "type_of_move" and "evaluation"
###############################################################################
def for_the_game(best_move, fen):
    """
    This helper function extracts type_of_move and evaluation without
    making a new API call (if you already have 'best_move').
    If you want it to query from scratch, you can re-use get_info instead.
    """
    board = chess.Board(fen)
    move_obj = chess.Move.from_uci(best_move)

    source_square = move_obj.from_square
    target_square = move_obj.to_square
    source_piece = board.piece_at(source_square)
    target_piece = board.piece_at(target_square)

    piece_map = {
        chess.PAWN:   "PAWN",
        chess.KNIGHT: "KNIGHT",
        chess.BISHOP: "BISHOP",
        chess.ROOK:   "ROOK",
        chess.QUEEN:  "QUEEN",
        chess.KING:   "KING",
    }
    p1 = piece_map.get(source_piece.piece_type, "UNKNOWN") if source_piece else "UNKNOWN"
    p2 = piece_map.get(target_piece.piece_type, "UNKNOWN") if target_piece else None
    is_capture = (target_piece is not None)

    if best_move in ["e8g8", "e8c8", "e1g1", "e1c1"] and p1 == "KING":
        type_of_move = f"Castling with the {p1}"
    elif is_capture:
        type_of_move = f"Capturing the {p2} with {p1}"
    else:
        type_of_move = f"Move the piece {p1}"

    evaluation = get_eval(fen)
    return type_of_move, evaluation