from dotenv import load_dotenv
import os
import re
import pandas as pd
import numpy as np
from groq import Groq
from stockfish import Stockfish

STOCKFISH_PATH = None
LLAMA_MODEL_PATH = None
client = None
stockfish = None
d1 = d2 = d3 = d4 = d5 = None
def initialize():
    global STOCKFISH_PATH, LLAMA_MODEL_PATH, client, stockfish, d1, d2, d3, d4, d5
    if STOCKFISH_PATH is not None:
        return
    load_dotenv()  
    STOCKFISH_PATH = os.environ.get("STOCKFISH_PATH")
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    stockfish = Stockfish(STOCKFISH_PATH, depth=25, parameters={"Threads": 20, "Minimum Thinking Time": 10})
    d1 = pd.read_csv('theory/a.tsv', sep='\t', header=0)
    d2 = pd.read_csv('theory/b.tsv', sep='\t', header=0)
    d3 = pd.read_csv('theory/c.tsv', sep='\t', header=0)
    d4 = pd.read_csv('theory/d.tsv', sep='\t', header=0)
    d5 = pd.read_csv('theory/e.tsv', sep='\t', header=0)
initialize()
def clean(response):
    response=re.sub(r'<think>.*?</think>','',response,flags=re.DOTALL)
    return response
def get_best_move(fen):
    stockfish.set_fen_position(fen)
    return stockfish.get_best_move()
def ch_comp_bm_w_exp(fen,best_move,type_of_move,evaluation):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a top-tier chess coach with deep strategic and tactical mastery. Your task is to recommend the best move with absolute clarity, using proper chess notation and piece names. Justify the move with precise reasoning—covering positional, tactical, and strategic factors. Highlight threats, weaknesses, and long-term plans. Keep explanations concise, potent, and highly structured to maximize the user's chess understanding. Don't use the UCI notation but simple English notation.",
            },
            {
                "role": "user",
                "content": f"Justify why {type_of_move} {best_move} is the best move for the FEN {fen} with an evaluation of {evaluation}",
            }
        ],
        model="deepseek-r1-distill-llama-70b",
    )

    return clean(chat_completion.choices[0].message.content)
def ch_comp_th(eco,name,pgn):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"You are a chess coach , explain a theory behind the opening of the move with the name {name} ,ECO {eco} and the PGN {pgn} , please tell ALL THE pros and cons of the opening . All the variations and how to play against them.",
            },
            {
                "role": "user",
                "content": f"Explain the pros and cons and how to play against the best variations of the opening of the name {name} ,ECO {eco} and the PGN {pgn}",
            }
        ],
        model="deepseek-r1-distill-llama-70b",
    )

    return clean(chat_completion.choices[0].message.content)
def find(theory):
    for x in range(0,len(d1["name"])):
        if d1["name"][x].lower()==theory.lower():
            return d1['eco'][x],d1['name'][x],d1['pgn'][x]
    for x in range(0,len(d2["name"])):
        if d2["name"][x].lower()==theory.lower():
            return d2['eco'][x],d2['name'][x],d2['pgn'][x]
    for x in range(0,len(d3["name"])):
        if d3["name"][x].lower()==theory.lower():
            return d3['eco'][x],d3['name'][x],d3['pgn'][x]
    for x in range(0,len(d4["name"])):
        if d4["name"][x].lower()==theory.lower():
            return d4['eco'][x],d4['name'][x],d4['pgn'][x]
    for x in range(0,len(d5["name"])):
        if d5["name"][x].lower()==theory.lower():
            return d5['eco'][x],d5['name'][x],d5['pgn'][x]
def spell_check(text):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Check and correct spelling errors in the given text while keeping its original structure intact. Do not modify proper names, technical terms, or specialized jargon. If the input represents a chess opening, return it in the format 'opening <corrected opening spelling>' while ensuring that only spelling errors are corrected and chess terminology remains unchanged. Do not rephrase, restructure, or explain corrections. Return only the corrected text.",
            },
            {
                "role": "user",
                "content": text,
            }
        ],
        model="deepseek-r1-distill-llama-70b",
    )
    return clean(chat_completion.choices[0].message.content)
def get_eval(fen):
    stockfish.set_fen_position(fen)
    x=stockfish.get_evaluation()
    if x["type"]=="mate":
        return f"Mate in {x['value']}"
    else:
        return f"{int(x['value']) / 100.0} pawn advantage for {'white' if x['value'] > 0 else 'black'}"
def bm_w_exp(fen):
    best_move = get_best_move(fen)
    g = str(stockfish.will_move_be_a_capture(best_move)).split(".")[1]
    if g=="NO_CAPTURE":
        g=False
    else:
        g=True
    evaluation=get_eval(fen)
    p1_split = str(stockfish.get_what_is_on_square(best_move[:2])).split(".")
    p2_split = str(stockfish.get_what_is_on_square(best_move[2:])).split(".")
    p1 = p1_split[1] if len(p1_split) > 1 else p1_split[0]
    p2 = p2_split[1] if len(p2_split) > 1 else p2_split[0]
    if g:
        type_of_move = f"Capturing the {p2} with {p1}"
    elif "e8g8" in best_move and "KING" in p1:
        type_of_move = f"Castling with the {p1}"
    elif "e8b8" in best_move and "KING" in p1:
        type_of_move = f"Castling with the {p1}"
    elif "e1g1" in best_move and "KING" in p1:
        type_of_move = f"Castling with the {p1}"
    elif "e1b1" in best_move and "KING" in p1:
        type_of_move = f"Castling with the {p1}"
    else:
        type_of_move = f"Move the piece {p1}"
    return ch_comp_bm_w_exp(fen, best_move, type_of_move,evaluation)
def for_the_game(best_move,fen):
    stockfish.set_fen_position(fen)
    g = str(stockfish.will_move_be_a_capture(best_move)).split(".")[1]
    if g=="NO_CAPTURE":
        g=False
    else:
        g=True
    evaluation=get_eval(fen)
    p1_split = str(stockfish.get_what_is_on_square(best_move[:2])).split(".")
    p2_split = str(stockfish.get_what_is_on_square(best_move[2:])).split(".")
    p1 = p1_split[1] if len(p1_split) > 1 else p1_split[0]
    p2 = p2_split[1] if len(p2_split) > 1 else p2_split[0]
    if g:
        type_of_move = f"Capturing the {p2} with {p1}"
    elif "e8g8" in best_move and "KING" in p1:
        type_of_move = f"Castling with the {p1}"
    elif "e8b8" in best_move and "KING" in p1:
        type_of_move = f"Castling with the {p1}"
    elif "e1g1" in best_move and "KING" in p1:
        type_of_move = f"Castling with the {p1}"
    elif "e1b1" in best_move and "KING" in p1:
        type_of_move = f"Castling with the {p1}"
    else:
        type_of_move = f"Move the piece {p1}"
    return type_of_move,evaluation