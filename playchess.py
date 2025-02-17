import chess.engine
import os
from dotenv import load_dotenv
from stockfish import Stockfish
from groq import Groq
import re

load_dotenv()
STOCKFISH_PATH = os.environ.get("STOCKFISH_PATH")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


stockfish = Stockfish(STOCKFISH_PATH, depth=20, parameters={"Threads": 10, "Minimum Thinking Time": 50})


client = Groq(api_key=GROQ_API_KEY)


board = chess.Board()

def clean(response):
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    return response

def explain_move(move_uci, board_fen):

    prompt = f"Explain why the move {move_uci} is a good move in this position:\n{board_fen}"

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return clean(response.choices[0].message.content.strip())


def play():

    while not board.is_game_over():
        print(board)


        user_move = input("Enter your move in UCI (e.g., e2e4): ").lower()
        if user_move not in [move.uci() for move in board.legal_moves]:
            print("Invalid move. Try again.")
            continue

        board.push_uci(user_move)

        if board.is_game_over():
            print("Game over!")
            break


        stockfish.set_fen_position(board.fen())
        engine_move = stockfish.get_best_move()
        board.push_uci(engine_move)

        explanation = clean(explain_move(engine_move, board.fen()))

        print(f"\nI played: {engine_move}")
        print(f"Explanation: {explanation}\n")

    print("Final position:")
    print(board)
    print("Game over!")

def greet():
    chat_completion_1 = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a chess coach, user want to play against you , greet him and ask him about rating of opponent he would like to face",
            },
            {
                "role": "user",
                "content": f"",
            }
        ],
        model="deepseek-r1-distill-llama-70b",
    )
    print(clean(chat_completion_1.choices[0].message.content))
    rating_input = int(input())
    stockfish.set_elo_rating(rating_input)

if __name__ == "__main__":
    greet()
    play()
