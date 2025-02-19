import json
import random
import chess
import chess.pgn
from deepseek import DeepSeekLLM  # Hypothetical integration

# Initialize DeepSeek-LLaMA-70B R1
deepseek_model = DeepSeekLLM(model="DeepSeek-LLaMA-70B-R1")

# Load Chess Puzzles from JSON
def load_puzzles(filename="chess_puzzles.json"):
    with open(filename, 'r') as file:
        puzzles = json.load(file)
    return puzzles

# Ask for difficulty and select puzzle
def get_user_difficulty():
    difficulties = ["easy", "medium", "hard"]
    while True:
        difficulty = input("Choose a difficulty (easy/medium/hard): ").lower()
        if difficulty in difficulties:
            return difficulty
        print("Invalid choice. Please enter easy, medium, or hard.")

def select_puzzle(puzzles, difficulty):
    return random.choice(puzzles[difficulty])

# Verify the user's move
def verify_move(user_move, correct_moves):
    return user_move in correct_moves

# Get the first move as a hint
def get_hint(pgn_str):
    game = chess.pgn.read_game(pgn_str)
    return game.mainline_moves()[0]  # First move

# Convert PGN to Plain English
def parse_pgn_to_english(pgn_str):
    game = chess.pgn.read_game(pgn_str)
    moves = list(game.mainline_moves())

    english_moves = []
    board = chess.Board()
    for move in moves:
        english_moves.append(board.san(move))
        board.push(move)

    return " → ".join(english_moves)

# Explain the solution using DeepSeek-LLaMA-70B R1
def explain_solution(pgn_str):
    solution_text = parse_pgn_to_english(pgn_str)
    prompt = f"Explain this chess solution in detail: {solution_text}"
    
    response = deepseek_model.generate(prompt)  # Call DeepSeek-LLaMA-70B R1
    return response

# Main function to handle the puzzle interaction
def chess_puzzle_solver():
    puzzles = load_puzzles()
    difficulty = get_user_difficulty()
    puzzle = select_puzzle(puzzles, difficulty)
    
    print(f"\nPuzzle (Difficulty: {difficulty.capitalize()}): {puzzle['position']}")
    
    user_move = input("Your move (e.g., e2e4): ")
    if verify_move(user_move, puzzle["solution"]):
        print("Correct! Well done.")
    else:
        print("Incorrect. Do you want a hint? (yes/no)")
        if input().lower() == "yes":
            hint = get_hint(puzzle["pgn"])
            print(f"Hint: Try {hint}")
        
        print("Still stuck? Want the full solution? (yes/no)")
        if input().lower() == "yes":
            solution = parse_pgn_to_english(puzzle["pgn"])
            print(f"Solution: {solution}")
            explanation = explain_solution(puzzle["pgn"])
            print(f"\nExplanation:\n{explanation}")

# Run the program
if __name__ == "__main__":
    chess_puzzle_solver()
